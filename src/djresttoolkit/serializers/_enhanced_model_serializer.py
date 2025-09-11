from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.db.models import Field as DjangoField
from django.db.models import Model
from rest_framework.serializers import Field as DrfField
from rest_framework.serializers import ModelSerializer
from rest_framework.utils.model_meta import RelationInfo


class EnhancedModelSerializer[T: Model](ModelSerializer[Model]):
    """
    A DRF ModelSerializer that automatically applies Django model field
    `error_messages` unless explicitly overridden in the serializer.
    """

    def _merge_error_messages(
        self,
        field_kwargs: dict[str, Any],
        model_field: DjangoField[Any, Any] | None,
    ) -> dict[str, Any]:
        """Safely merge model field error_messages with serializer kwargs."""
        model_errors: dict[str, str] | None = getattr(
            model_field, "error_messages", None
        )
        if model_errors:
            existing: dict[str, str] = field_kwargs.get("error_messages", {})
            field_kwargs["error_messages"] = {**deepcopy(model_errors), **existing}
        return field_kwargs

    def build_standard_field(
        self,
        field_name: str,
        model_field: DjangoField[Any, Any],
    ) -> tuple[type[DrfField[Any, Any, Any, Any]], dict[str, Any]]:
        field_class, field_kwargs = super().build_standard_field(  # type: ignore
            field_name,
            model_field,
        )
        return field_class, self._merge_error_messages(
            field_kwargs,
            model_field,
        )  # type: ignore

    def build_relational_field(
        self,
        field_name: str,
        relation_info: RelationInfo,
    ) -> tuple[type[DrfField[Any, Any, Any, Any]], dict[str, Any]]:
        field_class, field_kwargs = super().build_relational_field(  # type: ignore
            field_name,
            relation_info,
        )
        return field_class, self._merge_error_messages(
            field_kwargs,
            relation_info.model_field,  # type: ignore
        )
