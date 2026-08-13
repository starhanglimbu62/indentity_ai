from rest_framework import serializers

from .models import (
    IdentityDocument,
    VerifiableCredential,
)


class IdentityDocumentSerializer(
    serializers.ModelSerializer
):

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