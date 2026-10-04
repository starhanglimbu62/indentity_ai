from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    legal_name = serializers.CharField(
        source="first_name",
        write_only=True,
        required=True,
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={
            "input_type": "password"
        },
    )

    email = serializers.EmailField(
        required=True
    )

    class Meta:
        model = User

        fields = [
            "legal_name",
            "username",
            "email",
            "password",
            "phone_number",
        ]

        extra_kwargs = {
            "username": {
                "required": True,
            },
        }

    def validate_username(self, value):
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must contain at least 3 characters."
            )

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this username already exists."
            )

        return value

    def validate_legal_name(self, value):
        value = " ".join(value.split())

        if not value:
            raise serializers.ValidationError(
                "Legal name is required."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_phone_number(self, value):
        if not value:
            return value

        value = value.strip()

        return value

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )