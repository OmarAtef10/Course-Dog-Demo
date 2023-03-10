from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group, User
from rest_framework import exceptions
from django.db.models import Q


class IsOrganizationAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        curr_user = request.user
        return curr_user.groups.filter(Q(name='OrganizationAdmin') | Q(name='Admin')).exists() or curr_user.is_superuser


def is_organization_admin(user):
    return user.groups.filter(Q(name='OrganizationAdmin') | Q(name='Admin')).exists() or user.is_superuser
