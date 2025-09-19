from django.db import models

from uuid import uuid4

from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny


class BaseModel(models.Model):
    """Abstract base model with created_at and updated_at fields."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseAuthViewSet(ViewSet):
    http_method_names = ["post", "head"]
    permission_classes = [AllowAny]


class BaseViewSet(ViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]


class BaseModelViewSet(ModelViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
