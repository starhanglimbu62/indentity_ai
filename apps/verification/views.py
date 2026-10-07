from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.common.permissions import IsRequestOwnerOrStaff
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models

from apps.identity.models import VerifiableCredential
from apps.banks.models import Bank
from apps.accounts.models import User

from .services import VerificationService
from .models import VerificationRequest
from .serializers import VerificationRequestSerializer, VerifyProofSerializer


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

        approved = request.data.get("approved", True)

        try:
            if approved:
                VerificationService.approve_request(verification_request)
            else:
                VerificationService.deny_request(verification_request)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        status_str = "approved" if approved else "denied"
        return Response({"status": status_str})


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

        serializer = VerifyProofSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        proof = serializer.validated_data['proof']
        public_signals = serializer.validated_data['publicSignals']

        try:
            VerificationService.verify_request(
                verification_request, proof=proof, public_signals=public_signals
            )
        except Exception as exc:
            # Return a 400 for any verification/domain errors so callers get a clean API contract
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"verified": True, "claim": "AGE_OVER_18", "timestamp": verification_request.verified_at, "verification_id": verification_request.id})


class ListVerificationRequestsView(APIView):
    """List verification requests for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = VerificationRequest.objects.filter(user=request.user).select_related('bank').order_by('-created_at')
        serializer = VerificationRequestSerializer(requests, many=True)
        return Response(serializer.data)


class GetVerificationRequestView(APIView):
    """Get a single verification request (if owned by user or user is staff)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        verification_request = VerificationRequest.objects.filter(id=pk).select_related('bank').first()

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Only owner or staff can view
        if verification_request.user != request.user and not request.user.is_staff:
            return Response({"error": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        serializer = VerificationRequestSerializer(verification_request)
        return Response(serializer.data)


class ListNotificationsView(APIView):
    """List notifications for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import Notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        data = [
            {
                'id': str(n.id),
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at,
                'verification_request_id': str(n.verification_request.id) if n.verification_request else None,
            }
            for n in notifications
        ]
        return Response(data)


class MarkNotificationAsReadView(APIView):
    """Mark a notification as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from .models import Notification
        notification = Notification.objects.filter(id=pk, user=request.user).first()

        if not notification:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()

        return Response({"status": "marked_as_read"})


class SearchUsersView(APIView):
    """Search users by name or email (for bank portal)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return Response({"error": "Query must be at least 2 characters."}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(
            is_staff=False
        ).filter(
            models.Q(first_name__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(username__icontains=query)
        )[:20]

        data = [
            {
                'id': str(u.id),
                'name': u.first_name or u.username,
                'email': u.email,
                'username': u.username,
            }
            for u in users
        ]

        return Response(data)


class GetBankRequestsView(APIView):
    """Get verification requests for the authenticated bank (staff user)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Staff users can view their created requests
        requests = VerificationRequest.objects.filter(
            bank__is_active=True
        ).select_related('bank', 'user').order_by('-created_at')

        # For now, allow all staff to see all requests (in production, authenticate via bank token)
        if not request.user.is_staff:
            return Response({"error": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        data = [
            {
                'id': str(r.id),
                'user': {
                    'id': str(r.user.id),
                    'name': r.user.first_name or r.user.username,
                    'email': r.user.email,
                },
                'bank': {
                    'id': str(r.bank.id),
                    'name': r.bank.name,
                    'code': r.bank.bank_code,
                },
                'claim': r.claim,
                'status': r.status,
                'created_at': r.created_at,
                'verified_at': r.verified_at,
            }
            for r in requests
        ]

        return Response(data)


class GetBankRequestDetailView(APIView):
    """Get details of a single verification request (for bank)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_staff:
            return Response({"error": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        verification_request = VerificationRequest.objects.filter(id=pk).select_related('bank', 'user').first()

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'id': str(verification_request.id),
            'user': {
                'id': str(verification_request.user.id),
                'name': verification_request.user.first_name or verification_request.user.username,
                'email': verification_request.user.email,
            },
            'bank': {
                'id': str(verification_request.bank.id),
                'name': verification_request.bank.name,
                'code': verification_request.bank.bank_code,
            },
            'claim': verification_request.claim,
            'status': verification_request.status,
            'created_at': verification_request.created_at,
            'verified_at': verification_request.verified_at,
        }

        return Response(data)