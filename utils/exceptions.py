# utils/exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status

class PermissionDeniedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied: you do not have the required role or privileges to perform this action."
    default_code = "permission_denied"

# Opcional: handler para que todos los errores se vean profesionales
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "detail": str(getattr(exc, 'detail', exc))
        }
    else:
        response = Response(
            {"detail": "Internal server error."},
            status=500
        )

    return response
