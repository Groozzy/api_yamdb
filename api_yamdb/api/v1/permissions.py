from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права доступа для админа."""
    # def has_permission(self, request, view):
    #     if request.method in permissions.SAFE_METHODS:
    #         return True

    #     if request.user.is_authenticated:
    #         return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        return False
