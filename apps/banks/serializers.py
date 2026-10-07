from rest_framework import serializers

from .models import Bank


class BankProvisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ("name", "bank_code", "webhook_url")

    def validate_bank_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Bank code is required.")
        if Bank.objects.filter(bank_code__iexact=value).exists():
            raise serializers.ValidationError(
                "A bank with this code already exists."
            )
        return value

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Bank name is required.")
        return value


class BankLoginSerializer(serializers.Serializer):
    bank_code = serializers.CharField(max_length=50)
    api_key = serializers.CharField(write_only=True, trim_whitespace=False)
