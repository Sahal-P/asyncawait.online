from rest_framework import serializers
from account.models import User
from account.serializers import UserByIdSerializer
from chat.models import UserProfile
from account.serializers import UUIDField


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["password", "phone_number"]
        extra_kwargs = {"password": {"write_only": True}}

class CreateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['id', 'last_seen', 'status', 'user', 'profile_picture', 'username', 'about']
        read_only_fields = ( "id", "last_seen", "status" )
        
    # def create(self, validated_data):
    #     # When creating a new profile, associate it with the user specified in the request
    #     user = self.context['user']
    #     print(user,'crr@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    #     profile = UserProfile.objects.create(user=user, **validated_data)
    #     return profile