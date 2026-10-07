from rest_framework import serializers

from apps.banks.models import Bank
from apps.identity.services.zk_claims import CLAIM_AGE_OVER_18

from .models import VerificationRequest


class VerificationRequestCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    claim = serializers.ChoiceField(choices=(CLAIM_AGE_OVER_18,))
    bank_code = serializers.CharField(max_length=50, required=False)


class ConsentDecisionSerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)


class BankSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ("name", "bank_code")
        read_only_fields = fields


class VerifyProofSerializer(serializers.Serializer):
    proof = serializers.JSONField()
    publicSignals = serializers.JSONField()


class VerificationRequestSerializer(
    serializers.ModelSerializer
):
    bank = BankSummarySerializer(read_only=True)

    class Meta:
        model = VerificationRequest

        fields = [
            "id",
            "bank",
            "claim",
            "status",
            "created_at",
            "user_consented_at",
            "verified_at",
        ]

        read_only_fields = fields