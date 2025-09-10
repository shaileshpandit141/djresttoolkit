from django.forms.models import model_to_dict
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from djresttoolkit.views.mixins import RetrieveObjectMixin

from .models import Todo


class TodoDetailView(RetrieveObjectMixin[Todo], APIView):
    permission_classes = [AllowAny]
    queryset = Todo.objects.all()

    def get(self, request: Request, id: int) -> Response:
        todo = self.get_object(id=id)
        return Response(data=model_to_dict(todo))
