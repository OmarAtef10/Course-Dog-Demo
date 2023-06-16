import datetime
import random

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
from user_profile.views import creds_refresher
from user_profile import OAuth_helpers
from .tasks import load_announcements
from course.models import Subscription


# Create your views here.

def generate_announcement_id():
    return random.randint(100000000, 999999999)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_course_announcements(request, course_id):
    token = creds_refresher(request.user)
    course = get_object_or_404(Course, id=course_id)
    announcements = OAuth_helpers.get_announcements(
        auth_token=token.token, course_id=course_id)
    load_announcements.delay(request.user.id, course_id, announcements)
    # for key, val in announcements.items():
    #     for entry in val:
    #         announcement = Announcement.objects.filter(id=entry['id'])
    #         if not announcement:
    #             announcement = Announcement(id=entry['id'], course=course, announcement=entry['text'],
    #                                         title=entry.get('title', 'New Announcement'),
    #                                         creation_date=entry['creationTime'])
    #             announcement.save()

    return Response({"Message": "Announcements Loaded!!", "Announcements": announcements}, status=status.HTTP_200_OK)


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

            while True:
                id = random.randint(100, 999999)
                if not Announcement.objects.filter(id=id):
                    announcement = Announcement.objects.create(id=id, course=course, announcement=announcement,
                                                               title="From Admin Student Via Webhooks!",
                                                               creation_date=datetime.datetime.now())
                    announcement.save()
                    break

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
        try:
            course = get_object_or_404(
                Course, id=course_id, organization=user_organization)

            user_subscription = Subscription.objects.filter(
                user=user, course=course)
            if not user_subscription.exists():
                return Response({"message": "user is not subscribed to this course"}, status=status.HTTP_400_BAD_REQUEST)

        except Course.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)
        announcements = Announcement.objects.filter(course=course)
        serialized_announcements = self.get_serializer(
            announcements, many=True)
        serialized_course = CourseSerializer(course)
        return Response({"course": serialized_course.data, "announcements": serialized_announcements.data}, 200)

    def post(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        try:
            course = Course.objects.get(
                id=course_id, organization=user_organization)
            is_course_admin = UserCourseAdmin.objects.filter(
                course=course, user=user)
            if not is_course_admin.exists():
                return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)
        except Course.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

        announcement_data = self.get_serializer(data=request.data)
        if announcement_data.is_valid():
            announcement_id = generate_announcement_id()
            announcement = Announcement(
                id=announcement_id,
                course=course,
                announcement=announcement_data.validated_data['announcement'],
                creation_date=announcement_data.validated_data['creation_date'],
            )
            announcement.save()
        return Response({"message": "success"}, 200)

    def delete(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)

        try:
            course = get_object_or_404(
                Course, id=course_id, organization=user_organization)

            is_course_admin = UserCourseAdmin.objects.filter(
                course=course, user=user)
            if not is_course_admin.exists():
                return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)
        except Course.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

        announcement_id = request.data['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        return Response({"message": "success"}, 200)
