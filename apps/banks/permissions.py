from rest_framework.permissions import BasePermission

from apps.accounts.models import User

from .models import Bank


def get_authenticated_bank(request):
    if isinstance(request.user, Bank):
        return request.user if request.user.is_active else None

    user = request.user
    if isinstance(user, User) and user.is_authenticated and user.bank_id:
        bank = user.bank
        if bank.is_active:
            return bank
    return None


class IsBankPrincipal(BasePermission):
    def has_permission(self, request, view):
        return get_authenticated_bank(request) is not None
