from django.shortcuts import render
from rest_framework import generics, status, views, permissions, exceptions
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User


class UserAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        user = User.objects.all().first()
        serializer = self.serializer_class(user)
        data = serializer.data
        return Response(status=status.HTTP_200_OK, data=data)
        
class FriendsAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer
    
    def get(self, request):
        friends = User.objects.filter(is_superuser=False)
        print(friends)
        serializer = self.serializer_class(friends, many=True)
        print(serializer)
        data = serializer.data
        return Response(status=status.HTTP_200_OK, data=data)

class RegisterAPIView(generics.GenericAPIView):
    
    serializer_class = UserSerializer

    def post(self, request):
        user = request.data
        if user["password"] != user["confirm_password"]:
            raise exceptions.APIException('Password do not match')
        
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        return Response(user_data, status=status.HTTP_201_CREATED)