from django.shortcuts import render, get_object_or_404
from organization.models import Organization
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import *
from .models import *
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from .models import *
from user_profile.views import get_user_profile
from organization.models import *
from material.models import Material
from material.serializers import MaterialSerializer
from course.models import *

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


class UploadCourseAnnouncementAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnnouncementFullSerializer

    def get(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        course = get_object_or_404(
            Course, id=course_id, organization=user_organization)

        announcements = Announcement.objects.filter(course=course)
        serialized_announcements = self.get_serializer(announcements, many=True)
        serialized_course = CourseSerializer(course)
        return Response({"announcement": serialized_announcements.data, "course":serialized_course.data}, 200)

    def post(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        course = get_object_or_404(
            Course, id=course_id, organization=user_organization)

        try:
            is_course_admin = UserCourseAdmin.objects.get(
                course=course, user=user)
        except UserCourseAdmin.DoesNotExist:
            return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

        announcementData = self.get_serializer(data=request.data)
        if announcementData.is_valid():
            announcement = Announcement(course=course, announcement = announcementData.validated_data['announcement'])
            announcement.save()
        return Response({}, 200)
    
    
    def put(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        course = get_object_or_404(
            Course, id=course_id, organization=user_organization)

        try:
            is_course_admin = UserCourseAdmin.objects.get(
                course=course, user=user)
        except UserCourseAdmin.DoesNotExist:
            return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

        announcement_id = request.data['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.announcement = request.data['announcement']
        announcement.save()
        return Response({}, 200)

    def delete(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        course = get_object_or_404(
            Course, id=course_id, organization=user_organization)

        try:
            is_course_admin = UserCourseAdmin.objects.get(
                course=course, user=user)
        except UserCourseAdmin.DoesNotExist:
            return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

        announcement_id = request.data['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        return Response({}, 200)