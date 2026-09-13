from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1, write_only=True)


class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField()
    role = serializers.CharField()
