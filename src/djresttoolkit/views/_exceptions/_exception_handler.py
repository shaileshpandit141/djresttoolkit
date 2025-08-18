from typing import Any, cast

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework import status, views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """
    Custom exception handler that preserves DRF's default functionality
    while adding custom throttling behavior.
    """

    # Call DRF's default exception handler first
    response: Response | None = views.exception_handler(exc, context)

    request: Request | None = context.get("request")
    view = context.get("view")

    if request and view:
        # Pick throttle classes from view or default to AnonRateThrottle
        throttle_classes: list[type[AnonRateThrottle]] = getattr(
            view, "throttle_classes", [AnonRateThrottle]
        )

        # Set default throttles if user doesn't provide
        default = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_CLASSES", [])
        if not throttle_classes:
            if default:
                throttle_classes = []
                for path in default:
                    throttle_classes.append(import_string(path))

        # Handle all throttles by looping it
        for throttle_class in throttle_classes:
            throttle = throttle_class()
            cache_key = throttle.get_cache_key(request, view)
            if not cache_key:
                continue

            history: list[float] = cache.get(cache_key, [])
            now = timezone.now().timestamp()
            duration: float = cast(float, throttle.duration)  # type: ignore[attr-defined]

            # Keep only non-expired timestamps
            history = [float(ts) for ts in history if now - float(ts) < duration]

            # If throttle limit exceeded
            if len(history) >= throttle.num_requests:  # type: ignore[attr-defined]
                retry_after: float = (
                    duration - (now - history[0]) if history else duration
                )

                return Response(
                    data={
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": {
                            "time": round(retry_after, 2),
                            "unit": "seconds",
                        },
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Otherwise add current timestamp
            history.append(now)
            cache.set(key=cache_key, value=history, timeout=duration)

    # If DRF handled the exception, return that response
    return response
