from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.banks.authentication import BankAPIKeyAuthentication
from apps.banks.permissions import IsBankPrincipal, get_authenticated_bank
from apps.identity.models import CredentialStatus, VerifiableCredential
from apps.accounts.models import User
from apps.common.exceptions import InvalidStateTransition

from .services import VerificationService
from .models import VerificationRequest
from .serializers import (
    ConsentDecisionSerializer,
    VerificationRequestCreateSerializer,
    VerificationRequestSerializer,
    VerifyProofSerializer,
)


class CreateVerificationRequestView(APIView):
    """
    Bank-initiated creation of a verification request.

    Security: Only staff users (representing banks) are allowed to create
    verification requests via this endpoint. The caller must supply bank_code
    and user_id of the subject. Non-staff users are NOT allowed to create
    arbitrary bank requests here.
    """

    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def post(self, request):
        serializer = VerificationRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank = get_authenticated_bank(request)
        supplied_bank_code = serializer.validated_data.get("bank_code")
        if supplied_bank_code and supplied_bank_code.casefold() != bank.bank_code.casefold():
            return Response({"error": "Bank identity does not match credentials."}, status=status.HTTP_403_FORBIDDEN)

        try:
            target_user = User.objects.get(pk=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        credential = (
            VerifiableCredential.objects.filter(
                user=target_user,
                status=CredentialStatus.ACTIVE,
                is_active=True,
            )
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
            .order_by("-issued_at")
            .first()
        )

        if not credential:
            return Response({"error": "No active credential exists for the user."}, status=status.HTTP_404_NOT_FOUND)

        try:
            verification_request = VerificationService.create_request(
                bank=bank,
                user=target_user,
                credential=credential,
                claim=serializer.validated_data["claim"],
            )
        except InvalidStateTransition as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(VerificationRequestSerializer(verification_request).data, status=status.HTTP_201_CREATED)


class RequestChallengeView(APIView):

    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def post(self, request, pk):
        """Generate and return a challenge bound to the verification request.

        Only staff users (representing banks) may generate a challenge for a
        verification request. The holder still must approve (consent) before
        verification is accepted.
        """
        bank = get_authenticated_bank(request)
        verification_request = VerificationRequest.objects.filter(
            id=pk,
            bank=bank,
        ).select_related("credential").first()

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            token, expires_at = VerificationService.issue_challenge(
                verification_request
            )
        except InvalidStateTransition as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'challenge': token, 'expires_at': expires_at})


class ConsentView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):
        serializer = ConsentDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification_request = (
            VerificationRequest.objects.filter(id=pk, user=request.user).first()
        )

        if not verification_request:
            return Response({"error": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        approved = serializer.validated_data["approved"]

        try:
            if approved:
                VerificationService.approve_request(verification_request)
            else:
                VerificationService.deny_request(verification_request)
        except InvalidStateTransition as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        status_str = "approved" if approved else "denied"
        return Response({"status": status_str})


class VerifyRequestView(APIView):

    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def post(self, request, pk):
        bank = get_authenticated_bank(request)
        verification_request = (
            VerificationRequest.objects.filter(id=pk, bank=bank)
            .select_related("bank")
            .first()
        )

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VerifyProofSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        proof = serializer.validated_data['proof']
        public_signals = serializer.validated_data['publicSignals']

        try:
            verification_request = VerificationService.verify_request(
                verification_request, proof=proof, public_signals=public_signals
            )
        except (InvalidStateTransition, ValueError) as exc:
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
    """Search bank-visible user matches and return only opaque IDs."""

    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

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
            }
            for u in users
        ]

        return Response(data)


class GetBankRequestsView(APIView):
    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def get(self, request):
        bank = get_authenticated_bank(request)
        requests = VerificationRequest.objects.filter(
            bank=bank,
        ).order_by('-created_at')

        data = [
            {
                'id': str(r.id),
                'claim': r.claim,
                'status': r.status,
                'created_at': r.created_at,
                'verified_at': r.verified_at,
            }
            for r in requests
        ]

        return Response(data)


class GetBankRequestDetailView(APIView):
    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def get(self, request, pk):
        bank = get_authenticated_bank(request)
        verification_request = VerificationRequest.objects.filter(
            id=pk,
            bank=bank,
        ).first()

        if not verification_request:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'id': str(verification_request.id),
            'claim': verification_request.claim,
            'status': verification_request.status,
            'created_at': verification_request.created_at,
            'verified_at': verification_request.verified_at,
        }

        return Response(data)