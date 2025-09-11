from djresttoolkit.serializers import EnhancedModelSerializer

from .models import Todo


class TodoSerializer(EnhancedModelSerializer[Todo]):
    class Meta:
        model = Todo
        exclude = ["created_at", "updated_at"] 
