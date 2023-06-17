from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group, User
from rest_framework import exceptions
from django.db.models import Q


class IsSupportAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        return request.user.groups.filter(name='Support').exists() or request.user.is_superuser


def is_staff(user):
    return user.groups.filter(name='Support').exists() or user.is_superuser


class IsOrganizationAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        return request.user.groups.filter(name='OrganizationAdmin').exists()

class IsCourseAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        return request.user.groups.filter(name='CourseAdmin').exists()
