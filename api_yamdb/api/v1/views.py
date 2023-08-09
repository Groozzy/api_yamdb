from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers

User = get_user_model()


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request) -> Response:
        username = request.data.get('username')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            if User.objects.get(username=username).email != email:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            self.__send_confirmation_code(username, email)
            return Response(status=status.HTTP_200_OK)

        serializer = serializers.SignupSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.__send_confirmation_code(username, email)
        return Response(serializer.data)

    @staticmethod
    def __send_confirmation_code(username: str, email: str) -> None:
        user = get_object_or_404(User, username=username)
        confirmation_code: str = default_token_generator.make_token(user)
        send_mail('Confirmation code', confirmation_code, settings.ADMIN_EMAIL,
                  [email])
