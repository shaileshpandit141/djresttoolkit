import hashlib
import json
from typing import Any


class CacheKeyMixin:
    """Handles generating unique cache keys for views."""

    cache_timeout: int = 300

    def get_cache_timeout(self) -> int:
        return self.cache_timeout

    def get_cache_key(
        self,
        action_type: str,
        pk: Any | str = None,
        action_name: str | None = None,
    ) -> str | None:
        if action_type in ("list", "custom-list"):
            query_params = dict(sorted(self.request.query_params.items()))  # type: ignore
            query_string = json.dumps(query_params, separators=(",", ":"))
            query_hash = hashlib.md5(query_string.encode()).hexdigest()
            if action_type == "list":
                return f"{self.basename}_list_{query_hash}"  # type: ignore
            return f"{self.basename}_{action_name}_list_{query_hash}"  # type: ignore

        if action_type in ("retrieve", "custom-detail") and pk is not None:
            if action_type == "retrieve":
                return f"{self.basename}_detail_{pk}"  # type: ignore
            return f"{self.basename}_{action_name}_detail_{pk}"  # type: ignore

        return None
