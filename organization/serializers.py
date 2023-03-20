from rest_framework import serializers
from .models import *


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        queryset = Organization.objects.all()
        model = Organization
        fields = ['name']
