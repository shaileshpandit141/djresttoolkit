"""
URL configuration for todos app.
"""

from django.urls import path

from .views import TodoDetailView

urlpatterns = [
    path("<int:id>/", TodoDetailView.as_view(), name="todo-detail"),
]
