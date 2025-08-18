import logging
import re
from datetime import timedelta
from datetime import timezone as dt_timezone
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle, UserRateThrottle

if TYPE_CHECKING:
    from rest_framework.views import APIView

    ViewType = APIView
else:
    ViewType = object

# Get logger from logging.
logger = logging.getLogger(__name__)


class ThrottleInspector:
    """
    Inspects and retrieves DRF throttle details for both class-based
    and function-based views.
    """

    def __init__(
        self,
        view: ViewType,
        request: Request | None = None,
        throttle_classes: list[type[BaseThrottle]] | None = None,
    ) -> None:
        self.view = view
        self.request: Request | None = getattr(view, "request", request)
        self.throttle_classes: list[type[BaseThrottle]] = (
            getattr(view, "throttle_classes", throttle_classes) or []
        )

        if not self.request:
            logger.warning(f"Request object missing in {self._view_name()}.")
        if not self.throttle_classes:
            logger.info(f"No throttles configured for {self._view_name()}.")

    def _view_name(self) -> str:
        if callable(self.view):
            return getattr(self.view, "__name__", str(self.view))
        return type(self.view).__name__

    @staticmethod
    def to_snake_case(name: str) -> str:
        """Convert UpperCamelCase to snake_case and remove 'RateThrottle'."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name.replace("RateThrottle", "")).lower()

    @staticmethod
    def parse_rate(rate: str) -> tuple[int, int] | None:
        """Parse rate string like '100/day' into (limit, duration_in_seconds)."""
        if not rate:
            return None
        match = re.match(r"(\d+)/(second|minute|hour|day)", rate)
        if not match:
            return None
        num_requests, period = match.groups()
        duration_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return int(num_requests), duration_map[period]

    def get_throttle_rate(
        self, throttle_class: type[BaseThrottle]
    ) -> tuple[int, int] | None:
        """Return the (limit, duration_in_seconds) for a throttle class."""
        scope = getattr(throttle_class, "scope", None)
        if not scope:
            logger.warning(f"No scope defined in {throttle_class.__name__}. Skipping.")
            return None

        rate = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {}).get(scope)
        if not rate:
            logger.warning(f"No rate limit found for scope '{scope}'. Skipping.")
            return None

        return self.parse_rate(rate)

    def get_throttle_usage(
        self,
        throttle: UserRateThrottle,
        limit: int,
        duration: int,
    ) -> dict[str, Any]:
        """Return current usage info for a given throttle instance."""
        if not self.request:
            return {
                "limit": limit,
                "remaining": limit,
                "reset_time": None,
                "retry_after": {"time": None, "unit": "seconds"},
            }

        cache_key = throttle.get_cache_key(
            self.request,
            getattr(self.view, "view", self.view),  # type: ignore
        )  # type: ignore
        history: list[Any] = throttle.cache.get(cache_key, []) if cache_key else []

        remaining = max(0, limit - len(history))
        first_request_time = (  # type: ignore
            timezone.datetime.fromtimestamp(history[0], tz=dt_timezone.utc)  # type: ignore[attr-defined]
            if history
            else timezone.now()
        )
        reset_time = first_request_time + timedelta(seconds=duration)  # type: ignore
        retry_after = max(0, int((reset_time - timezone.now()).total_seconds()))  # type: ignore

        return {
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time.isoformat(),  # type: ignore
            "retry_after": {"time": retry_after, "unit": "seconds"},
        }

    def get_details(self) -> dict[str, Any]:
        """
        Return detailed throttle info for all configured throttles.
        If throttling is not configured, returns an empty dict.
        """
        if not self.throttle_classes:
            return {}

        details: dict[str, Any] = {"throttled_by": None, "throttles": {}}

        for throttle_class in self.throttle_classes:
            throttle = throttle_class()
            parsed_rate = self.get_throttle_rate(throttle_class)
            if not parsed_rate:
                continue

            limit, duration = parsed_rate
            scope = getattr(
                throttle_class, "scope", self.to_snake_case(throttle_class.__name__)
            )
            usage = self.get_throttle_usage(throttle, limit, duration)  # type: ignore[arg-type]
            details["throttles"][scope] = usage

            if usage["remaining"] == 0 and not details["throttled_by"]:
                details["throttled_by"] = scope
                logger.info(f"Request throttled by {scope}")

        return details

    def attach_headers(
        self,
        response: Response,
        throttle_info: dict[str, Any] | None,
    ) -> None:
        """
        Attaches throttle details to response headers in DRF-style.

        Header format:
            X-Throttle-{throttle_type}-Limit
            X-Throttle-{throttle_type}-Remaining
            X-Throttle-{throttle_type}-Reset
            X-Throttle-{throttle_type}-Retry-After (in seconds)
        """
        if not throttle_info:
            return

        for throttle_type, data in throttle_info.get("throttles", {}).items():
            response[f"X-Throttle-{throttle_type}-Limit"] = str(data.get("limit", ""))
            response[f"X-Throttle-{throttle_type}-Remaining"] = str(
                data.get("remaining", "")
            )
            response[f"X-Throttle-{throttle_type}-Reset"] = data.get("reset_time") or ""
            retry_after = data.get("retry_after", {}).get("time")
            response[f"X-Throttle-{throttle_type}-Retry-After"] = (
                str(retry_after) if retry_after is not None else "0"
            )

        logger.info(f"Throttle headers attached to response for {self._view_name()}.")
