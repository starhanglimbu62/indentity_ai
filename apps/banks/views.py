from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bank


class BankRegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        name = (request.data.get("name") or "").strip()
        bank_code = (request.data.get("bank_code") or "").strip()
        webhook_url = (request.data.get("webhook_url") or "").strip()

        if not name or not bank_code:
            return Response({"error": "name and bank_code are required."}, status=status.HTTP_400_BAD_REQUEST)

        if Bank.objects.filter(bank_code__iexact=bank_code).exists():
            return Response({"error": "A bank with this code already exists."}, status=status.HTTP_400_BAD_REQUEST)

        bank = Bank.objects.create(
            name=name,
            bank_code=bank_code,
            webhook_url=webhook_url or None,
        )

        return Response(
            {
                "id": str(bank.id),
                "name": bank.name,
                "bank_code": bank.bank_code,
                "api_key": bank.api_key,
                "webhook_url": bank.webhook_url,
                "is_active": bank.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class BankLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        bank_code = (request.data.get("bank_code") or "").strip()
        api_key = (request.data.get("api_key") or "").strip()

        if not bank_code or not api_key:
            return Response({"error": "bank_code and api_key are required."}, status=status.HTTP_400_BAD_REQUEST)

        bank = Bank.objects.filter(bank_code__iexact=bank_code, api_key=api_key, is_active=True).first()
        if not bank:
            return Response({"error": "Invalid bank credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "id": str(bank.id),
                "name": bank.name,
                "bank_code": bank.bank_code,
                "api_key": bank.api_key,
                "webhook_url": bank.webhook_url,
                "is_active": bank.is_active,
            },
            status=status.HTTP_200_OK,
        )
