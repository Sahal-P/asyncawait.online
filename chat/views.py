import logging
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
from django.db import transaction

logger = logging.getLogger(__name__)

class MessageUnknownAPIView(views.APIView):
    """
    API view for sending a message to an unknown user.

    This view handles the scenario where a user wants to send a message to another user
    who is not yet in their contacts. It creates a new chat between the requesting user
    and the unknown user, and also adds them to each other's contacts.

    Attributes:
        authentication_classes (list): List of authentication classes applied to this view.

    Returns:
        Response: A response with a serialized contact objects and a status code 200.
    """
    
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        
        data = self._validate_data(request.data)
        user = request.user
        second_user = self._get_requested_user(data["id"])
        self._validate_chat_participants(user, second_user)
        data = self._create_chat(user, second_user)
        return Response(data=data, status=status.HTTP_200_OK)
    
    def _validate_data(self, data):
        serialized_data = MessageUnknownSerializer(data=data)
        serialized_data.is_valid(raise_exception=True)
        return serialized_data.data
    
    def _get_requested_user(self, id):
        # The user that request for an Unknown connection 
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise exceptions.NotFound("Requested user not found.")
    
    def _validate_chat_participants(self, user, unknown_user):
        chat = (
            Chat.objects.filter(participants=user, is_group_chat=False)
            .filter(participants=unknown_user)
            .exists()
        )
        if chat:
            raise exceptions.APIException("participents already exits")
    
    def _create_chat(self, user, second_user):
        try:
            # Used Django transaction to ensure atomicity
            with transaction.atomic():
                chat = Chat.objects.create(is_group_chat=False)
                chat.participants.add(user)
                chat.participants.add(second_user)
                chat.full_clean()
                chat.save()
                return self._get_contacts(user, second_user)
        except Exception as e:
            # Handle the exception as needed
            raise exceptions.APIException(f"Error Creating Chat: {str(e)}")
        
    def _get_contacts(self, user, second_user):
        print('first here--------------------',second_user.profile.id)
        
        contact = Contacts.objects.create(
            user=user, contact=second_user, is_accepted=True
        )
        print('then here--------------------')
        
        serialized_data = ContactsSerializer(contact)
        return serialized_data.data
        
        
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
        logger.critical("Error Login user with params: dhfbvjdbdjfbv")
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
