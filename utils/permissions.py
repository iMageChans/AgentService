# permissions.py
from rest_framework import permissions

class IsAuthenticatedExternal(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.remote_user)