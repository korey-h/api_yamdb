from rest_framework import permissions

from .models import Roles


class IsOwnerOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == Roles.ADMIN
            or request.user.role == Roles.MODERATOR
        )


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == Roles.ADMIN or request.user.is_staff

    def has_permission(self, request, view):
        return request.user.role == Roles.ADMIN or request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user.role == Roles.ADMIN
        )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user.role == Roles.ADMIN
        )
