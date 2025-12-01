from __future__ import annotations

import logging
import time
from typing import Callable
import concurrent.futures

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class RequestTimedOut(Exception):
    """Raised when a request exceeds the configured timeout."""


class RequestTimeoutMiddleware:
    """
    Ensures long-running requests terminate with a friendly 504 response.

    Uses a thread-based timeout to be safe in multi-threaded servers
    (like Render, Gunicorn, uWSGI). No SIGALRM is used.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self.timeout_seconds = getattr(settings, "REQUEST_TIMEOUT_SECONDS", 15)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self.timeout_seconds <= 0:
            return self.get_response(request)

        return self._run_with_thread_timeout(request)

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

    def _run_with_thread_timeout(self, request: HttpRequest) -> HttpResponse:
        """
        Runs the request in a separate thread and enforces a timeout.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.get_response, request)
            try:
                response = future.result(timeout=self.timeout_seconds)
            except concurrent.futures.TimeoutError:
                logger.warning("Request exceeded %s seconds (thread timeout)", self.timeout_seconds)
                return self._timeout_response(request)
        return response
