from django.contrib.auth import get_user_model
from django.core.cache import caches
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
cache = caches["blacklist"]


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name")


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
        )


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        data = {"refresh": str(refresh)}
        return data


class TokenRefreshSerializerWithBlacklist(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])

        token_in_cache = cache.get(refresh)

        if token_in_cache:
            raise ValidationError("Token is blacklisted")

        data = {"access": str(refresh.access_token)}

        return data


class UserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "phone_number",
            "last_name",
            "email",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
        )

