from django.contrib.auth.models import User
from rest_framework.serializers import CharField, Serializer


class RetrieveTokenSerializer(Serializer[User]):
    username = CharField(required=True)
    password = CharField(write_only=True, required=True)
