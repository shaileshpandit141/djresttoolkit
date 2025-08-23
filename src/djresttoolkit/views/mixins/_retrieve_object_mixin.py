from typing import Any
from django.db.models import Model, QuerySet


class QuerysetNotDefinedError(Exception):
    """Exception raised when the `queryset` attribute is not set in the class."""

    pass


class RetrieveObjectMixin[T: Model]:
    """
    Mixin to provide a method for retrieving a single model object by filters.

    Requires the `queryset` attribute to be set in the class that inherits this mixin.

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

    def get_object(self, **filters: Any) -> T | None:
        """Retrieve a model object based on provided filters."""

        if self.queryset is None:
            raise QuerysetNotDefinedError(
                "Queryset attribute is not set in the class.",
            )

        try:
            return self.queryset.get(**filters)
        except self.queryset.model.DoesNotExist:
            return None
