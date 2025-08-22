from __future__ import annotations

import uuid
from uuid import UUID

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BigAutoField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextChoices,
    TextField,
    UUIDField,
)
from django.utils import timezone


class TodoPriority(TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class TodoStatus(TextChoices):
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"


class BaseModel(Model):
    """Abstract base with UUID PK and timestamps."""

    id: BigAutoField[int, int] = BigAutoField(primary_key=True, editable=False)
    uuid: UUIDField[UUID, str] = UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at: DateTimeField[str, str] = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField[str, str] = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Todo(BaseModel):
    """Main Todo model."""

    user: ForeignKey[int, AbstractUser] = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="todos",
        help_text="Owner of this todo",
    )
    title: CharField[str, str] = CharField(max_length=255)
    description: TextField[str, str] = TextField(blank=True, default="")
    due_date: DateTimeField[str | None, str | None] = DateTimeField(
        null=True,
        blank=True,
    )

    priority: CharField[str, str] = CharField(
        max_length=20,
        choices=TodoPriority.choices,
        default=TodoPriority.MEDIUM,
    )
    status: CharField[str, str] = CharField(
        max_length=20,
        choices=TodoStatus.choices,
        default=TodoStatus.PENDING,
    )

    completed_at: DateTimeField[str | None, str | None] = DateTimeField(
        null=True,
        blank=True,
    )

    def mark_completed(self) -> None:
        """Mark todo as completed safely."""
        self.status = TodoStatus.COMPLETED
        self.completed_at = str(timezone.now())
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def __str__(self) -> str:
        return f"Todo({self.id}, {self.title})"


class Tag(BaseModel):
    """Simple tags for todos."""

    name: CharField[str, str] = CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return f"Tag({self.id}, {self.name})"


class TodoTag(Model):
    """Many-to-many through model for tagging."""

    todo: ForeignKey[int, Todo] = ForeignKey(
        Todo,
        on_delete=CASCADE,
        related_name="todo_tags",
    )
    tag: ForeignKey[int, Tag] = ForeignKey(
        Tag,
        on_delete=CASCADE,
        related_name="tag_todos",
    )

    class Meta:
        unique_together = ("todo", "tag")
