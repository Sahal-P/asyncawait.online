from django.shortcuts import HttpResponse
from rest_framework.views import APIView
import datetime, random, string
from rest_framework.response import Response
from rest_framework import exceptions, status
from account.serializers import UserSerializer, UserDetailsSerializer
from authenticate.serializers import CreateProfileSerializer, LoginSerializer
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
import phonenumbers


class RegisterApiView(APIView):
    """
    API view  for user registration
    Args:
        APIView (class): A class from the Django Rest Framework for handling HTTP requests.
            This view extends the base APIView class to handle user registration.
    """
    def post(self, request):
        # Extract and validate data from the request 
        print(request.data)
        data = self._get_validated_data(request.data)
        print(data)
        # Creates a new user instance
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
                
        # Craft and return a response with appropriate status code
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _get_validated_data(self, data):
        # Validate passwords and phone number presence
        self._validate_password(data)
        self._validate_email(data)
        self._validate_duplicate(data)
        # formatted_number = self._validate_phone_nummber(data)
        # data["phone_number"] = formatted_number
        return data
    
    def _validate_duplicate(self, data):
        pass
    
    def _validate_password(self, data):
        # Ensure that password and confirm_password match
        if data["password"] != data["confirm_password"]:
            raise exceptions.ValidationError("Password do not match")
    
    def _validate_email(self, data):
        # Ensure that email is present in the data
        if "email" not in data:
            raise exceptions.ValidationError("Email is required")
    
                
    def _validate_phone_nummber(self, data):
        # Ensure that phone_number is present in the data
        if "phone_number" not in data:
            raise exceptions.ValidationError("Phone number is required")
        phone_number = data.get("phone_number")
        return phone_number
        # try:
        #     parsed_number = phonenumbers.parse(phone_number, None)
        #     if not phonenumbers.is_valid_number(parsed_number):
        #         raise exceptions.ValidationError("Invalid phone number format")
        #     formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        #     return formatted_number
            
        # except phonenumbers.NumberParseException:
        #     raise exceptions.ValidationError("Invalid phone number format")
        # except:
        #     raise exceptions.ValidationError("Error Ocuured During The Validation of Phone Number")
            

from chat.types import AVATAR_CHOICES

class CreateProfileApiView(APIView):
    """
    API view  for user registration
    Args:
        APIView (class): A class from the Django Rest Framework for handling HTTP requests.
            This view extends the base APIView class to handle user registration.
    """
    serializer_class = CreateProfileSerializer

    def post(self, request):
        # Extract and validate data from the request 
        data, user = self._get_validated_data(request.data)
        # data.add(user)
        
        # Creates a new user instance
        serializer = self.serializer_class(user.profile, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.data)
        response = self._get_response(user)
        # Craft and return a response with appropriate status code
        return response
    
    def _get_validated_data(self, data):
        # Validate passwords and phone number presence
        data = self._validate_profile_avatar(data)
        self._validate_username(data)
        self._validate_about(data)
        user = self._get_registerd_user(data)
        return data , user
    
    def _validate_profile_avatar(self, data):
        # Ensure that password and confirm_password match
        mutable_data = data.copy()
        if "default_avatar" in data:
            path = AVATAR_CHOICES.get(mutable_data["default_avatar"])
            if path:
                mutable_data["default_avatar"] = path
        return mutable_data
    
    def _validate_about(self, data):
        # Ensure that email is present in the data
        if "about" not in data:
            raise exceptions.ValidationError("About is required")
        
    def _get_registerd_user(self, data):
        try:
            # Attempt to retrieve the user based on the provided ID
            user = User.objects.get(id=data['user'])
            # data['user'] = user.id  # Set the user field to the retrieved user instance
            return user
        except User.DoesNotExist:
            raise exceptions.ValidationError("User Not Found")
        except:
            raise exceptions.ValidationError("Error While Verifying User")
    
    def _validate_username(self, data):
        # Ensure that username is present in the data
        if "username" not in data:
            raise exceptions.ValidationError("Username is required")
                
    def _get_response(self, user):
        response = Response(status=status.HTTP_201_CREATED)
        serialized = LoginSerializer(user)
        response.data = serialized.data
        return response
    
class LoginApiView(APIView):
    """
    API view  for user login
    Args:
        APIView (class): A class from the Django Rest Framework for handling HTTP requests.
            This view extends the base APIView class to handle user login.
    """
    def post(self, request):
        
        user = self._get_validated_data(request.data)
        serializer = UserDetailsSerializer(user)
        data = serializer.data
        token = self._create_jwt_token(user, data)
        # response = self._set_httponly_cookie(data, token)
        response = self._add_jwt_token(data, token)
        
        return response
    
    def _get_validated_data(self, data):
        
        phone_number = self._validate_phone_nummber(data)
        password = data["password"]
        print(phone_number,password)
        user = User.objects.filter(phone_number=phone_number).first()
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("Invalid Credentials")
        
        return user
    
    def _validate_phone_nummber(self, data):
        # Ensure that phone_number is present in the data
        if "phone_number" not in data:
            raise exceptions.ValidationError("Phone number is required")
        phone_number = data.get("phone_number")
        return phone_number
        # try:
        #     parsed_number = phonenumbers.parse(phone_number, None)
        #     if not phonenumbers.is_valid_number(parsed_number):
        #         raise exceptions.ValidationError("Invalid phone number format")
        #     formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        #     return formatted_number
            
        # except phonenumbers.NumberParseException:
        #     raise exceptions.ValidationError("Invalid phone number format")
        # except Exception as e:
        #     print(e)
        #     raise exceptions.ValidationError("Error Ocuured During The Validation of Phone Number")
    
    def _create_jwt_token(self, user, data):
        
        access_token = create_access_token(data["id"])
        refresh_token = create_refresh_token(data["id"])
        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        )
        return [access_token, refresh_token]
    
    # Currently Not Using this Method 
    def _set_httponly_cookie(self, data, token):
        access_expiration, refresh_expiration = datetime.datetime.now() + datetime.timedelta(days=1), datetime.datetime.now() + datetime.timedelta(days=7)
        response = Response()
        response.set_cookie(key="refresh_token", value=token[1], httponly=True, secure=True , expires=refresh_expiration, samesite=False )
        response.set_cookie(key="access_token", value=token[0], httponly=True, secure=True, expires=access_expiration, samesite=False)
        response.data = data
        
        return response
    
    def _add_jwt_token(self, data, token):
        response = Response()
        data['access_token'], data['refresh_token'] = token[0], token[1]
        response.data = data
        return response
    
    
class LogOutAPIView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        
        # self._handle_token(request.COOKIES)
        response = self._handle_delete_cookie()
        return response
    
    def _handle_token(self, Cookies):
        
        refresh_token = Cookies.get("refresh_token")
        if refresh_token is None:
            raise exceptions.AuthenticationFailed("Invalid authorization token provided")
        try:
            UserToken.objects.filter(token=refresh_token).delete()
        except:
            raise exceptions.AuthenticationFailed("Invalid authorization token provided")
        
    def _handle_delete_cookie(self):
        
        response = Response(status=status.HTTP_204_NO_CONTENT)
        # response.delete_cookie(key="refresh_token")
        # response.delete_cookie(key="access_token")
        response.data = {"message": "User logged out"}
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


class RefreshAPIView(APIView):
    def post(self, request):
        is_admin = request.data["token"]
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
        data = {"access_token": access_token}
        response = Response(data=data, status=status.HTTP_200_OK)
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


