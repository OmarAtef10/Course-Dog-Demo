from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import rest_framework.status as status

from .serializers import *
from .models import *


# Create your views here.

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
