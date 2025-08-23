from typing import Any

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination as DrfPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DrfPageNumberPagination):
    """
    Custom PageNumberPagination for Django REST Framework.

    This pagination class extends DRF's PageNumberPagination to provide:
    - Dynamic page size support via the "page-size" query parameter.
    - A streamlined, structured pagination metadata format in API responses.

    Features:
        - Clients can control the number of items per page using the "page-size" query parameter.
        - The paginated response includes a "page" object with detailed pagination metadata and a "results" list.

    Paginated Response Example:
    ```
    {
        "page": {
            "current": 1,
            "total": 10,
            "size": 20,
            "total_items": 200,
            "next": "http://api.example.com/items/?page=2&page-size=20",
            "previous": null
        },
        "results": [ ... ]
    }
    ```

    Attributes:
        page_size_query_param (str): Query parameter name for dynamic page size ("page-size").

    Methods:
        get_paginated_response(data: Any) -> Response:
            Returns a standardized paginated response with metadata and results.

    """

    # Allow clients to set page size via ?page-size=
    page_size_query_param = "page-size"

    def get_paginated_response(self, data: Any) -> Response:
        page = getattr(self, "page", None)
        paginator = getattr(self, "paginator", None)
        request = getattr(self, "request", None)
        if page is None or paginator is None or request is None:
            raise ValidationError(
                {"detail": "Pagination has not been properly configured."}
            )

        items_per_page = self.get_page_size(request)
        return Response(
            {
                "page": {
                    "current": page.number,
                    "total": paginator.num_pages,
                    "size": items_per_page,
                    "total_items": paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )
