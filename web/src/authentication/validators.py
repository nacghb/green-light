from rest_framework import status
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import User


class MessagedException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "err_custom_undefined"
    default_code = "ERROR"

    def __init__(self, status_code=None, detail=None, title=None):
        if detail is None:
            self.detail = self.default_detail
            self.code = self.default_code
        else:
            self.detail = detail
            self.code = title
            self.status_code = status_code


def is_valid_password(password):
    if len(password) < 8:
        return MessagedException(
            detail="err_password_tooshort",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return True


def cleaned_email_to_insert(email):
    email = email.rstrip().lower()
    try:
        validate_email(email)
    except ValidationError:
        raise MessagedException(
            detail="err_email_invalid", status_code=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()
    if user and user.is_active:
        raise MessagedException(
            detail="err_user_exists", status_code=status.HTTP_400_BAD_REQUEST
        )
    if user and not user.is_active:
        user.delete()

    return email
