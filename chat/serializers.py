from rest_framework import serializers
from account.serializers import UserSerializer, UUIDField
from account.models import User
from .models import Chat, Contacts, Message


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ("id", "participants", "is_group_chat")


class ContactsSerializer(serializers.ModelSerializer):
    contact = UserSerializer(read_only=True)

    class Meta:
        model = Contacts
        fields = (
            "id",
            "user",
            "contact",
            "is_favorite",
            "is_accepted",
            "is_blocked",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class MessageUnknownSerializer(serializers.ModelSerializer):
    id = UUIDField()

    class Meta:
        model = User
        fields = ("id",)


class GetChatDetailsSerializer(serializers.ModelSerializer):
    id = UUIDField()

    class Meta:
        model = Chat
        fields = ("id",)


class MessageDetailsSerislizer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("id",)
