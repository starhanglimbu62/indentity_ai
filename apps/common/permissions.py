from rest_framework.permissions import BasePermission


class IsRequestOwnerOrStaff(BasePermission):
    """Allow access if the user is the request owner (obj.user) or is staff.

    Designed for VerificationRequest-protected endpoints where bank actions are
    performed by staff accounts and consent must be given by the request owner.
    """

    def has_object_permission(self, request, view, obj):
        # obj is expected to be a model instance with a 'user' attribute
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        # fallback: owner
        return getattr(obj, "user", None) == user


class IsOwner(BasePermission):
    """Generic object-level owner check: obj.user == request.user"""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(obj, "user", None) == user
