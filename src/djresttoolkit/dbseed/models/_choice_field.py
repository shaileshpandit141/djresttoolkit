import random

from pydantic import Field


def choice_field[T](choices: list[T]) -> T:
    """
    Creates a field with a default value randomly selected from the provided choices.
    Args:
        choices (list[T]): A list of possible values for the field.
    Returns:
        T: A field with a default value randomly chosen from the given choices.
    """

    return Field(
        default_factory=lambda: random.choice(seq=choices),
    )
