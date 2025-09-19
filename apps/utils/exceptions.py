from rest_framework import exceptions, status, views
from rest_framework_simplejwt import exceptions as rest_exceptions


def custom_exception_handler(exc, context):
    """Custom exception handler

    Args:
        exc (_type_): exception
        context (_type_): context

    Returns:
        _type_: response
    """
    response = views.exception_handler(exc, context)

    if isinstance(exc, (exceptions.NotAuthenticated)) or isinstance(
        exc, (rest_exceptions.InvalidToken)
    ):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
