# your_app/exceptions.py
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """Fix the format of the validation error response."""
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ValidationError):
            if 'non_field_errors' in response.data:
                error_message = response.data['non_field_errors'][0]
                return Response(
                    {'detail': error_message},
                    status=response.status_code
                )
            elif isinstance(response.data, dict):
                return Response(
                    {'detail': str(exc)},
                    status=response.status_code
                )

    return response
