import logging
from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from django.db.models import Model
from ._page_number_pagination import PageNumberPagination

# Get logger from logging.
logger = logging.getLogger(__name__)


class PaginatedDataBuilder[T: Model]:
    """Builder class to handle pagination and serialization."""

    def __init__(
        self,
        request: Request,
        serializer_class: type[BaseSerializer[T]],
        queryset: QuerySet[T],
    ) -> None:
        """Initilize the PaginatedDataBuilder class."""
        self.request = request
        self.serializer_class = serializer_class
        self.queryset = queryset

    def get_paginated_data(self) -> dict[str, Any]:
        """Paginate and serialize the queryset."""

        logger.debug("Starting pagination with custom PageNumberPagination.")
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(
            self.queryset,
            self.request,
        )

        # If no data is returned from pagination, raise NotFound
        if page is None:
            logger.warning("No data returned from pagination. Possibly invalid page.")
            raise NotFound("The requested records were not found.")

        # Serialize the paginated data
        serializer = self.serializer_class(
            instance=page,  # type: ignore
            many=True,
            context={"request": self.request},
        )

        # Construct the paginated response
        paginated_data = {
            "page": {
                "current": paginator.page.number,  # type: ignore
                "total": paginator.page.paginator.num_pages,  # type: ignore
                "size": paginator.get_page_size(self.request),
                "total_items": paginator.page.paginator.count,  # type: ignore
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
            },
            "results": serializer.data,
        }

        logger.debug(f"Pagination result: {paginated_data}")
        return paginated_data
