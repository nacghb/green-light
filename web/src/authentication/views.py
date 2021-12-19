import random
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission


from .validators import cleaned_email_to_insert, is_valid_password
from .models import *
from .serializers import *


class Signup(APIView):
    """
    User Register
    - Input: POST:{"email", "password"}
    - Output: POST:{user details, "detail"}
    - Next step: /Auth/register/activate/
    """

    def post(self, request):
        cleaned_email = cleaned_email_to_insert(request.data["email"])
        is_valid_password(request.data["password"])

        user = User.objects.create_user(
            email=cleaned_email,
            password=request.data["password"],
        )
        # login automatically after Register.
        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "token": token.key,
                "detail": "inf_user_signedup",
            },
            status=status.HTTP_201_CREATED,
        )


class Login(APIView):
    """
    User Login
    - Input: POST:{"email", "password"}
    - Output: POST:{"id","token", "detail"}
    - Next Step: varied
    """

    def post(self, request):
        try:
            user = get_user_model().objects.get(email=request.data["email"])
        except get_user_model().DoesNotExist:
            return Response(
                data={"detail": "err_user_notfound"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(request.data["password"], user.password):
            return Response(
                data={"detail": "err_password_incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "token": token.key,
                "detail": "inf_user_loggedin",
            },
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    """
    User Logout
    - Input: POST:{}
    - Output: POST:{"detail"}
    - Next Step: varied
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = Token.objects.get(key=request.user.auth_token.key)
        token.delete()
        return Response(
            {"detail": "inf_user_loggedout"},
            status=status.HTTP_200_OK,
        )
