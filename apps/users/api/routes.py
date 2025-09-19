from rest_framework.routers import DefaultRouter

from apps.users.api.views import RegisterViewSet, LoginViewSet


router = DefaultRouter()
router.register(r"", RegisterViewSet, basename="register")
router.register(r"", LoginViewSet, basename="login")
