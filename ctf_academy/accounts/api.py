from __future__ import annotations

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
