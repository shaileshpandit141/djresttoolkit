from typing import Iterable, Tuple, cast

from django.db.models import Model
from django.core.exceptions import FieldDoesNotExist


class AttributeDoesNotExist(Exception):
    """
    Exception raised when a required attribute is missing in the class.
    """


class ChoiceFieldNotFound(Exception):
    """
    Exception raised when a specified choice field is missing
    or has invalid/empty choices in the model.
    """


class ModelChoiceFieldMixin:
    """
    Mixin to retrieve choice fields from a Django model.
    Designed to work seamlessly with Django's TextChoices.
    """

    model: type[Model] | None = None
    choice_fields: list[str] | None = None

    @classmethod
    def get_choices(cls) -> dict[str, dict[str, str]]:
        """
        Retrieve the choice fields from the model class.

        Returns:
            dict[str, dict[str, str]]: A dictionary where keys are field names
            and values are dictionaries of choices (value => label).

        Raises:
            ModelAttributeNotFound: If the model attribute is not set.
            ChoiceFieldAttributeNotFound: If the choice_fields attribute is not set.
            ChoiceFieldNotFound: If a field does not exist, has no choices,
                                 or has an invalid choice format.
        """

        if cls.model is None:
            raise AttributeDoesNotExist("Model attribute is not set in the class.")

        if cls.choice_fields is None:
            raise AttributeDoesNotExist(
                "The choice_fields attribute must be set in the class."
            )

        choices_as_dict: dict[str, dict[str, str]] = {}

        for field in cls.choice_fields:
            try:
                field_obj = cls.model._meta.get_field(field)  # type: ignore[attr-defined]
            except FieldDoesNotExist as e:
                raise ChoiceFieldNotFound(
                    f"The field '{field}' does not exist in model '{cls.model.__name__}'."
                ) from e

            raw_choices = cast(
                Iterable[Tuple[str, str]],
                field_obj.choices or [],  # type: ignore[union-attr]
            )

            if not raw_choices:
                raise ChoiceFieldNotFound(
                    f"The field '{field}' in model '{cls.model.__name__}' has no choices defined."
                )

            if not all(
                isinstance(choice, (list, tuple)) and len(choice) == 2  # type: ignore[misc]
                for choice in raw_choices
            ):
                raise ChoiceFieldNotFound(
                    f"The field '{field}' in model '{cls.model.__name__}' has invalid choice format. "
                    "Expected an iterable of 2-tuples (value, label)."
                )

            choices_as_dict[field] = dict(raw_choices)

        return choices_as_dict
