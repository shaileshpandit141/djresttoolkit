from __future__ import annotations

from typing import Any

from django.db.models import ForeignKey, ManyToManyField, Model, OneToOneField
from pydantic import BaseModel, PrivateAttr


class BaseDBSeedModel(BaseModel):
    """
    Base class for all fake data models.
    Each subclass must define a `model` attribute.
    """

    class Meta:
        model: type[Model]

    _meta: type[Meta] = PrivateAttr()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "Meta") or not hasattr(cls.Meta, "model"):
            raise TypeError(
                f"{cls.__name__} must define a Meta class with django model"
            )
        cls._meta = cls.Meta

    @classmethod
    def create_instance(cls) -> tuple[dict[str, Any], list[ManyToManyField[Any, Any]]]:
        """Handle ForeignKey, OneToOneField and ManyToMany relationship."""

        # dump pydantic model to python dict
        data = cls().model_dump()

        # Handle ForeignKey and OneToOneField
        for field in cls._meta.model._meta.get_fields():
            if isinstance(field, (ForeignKey, OneToOneField)):
                rel_model = field.remote_field.model
                if rel_model.objects.exists():
                    # For OneToOne, must ensure unique (pick unused relation)
                    if isinstance(field, OneToOneField):
                        used_ids = cls._meta.model.objects.values_list(
                            field.name, flat=True
                        )
                        available = rel_model.objects.exclude(pk__in=used_ids)
                        if available.exists():
                            data[field.name] = available.order_by("?").first()
                    else:  # Normal ForeignKey
                        data[field.name] = rel_model.objects.order_by("?").first()

        # Collect ManyToMany fields
        m2m_fields: list[ManyToManyField[Any, Any]] = [
            field
            for field in cls._meta.model._meta.get_fields()
            if isinstance(field, ManyToManyField)
        ]
        return data, m2m_fields
