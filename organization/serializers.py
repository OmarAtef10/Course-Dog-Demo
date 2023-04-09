from rest_framework import serializers
from .models import *


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        queryset = Organization.objects.all()
        model = Organization
        fields = ['name']


class OrganizationFullSerializer(serializers.ModelSerializer):
    class Meta:
        queryset = Organization.objects.all()
        model = Organization
        fields = ['name', 'faculty_name', 'organization_name']


class SubdomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSubdomain
        fields = ['subdomain']
