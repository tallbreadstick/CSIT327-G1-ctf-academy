from __future__ import annotations

from django.http import JsonResponse
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

TOO_MANY_REQUESTS_MESSAGE = "Too many requests — please try again."


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if isinstance(exc, Throttled):
        detail = {"detail": TOO_MANY_REQUESTS_MESSAGE}
        if exc.wait is not None:
            detail["retry_after"] = exc.wait
        return Response(detail, status=429)
    return response


def _build_payload(*, success: bool, message: str | None, data, meta, code: str | None):
    payload = {"success": success}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    if meta:
        payload["meta"] = meta
    if code and not success:
        payload["code"] = code
    return payload


def success_response(data=None, *, message: str | None = None, meta: dict | None = None, status_code: int = 200):
    return JsonResponse(_build_payload(success=True, message=message, data=data, meta=meta, code=None), status=status_code)


def error_response(message: str, *, code: str = "error", data=None, status_code: int = 400, meta: dict | None = None):
    return JsonResponse(_build_payload(success=False, message=message, data=data, meta=meta, code=code), status=status_code)
