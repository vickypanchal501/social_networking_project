from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, Friend, FriendRequest


class UserSignupSerializer(serializers.ModelSerializer):
    # Serializer for user signup
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "password", "confirm_password"]

    def validate(self, data):
        # Validate that password and confirm_password match
        if data["password"] != data.pop("confirm_password", None):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Create a new user
        validated_data.pop(
            "confirm_password", None
        )  # Remove confirm_password if exists
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    # Serializer for user login
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        # Validate email and password
        email = data.get("email")
        password = data.get("password")

        if email and password:
            # authenticate user
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        data["user"] = user
        return data


class FriendRequestSerializer(serializers.ModelSerializer):
    # Serializer for friend requests
    to_user = serializers.EmailField()

    class Meta:
        model = FriendRequest
        fields = ["to_user"]


class FriendSerializer(serializers.ModelSerializer):
    # Serializer for friends
    class Meta:
        model = Friend
        fields = "__all__"
