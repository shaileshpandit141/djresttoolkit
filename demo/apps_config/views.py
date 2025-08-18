from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .serializers import RetrieveTokenSerializer


class RetrieveToken(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Handle post request and return auth token."""
        serializer = RetrieveTokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,  # type: ignore
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError({"username": ["User not found."]})

        if not user.check_password(password):
            raise ValidationError({"password": ["Password does not match."]})

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})  # type: ignore
