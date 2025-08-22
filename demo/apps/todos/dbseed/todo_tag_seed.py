from djresttoolkit.dbseed.models import (  # type: ignore[import-not-found]
    Field,
    Gen,
    SeedModel,
)

from ..models import Tag, Todo, TodoTag


class TodoTagSeedModel(SeedModel):
    __model__ = TodoTag

    todo: int = Field(
        default_factory=lambda: Gen.random_element(
            list(Todo.objects.all().values_list("id", flat=True))
        )
    )
    tag: int = Field(
        default_factory=lambda: Gen.random_element(
            list(Tag.objects.all().values_list("id", flat=True))
        )
    )
