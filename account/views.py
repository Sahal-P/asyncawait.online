from django.shortcuts import render
from rest_framework import generics, status, views, permissions, exceptions
from .serializers import UserSerializer
from rest_framework.response import Response
from .models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers




class UsersAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer

    # @method_decorator(cache_page(60 * 60))
    # @method_decorator(vary_on_headers("X-User-Identifier"))
    def get(self, request):
        
        friends = User.objects.filter(is_superuser=False)
        serializer = self.serializer_class(friends, many=True)
        data = serializer.data
        return Response(status=status.HTTP_200_OK, data=data)



