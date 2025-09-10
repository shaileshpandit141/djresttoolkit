from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet
from django.http import Http404


class RetrieveObjectMixin[T: Model]:
    """
    Retrieve a single model object by filters.

    Requires the `queryset` attribute to be set in the class that inherits this mixin.

    Raises `Http404` when the object is missing.

    This works in both Django views and DRF views.

    Example:
    ```
        class MyView(RetrieveModelMixin[Book], APIView):
            queryset = Book.objects.all()

            def get(self, request, *args, **kwargs):
                obj = self.get_object(id=1)
                return JsonResponse(obj.to_dict())
    ```
    """

    queryset: QuerySet[T] | None = None

    def get_object(self, **filters: Any) -> T:
        """Retrieve a model object based on provided filters."""

        if self.queryset is None:
            raise ImproperlyConfigured(
                "Queryset attribute is not set in the class.",
            )

        try:
            return self.queryset.get(**filters)
        except self.queryset.model.DoesNotExist:
            raise Http404(self.not_found_detail())

    def not_found_detail(self) -> dict[str, str] | str:
        """
        Hook for customizing the 404 message.
        Can be overridden per view.
        """

        if self.queryset is None:
            raise ImproperlyConfigured(
                "Queryset attribute is not set in the class.",
            )

        verbose_name = self.queryset.model._meta.verbose_name
        model_name = (
            verbose_name.title() if verbose_name else self.queryset.model.__name__
        )
        return f"The requested {model_name} was not found."
