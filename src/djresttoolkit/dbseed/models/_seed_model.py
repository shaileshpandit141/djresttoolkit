from __future__ import annotations

from typing import Any, ClassVar

from django.db.models import ForeignKey, ManyToManyField, Model, OneToOneField
from pydantic import BaseModel


class SeedModel(BaseModel):
    """
    Base class for all fake data models.
    Each subclass must define a `__model__` attribute (a Django model).
    """

    __model__: ClassVar[type[Model] | None] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__model__"):
            raise TypeError(
                f"{cls.__name__} must define a `__model__` attribute "
                f"pointing to a Django model"
            )

    @classmethod
    def get_model(cls) -> type[Model]:
        """Class-level access to the Django model."""
        if cls.__model__ is None:
            raise ValueError(
                f"{cls.__name__} has no `__model__` defined. "
                "Please set it to a Django model class."
            )
        return cls.__model__

    @classmethod
    def create_instance(cls) -> tuple[dict[str, Any], list[ManyToManyField[Any, Any]]]:
        """Handle ForeignKey, OneToOneField and ManyToMany relationship."""

        # dump pydantic model to python dict
        data = cls().model_dump()

        # Handle ForeignKey and OneToOneField
        for field in cls.get_model()._meta.get_fields():
            if isinstance(field, (ForeignKey, OneToOneField)):
                rel_model = field.remote_field.model
                if rel_model.objects.exists():
                    # For OneToOne, must ensure unique (pick unused relation)
                    if isinstance(field, OneToOneField):
                        used_ids = cls.get_model().objects.values_list(
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
            for field in cls.get_model()._meta.get_fields()
            if isinstance(field, ManyToManyField)
        ]
        return data, m2m_fields
  