from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Tag, Todo, TodoTag

if TYPE_CHECKING:
    class TodoAdminBase(ModelAdmin[Todo]): ...
    class TagAdminBase(ModelAdmin[Todo]): ...
    class TodoTagAdminBase(ModelAdmin[Todo]): ...
else:
    class TodoAdminBase(ModelAdmin): ... 
    class TagAdminBase(ModelAdmin): ...
    class TodoTagAdminBase(ModelAdmin): ...


@admin.register(Todo)
class TodoAdmin(TodoAdminBase):
    list_display = [
        "id",
        "user",
        "title",
        "due_date",
        "priority",
        "status",
    ]
    list_display_links = list_display
    ordering = ("-id",)
    list_filter = ["priority", "status"]
    search_fields = ["title"]


@admin.register(Tag)
class TagAdmin(TagAdminBase):
    list_display = ["id", "name"]
    list_display_links = list_display
    ordering = ("-id",)
    search_fields = ["name"]


@admin.register(TodoTag)
class TodoTagAdmin(TodoTagAdminBase):
    list_display = ["id", "todo", "tag"]
    list_display_links = list_display
    ordering = ("-id",)
