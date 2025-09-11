from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from djresttoolkit.pagination import PaginatedDataBuilder
from djresttoolkit.views.mixins import RetrieveObjectMixin

from .models import Todo
from .serializers import TodoSerializer


class TodoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        pagination = PaginatedDataBuilder[Todo](
            request=request,
            serializer_class=TodoSerializer,
            queryset=Todo.objects.all(),
        )
        return Response(data=pagination.paginated_data)

    @extend_schema(
        request=TodoSerializer,
        responses=TodoSerializer,
        description="Create one or multiple todos. If a list is provided, bulk create is supported.",
    )
    def post(self, request: Request) -> Response:
        serializer = TodoSerializer(
            data=request.data,
            many=isinstance(request.data, list),
        )

        if serializer.is_valid():
            serializer.save(user=request.user)

        return Response(data=serializer.data)


class TodoDetailView(RetrieveObjectMixin[Todo], APIView):
    """Retrive a single todo."""

    permission_classes = [AllowAny]
    queryset = Todo.objects.all()

    @extend_schema(
        responses=TodoSerializer,
    )
    def get(self, request: Request, id: int) -> Response:
        todo = self.get_object(id=id)
        serializer = TodoSerializer(instance=todo, many=False)
        return Response(data=serializer.data)
