from django.shortcuts import render, get_object_or_404
from organization.models import Organization
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from .serializers import *
from .models import *
from django.http import JsonResponse


# Create your views here.

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = AnnouncementSerializer

    def list(self, request, *args, **kwargs):
        queryset = Announcement.objects.all()
        serializer = AnnouncementSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def add_announcement(request):
    try:
        org_name = request.data['org_name']
        organization = get_object_or_404(Organization, name=org_name)
        course_code = request.data['course_code']
        announcement = request.data['announcement']
        course = Course.objects.get(code=course_code)
        if course.organization == organization:
            announcement = Announcement.objects.create(course=course, announcement=announcement)
            announcement.save()
            return Response({'message': 'Announcement created successfully'}, status=HTTP_201_CREATED)
        else:
            return Response({'message': f'Course not found for {org_name} organization'}, status=HTTP_404_NOT_FOUND)

    except:
        return Response({"error": True, 'message': 'Course does not exist'}, status=HTTP_404_NOT_FOUND)
