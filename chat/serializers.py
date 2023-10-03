from rest_framework import serializers
from account.serializers import UserSerializer, UUIDField, UserProfileDetailsSerializer
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
        fields = "__all__"
        read_only_fields = ("id", "created_at","last_activity_type","last_activity","unread_count","last_activity_time")


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

class ContactDetailsSerislizer(serializers.ModelSerializer):
    # id = serializers.UUIDField(write_only=True)
    contact_id = serializers.CharField()
    count = serializers.IntegerField()
    class Meta:
        model = Message
        fields = ("id","content","timestampe","status","is_read","contact_id", "count")
