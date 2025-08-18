"""
URL configuration for apps_config project.
"""

from apps.todos import urls as todos_urls
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import RetrieveToken

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/token/old/", obtain_auth_token, name="api_token_auth"),
    path("api/v1/auth/token/", RetrieveToken.as_view(), name="api_token"),
    path("api/v1/todos/", include(todos_urls)),
]
