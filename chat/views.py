from rest_framework import generics, status, views, permissions, exceptions
from rest_framework.response import Response
from account.models import User
from authenticate.authenticate import JWTAuthentication
from .models import Chat, Contacts, Message, UserProfile
from django.db import models
from .serializers import (
    ChatSerializer,
    ContactsSerializer,
    MessageUnknownSerializer,
    GetChatDetailsSerializer,
    MessageDetailsSerislizer,
)
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers


# Create your views here.
class ChatAPIView(generics.GenericAPIView):
    def get(self, request):
        return Response


class MessageUnknownAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serialized_data = MessageUnknownSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        data = serialized_data.data
        user = User.objects.get(id=request.user.id)
        second_user = User.objects.get(id=data["id"])
        chat = (
            Chat.objects.filter(participants=user, is_group_chat=False)
            .filter(participants=second_user)
            .exists()
        )
        if chat:
            raise exceptions.APIException("participents already exits")
        chat = Chat.objects.create(is_group_chat=False)
        chat.participants.add(user)
        chat.participants.add(second_user)
        chat.full_clean()
        chat.save()
        contact = Contacts.objects.create(
            user=user, contact=second_user, is_accepted=True
        )
        serialized_data = ContactsSerializer(contact)
        return Response(status=status.HTTP_200_OK, data=serialized_data.data)


class GetChatIDAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        user = User.objects.get(id=request.user.id)
        second_user = User.objects.get(id=int(data["user_id"]))
        # chat = Chat.objects.annotate(participant_count=models.Count('participants')).filter(participant_count=2,participants=user,participants__in=[second_user]).first()
        chat = Chat.objects.filter(
            participants__in=[user, second_user], is_group_chat=False
        ).first()
        serialized_data = ChatSerializer(chat)
        return Response(status=status.HTTP_200_OK, data=serialized_data.data)


class GetContactsAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]
    
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    # @method_decorator(cache_page(60 * 60))
    # @method_decorator(vary_on_headers("X-User-Identifier"))
    def get(self, request):
        user = request.user
        contacts = Contacts.objects.filter(user=user)
        contact_serializer = ContactsSerializer(contacts, many=True)
        return Response(status=status.HTTP_200_OK, data=contact_serializer.data)


class GetChatDetailsAPIView(views.APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serialized_data = GetChatDetailsSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        data = serialized_data.data
        user = request.user
        chat_user = User.objects.get(id=data["id"])
        chat = (
            Chat.objects.filter(participants=user, is_group_chat=False)
            .filter(participants=chat_user)
            .first()
        )
        message = Message.objects.filter(chat=chat).order_by("timestampe")
        message_serialized_data = MessageDetailsSerislizer(message, many=True)
        serialized_data = ChatSerializer(chat)
        data = {"chat": serialized_data.data, "message": message_serialized_data.data}
        return Response(status=status.HTTP_200_OK, data=data)
