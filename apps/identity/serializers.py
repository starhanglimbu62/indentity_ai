from rest_framework import serializers

from apps.identity.services.validation import DocumentValidationService

from .models import (
    IdentityDocument,
    VerifiableCredential,
)


class IdentityDocumentSerializer(
    serializers.ModelSerializer
):

    def validate_document_file(self, value):
        try:
            DocumentValidationService.validate_file(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value

    class Meta:
        model = IdentityDocument

        fields = [
            "id",
            "document_type",
            "document_file",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]


class CredentialSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = VerifiableCredential

        fields = [
            "id",
            "issuer",
            "issued_at",
            "expires_at",
            "is_active",
        ]

        read_only_fields = fields