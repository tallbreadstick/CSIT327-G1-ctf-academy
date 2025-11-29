from __future__ import annotations

import logging
import signal
import time
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class RequestTimedOut(Exception):
    """Raised when a request exceeds the configured timeout."""


class RequestTimeoutMiddleware:
    """Ensures long-running requests terminate with a friendly 504 response.

    On Unix platforms we rely on SIGALRM to interrupt the request processing.
    On platforms without SIGALRM (e.g. Windows) we fallback to measuring the
    elapsed time and returning a timeout response if the threshold is exceeded.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.timeout_seconds = getattr(settings, "REQUEST_TIMEOUT_SECONDS", 15)
        self.supports_alarm = hasattr(signal, "SIGALRM")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self.timeout_seconds <= 0:
            return self.get_response(request)

        start = time.monotonic()
        if self.supports_alarm:
            response = self._run_with_alarm(request)
        else:
            response = self._run_with_timer(request)

        return response

    def _timeout_response(self, request: HttpRequest) -> HttpResponse:
        message = "Request timed out — please try again."
        accepts_json = (
            request.headers.get("accept", "").lower().find("json") != -1
            or request.headers.get("x-requested-with") == "XMLHttpRequest"
        )
        if accepts_json:
            payload = {"detail": message}
            return JsonResponse(payload, status=504)
        return HttpResponse(message, status=504)

    def _run_with_alarm(self, request: HttpRequest) -> HttpResponse:
        def _handler(signum, frame):  # pragma: no cover - signal handler
            raise RequestTimedOut()

        old_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler)
        signal.setitimer(signal.ITIMER_REAL, self.timeout_seconds)
        try:
            response = self.get_response(request)
        except RequestTimedOut:
            logger.warning("Request exceeded %s seconds (SIGALRM)", self.timeout_seconds)
            return self._timeout_response(request)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)
        return response

    def _run_with_timer(self, request: HttpRequest) -> HttpResponse:
        start = time.monotonic()
        response = self.get_response(request)
        elapsed = time.monotonic() - start
        if elapsed > self.timeout_seconds:
            logger.warning("Request exceeded %s seconds (fallback timer)", self.timeout_seconds)
            return self._timeout_response(request)
        return response
