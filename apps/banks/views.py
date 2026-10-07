from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .authentication import BankAPIKeyAuthentication
from .permissions import IsBankPrincipal, get_authenticated_bank
from .serializers import BankLoginSerializer, BankProvisionSerializer
from .services import BankCredentialService


class BankRegisterView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BankProvisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            bank, api_key = BankCredentialService.provision_bank(
                **serializer.validated_data
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": str(bank.id),
                "name": bank.name,
                "bank_code": bank.bank_code,
                "webhook_url": bank.webhook_url,
                "is_active": bank.is_active,
                "api_key": api_key,
            },
            status=status.HTTP_201_CREATED,
        )


class BankLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BankLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank = BankCredentialService.authenticate(
            **serializer.validated_data
        )
        if not bank:
            return Response(
                {"error": "Invalid bank credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "id": str(bank.id),
                "name": bank.name,
                "bank_code": bank.bank_code,
            },
            status=status.HTTP_200_OK,
        )


class BankGetInfoView(APIView):
    authentication_classes = [BankAPIKeyAuthentication, JWTAuthentication]
    permission_classes = [IsBankPrincipal]

    def get(self, request):
        bank = get_authenticated_bank(request)
        return Response({
            "id": str(bank.id),
            "name": bank.name,
            "bank_code": bank.bank_code,
            "is_active": bank.is_active,
        })
