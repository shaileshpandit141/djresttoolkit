import logging
import time
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

# Get logger from logging.
logger = logging.getLogger(__name__)


class ResponseTimeMiddleware:
    """Calculte response response time."""

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ) -> None:
        "Initilize response time middleware."
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Handle to response response time calculation."""
        start_time = time.perf_counter()
        response = self.get_response(request)
        end_time = time.perf_counter()

        response_time = f"{round(end_time - start_time, 5)} seconds"
        response["X-Response-Time"] = response_time

        logger.info(f"Request processed in {response_time}")

        return response