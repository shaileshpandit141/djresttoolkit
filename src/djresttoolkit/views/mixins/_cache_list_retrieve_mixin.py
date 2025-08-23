from typing import Any

from rest_framework.response import Response
from rest_framework.request import Request
from ._cache_action_mixin import CacheActionMixin


class CacheListRetrieveMixin(CacheActionMixin):
    """Caches list() and retrieve() responses."""

    def list(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        cache_key = self.get_cache_key("list")
        if not cache_key:
            return super().list(request, *args, **kwargs)  # type: ignore

        data = self.get_or_set_cache(
            cache_key,
            lambda: self._get_list_data(request),  # type: ignore
        )
        return Response(data)

    def _get_list_data(self, request: Response) -> Any:
        queryset = self.filter_queryset(self.get_queryset())  # type: ignore
        page = self.paginate_queryset(queryset)  # type: ignore
        if page is not None:
            serializer = self.get_serializer(page, many=True)  # type: ignore
            return self.get_paginated_response(serializer.data).data  # type: ignore
        else:
            serializer = self.get_serializer(queryset, many=True)  # type: ignore
            return serializer.data  # type: ignore

    def retrieve(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        pk = self.kwargs.get("pk")  # type: ignore
        cache_key = self.get_cache_key("retrieve", pk=pk)  # type: ignore
        if not cache_key:
            return super().retrieve(request, *args, **kwargs)  # type: ignore

        data = self.get_or_set_cache(
            cache_key,
            lambda: self._get_detail_data(),
        )
        return Response(data)

    def _get_detail_data(self) -> Any:
        instance = self.get_object()  # type: ignore
        serializer = self.get_serializer(instance)  # type: ignore
        return serializer.data  # type: ignore
