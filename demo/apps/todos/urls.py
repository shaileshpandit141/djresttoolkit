"""
URL configuration for todos app.
"""

from django.urls import path

from .views import TodoDetailView, TodoListView

urlpatterns = [
    path("", TodoListView.as_view(), name="todo-list"),
    path("<int:id>/", TodoDetailView.as_view(), name="todo-detail"),
]
