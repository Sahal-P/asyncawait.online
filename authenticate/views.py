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
    verify_phone_number,
)
import json
import pyotp
from .service import compres_profile_picture
from chat.types import AVATAR_CHOICES




class RegisterApiView(APIView):
    """
    API view  for user registration
    Args:
        APIView (class): This view extends the base APIView class to handle user registration. Throttle limit 5 request per day
        Method: POST.
        data: {
            email: example@gmail.com,
            phone_number: 000 000 00 00,
            password: ********,
            confirm_password: ********,
        }
    """
    # throttle_classes = "register_rate"
    
    def post(self, request):
        # Extract and validate data from the request 
        try:
            data = self._get_validated_data(request.data)
            # Creates a new user instance
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            raise exceptions.APIException(f"UnKnown Error: {str(e)}")
        # Craft and return a response with appropriate status code
        # return Response(data=None, status=status.HTTP_201_CREATED)
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
        # verified_number = verify_phone_number(phone_number)
        return phone_number
            



class CreateProfileApiView(APIView):
    """
    API view for creating user profile
    Args:
        APIView (class): This view extends the base APIView class to handle profile creation.
        Method: POST.
        data: {
            profile_picture: InMemoryUploadedFile, (optional)
            default_avatar: AVATAR_CHOICE, (optional)
            username: example_123, (optional)
            about: hey there, (optional)
        }
        
    """
    serializer_class = CreateProfileSerializer

    def post(self, request):
        # Extract and validate data from the request 
        try:
            data, user = self._get_validated_data(request.data)
            # data.add(user)
            # Creates a new user instance
            serializer = self.serializer_class(user.profile, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = self._get_response(user)
        except Exception as e:
            raise exceptions.APIException(f"UnKnown Error: {str(e)}")
        # Craft and return a response with appropriate status code
        # return Response(data=None, status=status.HTTP_201_CREATED)
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
        if "profile_picture" in data:
            mutable_data = compres_profile_picture(mutable_data)
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
        APIView (class): This view extends the base APIView class to handle user login. Throttle limit 10 request per day
        Method: POST.
        data: {
            phone_number: 000 000 00 00,
            password: ********,
        }
    """
    # throttle_classes = "login_rate"
    def options(self, request):
        response = Response()
        response["Access-Control-Allow-Origin"] = "https://asyncawait.online"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-User-Identifier, Authorization"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    
    def post(self, request):
        print("@@@@@@@@ api called here @@@@@@@@@@@ 1")
        try:
            print("@@@@@@@@ api called here @@@@@@@@@@@ 2")
            user = self._get_validated_data(request.data)
            serializer = UserDetailsSerializer(user)
            data = serializer.data
            token = self._create_jwt_token(user, data)
            # response = self._set_httponly_cookie(data, token)
            response = self._add_jwt_token(data, token)
        except Exception as e:
            print(f"@@@@@@@@ api called here @@@@@@@@@@@ 3  {str(e)}")
            raise exceptions.APIException(f"UnKnown Error: {str(e)}")
        return response
    
    def _get_validated_data(self, data):
        
        phone_number = self._validate_phone_nummber(data)
        password = data["password"]
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
        # verified_number = verify_phone_number(phone_number)
        return phone_number
    
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
    """
    API view  for user logout
    Args:
        APIView (class): This view is to handle user logout. 
        Method: POST.
        data: {
            refresh_token: example buBGBUYBYg674#$#@Q#@%fvsaf@#RCRCTYITIV%^&#sasf$@#%$asfd#$%^^&DCGVGK,
        }
    """
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
    """
    API is under Development 
    status: Not ready
    
    """
    def post(self, request):
        id = request.data["digits"]
        user = User.objects.filter(pk=id)
        if not user:
            raise exceptions.AuthenticationFailed("Invalid Password")
        secret = user.tfa_secret if user.tfa_secret != "" else request.data["secret"]
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
    """
    API view  for user refresh token
    Args:
        APIView (class): This view is to handle user refresh token. 
        Method: POST.
        data: {
            token: example buBGBUYBYg674#$#@Q#@%fvsaf@#RCRCTYITIV%^&#sasf$@#%$asfd#$%^^&DCGVGK,
        }
    """
    def post(self, request):
        refresh_token = request.data["token"]
        id = decode_refresh_token(refresh_token)
        
        self._verify_token(id, refresh_token)
        access_token = create_access_token(id)
        response = self.get_response(access_token)
        return response
    
    def get_response(self, access_token):
        data = {"access_token": access_token}
        return Response(data=data, status=status.HTTP_200_OK)
    
    def _verify_token(self, id, refresh_token):
        try:
            if not UserToken.objects.filter(
                user_id=id,
                token=refresh_token,
                expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc),
            ).exists():
                raise exceptions.AuthenticationFailed("unauthenticated")
        except:
            raise exceptions.AuthenticationFailed("unauthenticated")



class ForgotAPIView(APIView):
    """
    API is under Development 
    status: Not ready
    
    """
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
    """
    API is under Development 
    status: Not ready
    
    """
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


