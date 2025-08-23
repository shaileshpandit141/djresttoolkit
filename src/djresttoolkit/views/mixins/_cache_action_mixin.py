from functools import wraps
from typing import Any, Callable

from rest_framework.response import Response
from ._cache_ops_mixin import CacheOpsMixin
from rest_framework.request import Request


class CacheActionMixin(CacheOpsMixin):
    """Provides decorator for caching custom @action methods."""

    def cache_action(
        self,
        detail: bool = False,
        action_name: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(view_method: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(view_method)
            def wrapper(
                viewset: Any,
                request: Request,
                *args: Any,
                **kwargs: Any,
            ) -> Response:
                name = action_name or view_method.__name__
                pk = kwargs.get("pk") if detail else None
                action_type = "custom-detail" if detail else "custom-list"
                key = viewset.get_cache_key(action_type, pk=pk, action_name=name)

                def get_data() -> None | Any:
                    response = view_method(
                        viewset,
                        request,
                        *args,
                        **kwargs,
                    )
                    return response.data if isinstance(response, Response) else response

                data = viewset.get_or_set_cache(key, get_data)
                return Response(data)

            return wrapper

        return decorator
