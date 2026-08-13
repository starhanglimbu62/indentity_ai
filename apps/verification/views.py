from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import VerifiableCredential
from apps.banks.models import Bank

from .services import VerificationService
from .models import VerificationRequest
from .serializers import VerificationRequestSerializer


class CreateVerificationRequestView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        bank_code = request.data.get(
            "bank_code"
        )

        user_id = request.data.get(
            "user_id"
        )

        claim = request.data.get(
            "claim"
        )

        if not all([
            bank_code,
            user_id,
            claim,
        ]):
            return Response(
                {
                    "error": "bank_code, user_id and claim are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            bank = Bank.objects.get(
                bank_code=bank_code,
                is_active=True
            )

            credential = (
                VerifiableCredential.objects
                .filter(
                    user_id=user_id,
                    is_active=True
                )
                .first()
            )

            if not credential:
                return Response(
                    {
                        "error":
                        "No active credential exists."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            verification_request = (
                VerificationService.create_request(
                    bank=bank,
                    user=credential.user,
                    credential=credential,
                    claim=claim,
                )
            )

            return Response(
                VerificationRequestSerializer(
                    verification_request
                ).data,
                status=status.HTTP_201_CREATED
            )

        except Bank.DoesNotExist:

            return Response(
                {
                    "error": "Bank not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ConsentView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        verification_request = (
            VerificationRequest.objects
            .filter(
                id=pk,
                user=request.user
            )
            .first()
        )

        if not verification_request:

            return Response(
                {
                    "error":
                    "Verification request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            VerificationService.approve_request(
                verification_request
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "status": "approved"
        })


class VerifyRequestView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        verification_request = (
            VerificationRequest.objects
            .filter(id=pk)
            .select_related("bank")
            .first()
        )

        if not verification_request:

            return Response(
                {
                    "error": "Request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            VerificationService.verify_request(
                verification_request
            )

        except ValueError as exc:

            return Response(
                {
                    "error": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "verified": True,
            "timestamp":
                verification_request.verified_at,
            "verification_id":
                verification_request.id,
        })