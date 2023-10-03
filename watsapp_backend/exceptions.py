from rest_framework.views import exception_handler
from rest_framework import exceptions, status
from django.utils.translation import gettext_lazy as _

def status_code_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response

class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Already exists.')
    default_code = 'conflict_error'