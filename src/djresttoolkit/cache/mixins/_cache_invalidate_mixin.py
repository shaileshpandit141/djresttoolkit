from typing import Any
from rest_framework.request import Request
from rest_framework.response import Response
from ._cache_list_retrieve_mixin import CacheListRetrieveMixin


class CacheInvalidateMixin(CacheListRetrieveMixin):
    """Invalidate caches after create, update, destroy."""

    def create(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        response = super().create(request, *args, **kwargs)  # type: ignore
        self.invalidate_cache()
        return response  # type: ignore

    def update(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        response = super().update(request, *args, **kwargs)  # type: ignore
        self.invalidate_cache(pk=self.kwargs.get("pk"))  # type: ignore
        return response  # type: ignore

    def destroy(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        response = super().destroy(request, *args, **kwargs)  # type: ignore
        self.invalidate_cache(pk=self.kwargs.get("pk"))  # type: ignore
        return response  # type: ignore
