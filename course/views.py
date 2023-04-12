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

# Create your views here.


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
