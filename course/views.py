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


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer


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


class UserCourseSubscribtionsAPIView(GenericAPIView):
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
            Subscription.objects.create(user=user, course=course)
        except Course.DoesNotExist:
            return Response({"message": "course doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)

    def delete(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        try:
            Subscription.objects.get(user=user, course=course_id).delete()
        except Course.DoesNotExist:
            return Response({"message": "user is not subscribed to such course"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)


class UploadCourseContentAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MaterialSerializer
    queryset = Material.objects.all()
    def get(self, request, course_id):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        course = get_object_or_404(
            Course, id=course_id, organization=user_organization)

        files = Material.objects.filter(parent_course=course)
        serialized_files = MaterialSerializer(files, many=True)
        return Response(serialized_files.data, 200)

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

        file = request.FILES.get('file')
        file_name = request.POST.get('file_name')

        material = Material(parent_course=course,
                            file=file, file_name=file_name)
        material.save()
        return Response({}, 200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_course_content(request, course_id, file_id):
    user = request.user
    user_organization = get_user_profile(user).organization
    if user_organization == None:
        return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
    course = get_object_or_404(
        Course, id=course_id, organization=user_organization)

    try:
        is_course_admin = UserCourseAdmin.objects.get(course=course, user=user)
    except UserCourseAdmin.DoesNotExist:
        return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

    material = get_object_or_404(Material, id=file_id, parent_course=course)
    material.delete()

    return Response({}, 200)
