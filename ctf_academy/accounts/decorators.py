from __future__ import annotations

from functools import wraps

from django.http import HttpRequest, HttpResponse, JsonResponse

from django_ratelimit.decorators import ratelimit

TOO_MANY_REQUESTS_MESSAGE = "Too many requests — please try again."


def friendly_ratelimit(*, rate: str, method: str | None = None, key: str = "user_or_ip"):
    """Wrap django-ratelimit with a consistent 429 response."""

    def decorator(view_func):
        @ratelimit(key=key, rate=rate, method=method, block=False)
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs):
            if getattr(request, "limited", False):
                accepts_json = (
                    request.headers.get("accept", "").lower().find("json") != -1
                    or request.headers.get("x-requested-with") == "XMLHttpRequest"
                    or request.content_type == "application/json"
                )
                if accepts_json:
                    return JsonResponse({"detail": TOO_MANY_REQUESTS_MESSAGE}, status=429)
                return HttpResponse(TOO_MANY_REQUESTS_MESSAGE, status=429)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
