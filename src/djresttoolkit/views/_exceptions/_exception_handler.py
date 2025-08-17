from typing import Any, cast

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, views
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Hnadle throttle classes."""

    request: Request | None = context.get("request")
    response: Response | None = views.exception_handler(exc, context)

    # Apply throttling before exception is raised
    if request:
        view = context.get("view")
        if view:
            throttle_classes: list[type[AnonRateThrottle]] = getattr(
                view, "throttle_classes", []
            )
            if not throttle_classes:
                throttle_classes = [AnonRateThrottle]

            # Iterate over the list of throttles class
            for throttle_class in throttle_classes:
                throttle = throttle_class()  # Instantiate the throttle class
                cache_key = throttle.get_cache_key(request, view)
                if cache_key:
                    history: list[float] = cache.get(cache_key, [])
                    now = timezone.now().timestamp()
                    duration: float = cast(float, throttle.duration)  # type: ignore[attr-defined]

                    # Remove expired requests from history
                    history = [
                        float(ts) for ts in history if now - float(ts) < duration
                    ]

                    # Check if throttle limit is exceeded or not
                    if len(history) > throttle.num_requests:  # type: ignore[attr-defined]
                        retry_after: float = duration
                        if history:
                            retry_after = duration - (now - history[0])

                        response = Response(
                            data={
                                "detail": "Too many requests. Please try again later.",
                                "retry_after": {
                                    "time": retry_after,
                                    "unit": "seconds",
                                },
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS,
                        )

                        # Return the response with 429 status code
                        return response
                    else:
                        # Otherwise, add the current request to history and update cache
                        history.append(now)
                        cache.set(key=cache_key, value=history, timeout=duration)

    # Return un updaed response instance
    return response
