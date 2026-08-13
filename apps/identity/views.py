from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IdentityDocument
from .serializers import IdentityDocumentSerializer
from .services import IdentityService


class IdentityDocumentUploadView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = IdentityDocumentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        document = serializer.save(
            user=request.user
        )

        try:

            credential = IdentityService.process_document(
                document
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "status": "verified",
                "credential_id": credential.id
            },
            status=status.HTTP_201_CREATED
        )