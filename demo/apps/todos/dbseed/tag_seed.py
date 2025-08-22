from djresttoolkit.dbseed.models import (  # type: ignore[import-not-found]
    Field,
    Gen,
    SeedModel,
)

from ..models import Tag


class TagSeedModel(SeedModel):
    __model__ = Tag

    name: str = Field(default_factory=Gen.word)
