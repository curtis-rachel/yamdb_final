from rest_framework import permissions
from reviews.models import Role


class IsAdmin(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.role == Role.ADMIN or request.user.is_superuser)


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (request.method
                in permissions.SAFE_METHODS
                or (user.is_authenticated
                    and (user.is_admin or user.is_superuser))
                )
