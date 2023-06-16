from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
    
#     def create(self, validated_data):
#         instance = self.Meta.model.objects.create_user(**validated_data)
#         return instance
    
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'password', 'username', 'phone_number']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","password","username","phone_number"]
        extra_kwargs = {'password':{'write_only':True}}
        
    def create(self,validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance
 