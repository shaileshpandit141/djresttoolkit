# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from djresttoolkit.models.mixins import ModelChoiceFieldMixin, AttributeDoesNotExist
from django.db.models import Model


class ChoiceFieldsAPIView(APIView):
    """
    Generic API view to return choice fields from a model.
    """

    model_class: type[Model] | None = None
    choice_fields: list[str] | None = None

    def get(self, request: Request) -> Response:
        """
        Return a JSON response with all choices for the specified fields.
        """
        if not self.model_class or not self.choice_fields:
            raise AttributeDoesNotExist(
                "model_class and choice_fields must be set.",
            )

        # Dynamically create a mixin instance
        class DynamicChoiceMixin(ModelChoiceFieldMixin):
            model = self.model_class
            choice_fields = self.choice_fields

        try:
            choices = DynamicChoiceMixin.get_choices()
            return Response(
                {"choices": choices},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "An error occurred while retrieving choices."},
                status=status.HTTP_400_BAD_REQUEST,
            )
