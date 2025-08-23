import logging
from typing import Any, cast

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from rest_framework.serializers import Field as SerializerField
from django.db.models import Field as ModelField


logger = logging.getLogger(__name__)


class BulkCreateMixin:
    """
    A mixin for DRF serializers that supports:
      - Single instance creation with extra context fields
      - Bulk creation from a list of validated_data dicts
      - Updating field error messages with model-specific messages

    Notes:
      - bulk_create() does not trigger model signals or .save()
      - Meta.model must be defined
    """

    def create(
        self, validated_data: dict[str, Any] | list[dict[str, Any]]
    ) -> Model | list[Model]:
        logger.debug("Starting creation", extra={"validated_data": validated_data})

        model: type[Model] | None = getattr(getattr(self, "Meta", None), "model", None)
        if model is None:
            logger.error("Meta.model not defined.")
            raise AttributeError(f"{self.__class__.__name__} missing Meta.model.")

        # Bulk creation
        if isinstance(validated_data, list):
            instances = [model(**item) for item in validated_data]
            if instances:
                logger.info(
                    "Bulk creating instances",
                    extra={"count": len(instances), "model": model.__name__},
                )
                return model.objects.bulk_create(instances)
            logger.info("No instances to create.")
            return []

        # Single instance creation
        if not hasattr(super(), "create"):
            raise NotImplementedError(
                f"{self.__class__.__name__} must be used with a DRF serializer "
                "that implements create()."
            )

        logger.info("Creating a single instance", extra={"model": model.__name__})
        return super().create({**validated_data})  # type: ignore[misc]

    def get_fields(self) -> dict[str, SerializerField[Any, Any, Any, Any]]:
        # DRF serializer fields
        fields = cast(
            dict[str, SerializerField[Any, Any, Any, Any]],
            super().get_fields(),  # type: ignore
        )

        meta = getattr(self, "Meta", None)
        model: type[Model] | None = getattr(meta, "model", None)

        if model is None:
            raise ValueError(f"{self.__class__.__name__}.Meta.model must be defined.")

        logger.debug("Setting up serializer fields", extra={"model": model.__name__})

        for field_name, serializer_field in fields.items():
            try:
                # Django model field
                model_field = cast(
                    ModelField[Any, Any],
                    model._meta.get_field(field_name),  # type: ignore
                )
                if hasattr(model_field, "error_messages"):
                    serializer_field.error_messages.update(model_field.error_messages)
            except FieldDoesNotExist:
                logger.warning(
                    "Skipping serializer field not present on model",
                    extra={"field_name": field_name, "model": model.__name__},
                )

        return fields
