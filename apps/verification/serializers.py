from rest_framework import serializers

from .models import VerificationRequest


class VerificationRequestSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = VerificationRequest

        fields = [
            "id",
            "claim",
            "status",
            "created_at",
            "user_consented_at",
            "verified_at",
        ]

        read_only_fields = fields