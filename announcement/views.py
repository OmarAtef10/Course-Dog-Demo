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
from authentication.permissions import IsCourseAdmin
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
from course.serializers import *
from user_profile.views import creds_refresher
from user_profile import OAuth_helpers
from .tasks import load_announcements
from course.views import is_course_admin


# Create your views here.

def generate_announcement_id():
    return random.randint(1000, 999999)


def get_main_course_sub_courses(main_course):
    return Course.objects.filter(main_course=main_course)


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


@api_view(["POST"])
def add_announcement(request):
    try:
        org_name = request.data['org_name']
        organization = get_object_or_404(Organization, name=org_name)
        course_code = request.data['course_code']
        announcement = request.data['announcement']
        main_course = MainCourse.objects.get(code=course_code)
        if main_course.organization == organization:
            course = Course.objects.create(code=course_code, organization=organization, main_course=main_course,
                                           id=generate_announcement_id(), name="Via Webhooks")

            while True:
                id = random.randint(100, 999999)
                if not Announcement.objects.filter(id=id):
                    announcement = Announcement.objects.create(id=id, course=course, content=announcement,
                                                               title="By Admin Student Via Webhooks!",
                                                               creation_date=datetime.datetime.now())
                    announcement.save()
                    break
                main_course.announcements_clusterd = False
                main_course.save()

            return Response({'message': 'Announcement created successfully'}, status=HTTP_201_CREATED)
        else:
            return Response({'message': f'Course not found for {org_name} organization'}, status=HTTP_404_NOT_FOUND)

    except:
        return Response({"error": True, 'message': 'Course does not exist'}, status=HTTP_404_NOT_FOUND)


class UploadCourseAnnouncementAPIView(GenericAPIView):
    serializer_class = AnnouncementFullSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes.append(IsCourseAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        try:
            main_course = get_object_or_404(
                MainCourse, organization=user_organization, code=course_code)

            user_subscription = Subscription.objects.filter(
                user=user, course=main_course)
            if not user_subscription.exists():
                return Response({"message": "user is not subscribed to this course"},
                                status=status.HTTP_400_BAD_REQUEST)
        except MainCourse.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

        courses_list = get_main_course_sub_courses(main_course)
        announcements = []
        for course_ in courses_list:
            course_announcements = Announcement.objects.filter(course=course_, similar_to=None)
            for announcement in course_announcements:
                announcements.append(announcement)

        serialized_announcements = self.get_serializer(
            announcements, many=True)
        serialized_course = MainCourseSerializer(main_course)
        is_admin = is_course_admin(user, main_course)
        return Response({"course": serialized_course.data, "is_course_admin": is_admin,
                         "announcements": serialized_announcements.data}, 200)

    def post(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        try:
            main_course = MainCourse.objects.get(
                code=course_code, organization=user_organization)
            is_course_admin = UserCourseAdmin.objects.filter(
                course=main_course, user=user)
            if not is_course_admin.exists():
                return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)
        except MainCourse.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

        title = request.data.get("title", "New Announcement")
        if title == "":
            title = "New Announcement"

        announcement_details = request.data.get("announcement", "")
        if announcement_details == "":
            return Response({"message": "Announcement cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)
        courses = get_main_course_sub_courses(main_course)
        for course in courses:
            announcement = Announcement(
                id=generate_announcement_id(),
                course=course,
                title=title,
                content=announcement_details,
            )
            announcement.save()
        main_course.announcements_clusterd = False
        main_course.save()
        return Response({"message": "success"}, 200)

    def delete(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)

        try:
            course = get_object_or_404(
                MainCourse, code=course_code, organization=user_organization)

            is_course_admin = UserCourseAdmin.objects.filter(
                course=course, user=user)
            if not is_course_admin.exists():
                return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)
        except MainCourse.DoesNotExist:
            return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

        announcement_id = request.data['announcement_id']
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()
        return Response({"message": "success"}, 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_similar_announcements(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
    except Announcement.DoesNotExist:
        return Response({"message": "Announcement does not exist"}, status=status.HTTP_404_NOT_FOUND)
    similar_announcements = Announcement.objects.filter(
        similar_to=announcement)
    serialized_announcements = AnnouncementSerializer(
        similar_announcements, many=True).data
    ctx = {"orgininal_announcement": AnnouncementSerializer(
        announcement).data, "similar_announcements": serialized_announcements}
    return Response(ctx, 200)
