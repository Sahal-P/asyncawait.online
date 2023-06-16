from rest_framework import generics, status, views, permissions, exceptions
from rest_framework.response import Response

# Create your views here.
class ChatAPIView(generics.GenericAPIView):
    def get(self, request):
        return Response