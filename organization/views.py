from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from user_profile.models import Profile
from authentication.serializers import UserSerializer
# Create your views here.
# CourseAdmin - OrganizationAdmin - Student


class OrganizationViewSet(GenericAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('name')

    def get(self, request, *args, **kwargs):
        queryset = Organization.objects.all()
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_organization(request, name):
    organization = get_object_or_404(Organization, name=name)
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationAPIView(GenericAPIView):
    serializer_class = OrganizationFullSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = get_object_or_404(Profile, user=request.user)
        organization = get_object_or_404(
            Organization, name=user_profile.organization.name)
        subdomains = OrganizationSubdomain.objects.filter(
            organization=organization)

        serialized_organization = self.get_serializer(organization).data
        serialized_subdomains = SubdomainSerializer(subdomains, many=True).data

        return Response({'organization_info': serialized_organization, 'subdomains': serialized_subdomains}, status=status.HTTP_200_OK)


class OrganizationAdminsDataAPIView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = get_object_or_404(Profile, user=request.user)
        organization = get_object_or_404(
            Organization, name=user_profile.organization.name)
        organization_admins = UserOrganizationAdmin.objects.filter(
            organization=organization)
        users = [
            organization_admin.user for organization_admin in organization_admins]

        serialized_users = self.get_serializer(users, many=True)
        return Response(serialized_users.data, status=status.HTTP_200_OK)
