from typing import Any
from urllib.parse import urlencode
from django.http import HttpRequest
from django.urls import reverse
from rest_framework.request import Request


def build_absolute_uri(
    request: HttpRequest | Request,
    url_name: str,
    query_params: dict[str, Any] | None = None,
    *args: Any,
    **kwargs: Any,
) -> str:
    """
    Build an absolute URI for a given Django or DRF view.

    Args:
        request: Django or DRF request object.
        url_name: Name of the URL pattern to reverse.
        query_params: Optional dictionary of query parameters.
        *args: Positional arguments for the URL.
        **kwargs: Keyword arguments for the URL.

    Returns:
        Absolute URI as a string.
    """
    url = reverse(url_name, args=args, kwargs=kwargs)

    if query_params:
        url += f"?{urlencode(query_params, doseq=True)}"

    return request.build_absolute_uri(url)
