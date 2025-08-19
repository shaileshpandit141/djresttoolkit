from djresttoolkit.dbseed.models import (  # type: ignore[import-not-found]
    BaseSeedModel,
    Field,
    Gen,
)

from ..models import Tag


class TagSeedModel(BaseSeedModel):
    class Meta(BaseSeedModel.Meta):
        model = Tag

    name: str = Field(default_factory=Gen.word)
