from django.db.models import Model
from rest_framework import permissions, views
from rest_framework.request import Request


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: views.APIView) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request: Request, view: views.APIView,
                              obj: Model) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_moderator or obj.author.id == request.user.id
