from rest_framework.views import exception_handler
from rest_framework import exceptions, status


def status_code_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
