import threading
import json
from os import getenv
from typing import Any, Self, get_type_hints
import logging

logger = logging.getLogger(__name__)


class BaseEnvConfig:
    """Production-ready environment loader."""

    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._env_cache: dict[str, Any] = {}
        self._sync_env()
        self._initialized = True

    def _sync_env(self) -> None:
        hints = get_type_hints(self.__class__)
        for field, _ in hints.items():
            raw = getenv(field)

            if raw is None:
                if hasattr(self, field):
                    value = getattr(self, field)
                    logger.info(f"{field} not set, using default: {value}")
                else:
                    raise EnvironmentError(
                        f"Missing required environment variable: {field}"
                    )
            else:
                if field in self._env_cache:
                    value = self._env_cache[field]
                else:
                    value = self._parse_env_value(raw)
                    self._env_cache[field] = value

            setattr(self, field, value)

    def _parse_env_value(self, raw: str) -> Any:
        """Parse string from environment."""
        lowered = raw.lower()

        # Boolean parsing
        if lowered == "true":
            return True
        if lowered == "false":
            return False

        # JSON parsing
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Numeric parsing
        if raw.isdigit():
            return int(raw)
        try:
            return float(raw)
        except ValueError:
            pass

        # Fallback: plain string
        return raw

    def reload(self) -> None:
        """Reload environment variables at runtime."""
        self._env_cache.clear()
        self._sync_env()
        logger.info("Environment variables reloaded.")
