from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.api.serializers import UserSerializer
from apps.utils.base import BaseAuthViewSet
from apps.users.models import User
from apps.drivers.models import Driver

from django.contrib.auth import authenticate


class RegisterViewSet(BaseAuthViewSet):
    @action(detail=False, methods=["post"])
    def register(self, request):
        """
        Register a new user.
        """
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        cdl_number = request.data.get("cdl_number")
        confirm_password = request.data.get("confirm_password")

        if not all(
            [
                first_name,
                last_name,
                email,
                phone_number,
                password,
                cdl_number,
                confirm_password,
            ]
        ):
            return Response(
                {"detail": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != confirm_password:
            return Response(
                {"detail": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email already in use"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save()

        driver = Driver.objects.create(
            user=user,
            license_number=cdl_number,
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginViewSet(BaseAuthViewSet, TokenObtainPairSerializer):
    @action(detail=False, methods=["post"])
    def login(self, request):
        """
        Authenticate user and issue JWT token.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = self.get_token(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
