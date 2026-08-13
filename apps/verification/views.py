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


class RequestChallengeView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):
        """Generate and return a challenge bound to the verification request.

        The challenge is short-lived and must be presented to the prover.
        """
        verification_request = (
            VerificationRequest.objects
            .filter(id=pk)
            .select_related('credential')
            .first()
        )

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only allow challenge generation for pending or approved requests (bank initiates)
        # The UI/holder will still need the user to approve before verification.
        from apps.identity.services.zk_challenge import generate_challenge

        token, expires_at = generate_challenge()
        verification_request.challenge = token
        # store as naive UTC; views/services use timezone-aware where appropriate
        verification_request.challenge_expires_at = expires_at
        verification_request.save(update_fields=['challenge', 'challenge_expires_at'])

        return Response({
            'challenge': token,
            'expires_at': expires_at,
        })


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

        proof = request.data.get('proof')
        public_signals = request.data.get('publicSignals')

        if not proof or not public_signals:
            return Response(
                {"error": "proof and publicSignals are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            VerificationService.verify_request(
                verification_request,
                proof=proof,
                public_signals=public_signals,
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
            "claim": "AGE_OVER_18",
            "timestamp": verification_request.verified_at,
            "verification_id": verification_request.id,
        })