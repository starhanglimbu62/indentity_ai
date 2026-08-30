from rest_framework import serializers

from .models import VerificationRequest


class VerifyProofSerializer(serializers.Serializer):
    proof = serializers.JSONField()
    publicSignals = serializers.JSONField()


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