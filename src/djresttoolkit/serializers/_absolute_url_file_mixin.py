import logging
from typing import Any, cast
from urllib.parse import urlparse

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class MissingRequestContext(Exception):
    """Custom exception for missing request in serializer context."""

    ...


class AbsoluteUrlFileMixin:
    """
    A mixin that updates FileField and ImageField URLs in serializer output
    to be absolute URLs, compatible with cloud storage backends.
    """

    # manually specify file fields for non-model serializers
    file_fields: list[str] | None = None

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Extend serializer representation to enhance file field URLs."""
        representation = cast(dict[str, Any], super().to_representation(instance))  # type: ignore[misc]
        request = self.context.get("request")  # type: ignore
        return self.enhance_file_fields(instance, representation, request)

    def enhance_file_fields(
        self,
        instance: Any,
        representation: dict[str, Any],
        request: Any,
    ) -> dict[str, Any]:
        if request is None:
            logger.warning("Request not found in serializer context.")
            if settings.DEBUG:
                raise MissingRequestContext("Request not found in serializer context.")
            return representation

        # Collect only file-related model fields if available
        model_fields = (
            {
                field.name: field
                for field in instance._meta.get_fields()
                if isinstance(field, (models.FileField, models.ImageField))
            }
            if hasattr(instance, "_meta")
            else {}
        )

        manual_fields = getattr(self, "file_fields", []) or []

        for field_name, field_value in representation.items():
            model_field = model_fields.get(field_name)

            is_file_field = model_field or (field_name in manual_fields)
            if not is_file_field:
                continue

            try:
                # Get file URL from instance or raw serializer value
                if model_field:
                    file_instance = getattr(instance, field_name, None)
                    file_url = (
                        getattr(file_instance, "url", None) if file_instance else None
                    )
                else:
                    file_url = field_value

                if not file_url:
                    logger.info("No file found for field: %s", field_name)
                    representation[field_name] = None
                    continue

                # Only build absolute URL if it's relative
                parsed_url = urlparse(str(file_url))
                if not parsed_url.netloc:  # relative path
                    file_url = request.build_absolute_uri(file_url)

                representation[field_name] = file_url
                logger.debug("Enhanced URL for %s: %s", field_name, file_url)

            except Exception as error:
                logger.error(
                    "Unexpected error processing file field %s: %s",
                    field_name,
                    error,
                )

        return representation
