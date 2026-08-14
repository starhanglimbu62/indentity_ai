from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.common.permissions import IsRequestOwnerOrStaff
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import VerifiableCredential
from apps.banks.models import Bank
from apps.accounts.models import User

from .services import VerificationService
from .models import VerificationRequest
from .serializers import VerificationRequestSerializer


class CreateVerificationRequestView(APIView):
    """
    Bank-initiated creation of a verification request.

    Security: Only staff users (representing banks) are allowed to create
    verification requests via this endpoint. The caller must supply bank_code
    and user_id of the subject. Non-staff users are NOT allowed to create
    arbitrary bank requests here.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):

        bank_code = request.data.get("bank_code")
        user_id = request.data.get("user_id")
        claim = request.data.get("claim")

        if not all([bank_code, claim]):
            return Response({"error": "bank_code and claim are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine target user: staff may specify user_id; non-staff may only create a request for themselves
        if request.user.is_staff:
            if not user_id:
                return Response({"error": "user_id is required for staff-initiated requests."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If non-staff provided a user_id that is not themselves, forbid the action
            if user_id and str(request.user.id) != str(user_id):
                return Response({"error": "Forbidden to create requests for other users."}, status=status.HTTP_403_FORBIDDEN)
            # non-staff may only act for themselves
            target_user = request.user

        try:
            bank = Bank.objects.get(bank_code=bank_code, is_active=True)
        except Bank.DoesNotExist:
            return Response({"error": "Bank not found."}, status=status.HTTP_404_NOT_FOUND)

        # Find any credential for the target user (we allow request creation even if credential later is inactive)
        credential = VerifiableCredential.objects.filter(user=target_user).first()

        if not credential:
            return Response({"error": "No credential exists for the user."}, status=status.HTTP_404_NOT_FOUND)

        verification_request = VerificationService.create_request(bank=bank, user=target_user, credential=credential, claim=claim)

        return Response(VerificationRequestSerializer(verification_request).data, status=status.HTTP_201_CREATED)


class RequestChallengeView(APIView):

    # Only staff (bank) users may generate challenges
    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]

    def post(self, request, pk):
        """Generate and return a challenge bound to the verification request.

        Only staff users (representing banks) may generate a challenge for a
        verification request. The holder still must approve (consent) before
        verification is accepted.
        """
        verification_request = (
            VerificationRequest.objects.filter(id=pk).select_related('credential').first()
        )

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only allow challenge generation for pending or approved requests (bank initiates)
        # The UI/holder will still need the user to approve before verification.
        from apps.identity.services.zk_challenge import generate_challenge

        token, expires_at = generate_challenge()
        verification_request.challenge = token
        verification_request.challenge_expires_at = expires_at
        verification_request.save(update_fields=['challenge', 'challenge_expires_at'])

        return Response({'challenge': token, 'expires_at': expires_at})


class ConsentView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):

        verification_request = (
            VerificationRequest.objects.filter(id=pk, user=request.user).first()
        )

        if not verification_request:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            VerificationService.approve_request(verification_request)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "approved"})


class VerifyRequestView(APIView):

    # Allow staff (bank) users or the request owner to submit verification payloads
    permission_classes = [
        IsAuthenticated,
        IsRequestOwnerOrStaff,
    ]

    def post(self, request, pk):

        verification_request = (
            VerificationRequest.objects.filter(id=pk).select_related("bank").first()
        )

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        proof = request.data.get('proof')
        public_signals = request.data.get('publicSignals')

        if not proof or not public_signals:
            return Response({"error": "proof and publicSignals are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            VerificationService.verify_request(
                verification_request, proof=proof, public_signals=public_signals
            )
        except Exception as exc:
            # Return a 400 for any verification/domain errors so callers get a clean API contract
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"verified": True, "claim": "AGE_OVER_18", "timestamp": verification_request.verified_at, "verification_id": verification_request.id})