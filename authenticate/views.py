from django.shortcuts import HttpResponse
from rest_framework.views import APIView
import datetime, random, string
from rest_framework.response import Response
from rest_framework import exceptions
from account.serializers import UserSerializer
from .models import UserToken, Reset
from account.models import User
from .authenticate import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    JWTAuthentication,
    send_email,
)
import pyotp


class RegisterApiView(APIView):
    def post(self, request):
        data = request.data
        if data["password"] != data["confirm_password"]:
            raise exceptions.APIException("Password do not match")
        if "phone_number" not in data:
            raise exceptions.APIException("Phone number is required")

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class LoginApiView(APIView):
    def post(self, request):
        phone_number = request.data["phone_number"]
        password = request.data["password"]
        print(phone_number)
        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid Password")

        serializer = UserSerializer(user)
        data = serializer.data
        access_token = create_access_token(data["id"])
        refresh_token = create_refresh_token(data["id"])
        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        )
        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.data = serializer.data
        return response


class AdminLoginApiView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        user = User.objects.filter(email=email, is_admin=True).first()
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid Password")
        print(user.id)
        access_token = create_access_token(user.id, admin=True)
        refresh_token = create_refresh_token(user.id, admin=True)
        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
            is_admin=True,
        )
        response = Response()
        response.set_cookie(
            key="admin_refresh_token", value=refresh_token, httponly=True
        )
        response.set_cookie(key="admin_access_token", value=access_token, httponly=True)
        response.data = {"token": access_token}
        return response


class TwoFactorAPIView(APIView):
    def post(self, request):
        id = request.data["digits"]
        user = User.objects.filter(pk=id)
        if not user:
            raise exceptions.AuthenticationFailed("Invalid Password")
        secret = user.tfa_secret if user.tfa_secret != "" else request.data["secret"]
        # print(Color.G,user.tfa_secret,'oooooooooooooyeaaaaaaaaaaaaaaaaaaaaaaa'.data,Color.E)
        access_token = create_access_token(id)
        refresh_token = create_refresh_token(id)
        UserToken.objects.create(
            user_id=id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        )
        response = Response()
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        response.data = {"login": "success"}
        return response


class LoginWithPhoneAPIView(APIView):
    def post(self, request):
        phone_number = request.data["phone_number"]
        return Response({"verify": "success"})


class UserAPIView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UsersAPIView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = User.objects.all()
        return Response(UserSerializer(user, many=True).data)


class RefreshAPIView(APIView):
    def post(self, request):
        is_admin = request.data["is_admin"]
        print(is_admin)
        refresh_token = request.COOKIES.get("refresh_token")
        id = decode_refresh_token(refresh_token)
        print(id)
        if not UserToken.objects.filter(
            user_id=id,
            token=refresh_token,
            expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc),
        ).exists():
            raise exceptions.AuthenticationFailed("unauthenticated")
        access_token = create_access_token(id)
        response = Response({"token": access_token})
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response


class LogOutAPIView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        UserToken.objects.filter(token=refresh_token).delete()
        response = Response()
        response.delete_cookie(key="refresh_token")
        response.delete_cookie(key="access_token")
        response.data = {"message": "succesfuly loged out"}
        return response


class ForgotAPIView(APIView):
    def post(self, request):
        token = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(18)
        )
        email = request.data["email"]
        print(email, token)
        if not User.objects.filter(email=email).exists():
            raise exceptions.APIException({"message": "User not Found!"})
        Reset.objects.create(email=email, token=token)
        print("ooooo")
        send_email(email, token, "rest_password")
        return Response({"message": "Please check your email"})


class ResetAPIView(APIView):
    def post(self, request):
        data = request.data
        if data["password"] != data["confirm_password"]:
            raise exceptions.APIException("Password do not match")
        reset_password = Reset.objects.filter(token=data["token"]).first()
        if not reset_password:
            raise exceptions.APIException("Invalid Link")
        user = User.objects.filter(email=reset_password.email).first()
        if not user:
            raise exceptions.APIException("User Not Found!")
        user.set_password(data["password"])
        user.save()
        reset_password.delete()

        return Response({"message": "success"})


class AdminLgoinAPIView(APIView):
    def post(self, request):
        return Response()


class AdminLogOutAPIView(APIView):
    def post(self, request):
        return Response()
