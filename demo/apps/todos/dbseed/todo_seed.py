from django.utils import timezone

from djresttoolkit.dbseed.models import (  # type: ignore[import-not-found]
    Field,
    Gen,
    SeedModel,
)

from ..models import Todo, TodoPriority, TodoStatus


class TodoSeedModel(SeedModel):
    __model__ = Todo

    title: str = Field(
        default_factory=lambda: Gen.sentence(nb_words=4),
    )
    description: str = Field(
        default_factory=lambda: Gen.sentence(nb_words=20),
    )
    due_date: str | None = Field(
        default_factory=lambda: Gen.date_time_this_year(
            before_now=False, after_now=True
        )
        .replace(tzinfo=timezone.get_current_timezone())
        .isoformat(),
    )
    priority: str = Field(
        default_factory=lambda: Gen.random_element(
            elements=[choice[0] for choice in TodoPriority.choices]
        ),
    )
    status: str = Field(
        default_factory=lambda: Gen.random_element(
            elements=[choice[0] for choice in TodoStatus.choices]
        ),
    )
    completed_at: str | None = Field(
        default_factory=lambda: Gen.date_time_this_year(
            before_now=False, after_now=True
        )
        .replace(tzinfo=timezone.get_current_timezone())
        .isoformat(),
    )
