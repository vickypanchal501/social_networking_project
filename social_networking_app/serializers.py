from rest_framework import serializers

from django.core.validators import EmailValidator

from .models import FriendRequest, Friend, CustomUser
from django.contrib.auth import authenticate

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']  # Include confirm_password field

    def validate(self, data):
        if data['password'] != data.pop('confirm_password', None):  # Use dict.get to safely pop confirm_password
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)  # Remove confirm_password if exists
        user = CustomUser.objects.create_user(**validated_data)
        return user

    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        data['user'] = user
        return data

class FriendRequestSerializer(serializers.ModelSerializer):
    to_user = serializers.EmailField()

    class Meta:
        model = FriendRequest
        fields = ['to_user']

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'
