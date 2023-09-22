from django.shortcuts import render
from rest_framework import generics, status, views, permissions, exceptions
from .serializers import UserSerializer, UserProfileDetailsSerializer, UserProfile
from rest_framework.response import Response

from .models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from authenticate.authenticate import JWTAuthentication




class UsersAPIView(generics.GenericAPIView):
    """
    API view for retrieving a list of users.

    This view returns a list of all users who are not superusers.
    
    Attributes:
        serializer_class (Serializer): The serializer class for user data.

    Methods:
        get(request): Handles the GET request for retrieving user data.
    """
    
    authentication_classes = [JWTAuthentication]
    serializer_class = UserProfileDetailsSerializer
    
    @method_decorator(cache_page(60 * 15, key_prefix="UsersAPIVIEW"))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):
        
        users = self._get_users(request.user.id)
        serialized_data = self.serialize_users(users)
        data = serialized_data
        return Response(status=status.HTTP_200_OK, data=data)


    def _get_users(self, user_id):
        """
        Retrieve a list of users who are not superusers.

        Returns:
            QuerySet: A queryset of non-superuser users.
        """
        return UserProfile.objects.all().exclude(user= user_id)

    def serialize_users(self, users):
        """
        Serialize a list of users.

        Args:
            users (QuerySet): A queryset of user instances.

        Returns:
            dict: Serialized user data.
        """
        serializer = self.serializer_class(users, many=True)
        return serializer.data
