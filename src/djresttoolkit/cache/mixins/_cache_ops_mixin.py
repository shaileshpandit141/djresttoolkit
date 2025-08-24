from typing import Any, Callable

from django.core.cache import cache

from ._cache_key_mixin import CacheKeyMixin


class CacheOpsMixin(CacheKeyMixin):
    """Handles getting, setting, and invalidating cache."""

    def get_or_set_cache(
        self,
        cache_key: str,
        data_fn: Callable[[], Any],
        timeout: int | None = None,
    ) -> Any:
        data = cache.get(cache_key)
        if data is None:
            data = data_fn()
            cache.set(cache_key, data, timeout or self.get_cache_timeout())
        return data

    def invalidate_cache(
        self,
        pk: Any | None = None,
        custom_actions: list[str] | None = None,
    ) -> None:
        if pk:
            key = self.get_cache_key("retrieve", pk=pk)
            if key:
                cache.delete(key)

            if custom_actions:
                for action in custom_actions:
                    key = self.get_cache_key(
                        "custom-detail",
                        pk=pk,
                        action_name=action,
                    )
                    if key:
                        cache.delete(key)

        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{self.basename}_list_*")  # type: ignore
            if custom_actions:
                for action in custom_actions:
                    cache.delete_pattern(f"{self.basename}_{action}_list_*")  # type: ignore
