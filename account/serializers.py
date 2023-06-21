from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from uuid import UUID


class UUIDField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, UUID):
            return str(value)
        return value

    def to_internal_value(self, data):
        try:
            return UUID(data)
        except ValueError:
            raise serializers.ValidationError("Invalid UUID Format")
        except:
            raise Exception("somthing went wrong with uuid field")


class UserSerializer(serializers.ModelSerializer):
    id = UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "username", "phone_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        instance = self.Meta.model.objects.create_user(**validated_data)
        return instance
