import user_profile.models
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from user_profile.views import get_user_profile
from organization.models import *
from material.models import Material
from material.serializers import MaterialSerializer
from allauth.socialaccount.models import SocialAccount, SocialToken
from user_profile.views import creds_refresher
from user_profile.models import Profile
from user_profile import OAuth_helpers
from material.tasks import load_user_course_material
from announcement.tasks import load_announcement_helper


# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_courses_from_user(request):
    user = request.user
    creds = creds_refresher(user)
    if creds:
        profile = None
        try:
            profile = Profile.objects.get(user=user)
        except:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        organization = profile.organization
        courses = OAuth_helpers.get_courses(creds.token)
        for key, val in courses.items():
            for entry in val:
                try:
                    course = Course.objects.get(id=entry['id'])
                    load_user_course_material.delay(user.id, course.id)
                    load_announcement_helper.delay(user.id, course.id)
                except Course.DoesNotExist:
                    course = None

                if course is None:
                    course = Course(id=entry['id'], name=entry['name'], organization=organization,
                                    description=entry['descriptionHeading'])
                    course.save()
                    load_user_course_material.delay(user.id, course.id)
                    load_announcement_helper.delay(user.id, course.id)
        return Response({"Message": "Courses Loaded!!", "Courses": courses}, status=status.HTTP_200_OK)
    else:
        return Response({"Message": "No Credentials Found maybe u didnt login with google or sth is wrong"},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_user_courses_by_phone_number(request, phone_number):
    try:
        organization = user_profile.models.Profile.objects.get(
            whatsapp_number=phone_number).organization
        courses = Course.objects.filter(organization=organization)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


def get_all_organization_courses(organization):
    return Course.objects.filter(organization=organization)


def get_all_user_subscriptions(user):
    return Subscription.objects.filter(user=user)


def get_all_user_courses(user):
    user_subscriptions = get_all_user_subscriptions(user)
    courses = [sub.course for sub in user_subscriptions]
    return courses


def get_all_course_admins(course):
    return UserCourseAdmin.objects.filter(course=course)


def is_course_admin(user, course):
    is_admin = UserCourseAdmin.objects.filter(user=user, course=course)
    return is_admin.exists()


class UserOrganizationCoursesAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get(self, request):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        courses = get_all_organization_courses(user_organization)
        serialized_courses = self.get_serializer(courses, many=True)
        return Response(serialized_courses.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_subscriptions(request):
    user = request.user
    user_organization = get_user_profile(user).organization

    if user_organization == None:
        return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

    user_courses = get_all_user_courses(user)

    serialized_courses = CourseSerializer(user_courses, many=True)
    return Response(serialized_courses.data, status=status.HTTP_200_OK)


class UserCourseSubscriptionsAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def post(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        try:
            course = Course.objects.get(
                id=course_id, organization=user_organization)
            user_subscription = Subscription.objects.filter(
                user=user, course=course)
            if user_subscription.exists():
                return Response({"message": "user is already subscribed to this course"},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, course=course)
        except Course.DoesNotExist:
            return Response({"message": "course doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "success"}, status=status.HTTP_200_OK)

    def delete(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        try:
            Subscription.objects.get(user=user, course=course_id).delete()
        except Subscription.DoesNotExist:
            return Response({"message": "There is no such user course subscribtion"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)


### adding course/materials from drive
class DriveIntegration(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def post(self, request):

        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization is None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        try:
            creds = creds_refresher(user)
        except SocialAccount.DoesNotExist:
            return Response({"message": "No Credentials Found maybe u didnt login with google or sth is wrong"},
                            status=status.HTTP_400_BAD_REQUEST)

        course_id = request.data.get('course_id', "")
        if course_id == "" or course_id is None:
            return Response({"message": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        course_name = request.data.get('course_name', "")
        if course_name == "" or course_name is None:
            return Response({"message": "course_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        course_code = request.data.get('course_code', "")
        if course_code == "" or course_code is None:
            return Response({"message": "course_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(
                id=course_id, organization=user_organization)
            return Response({"message": "course already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            course = Course.objects.create(
                id=course_id, name=course_name, description="Added by a student via drive integration",
                organization=user_organization, code=course_code)
            course.save()

        return Response({"message": "success"}, status=status.HTTP_200_OK)
