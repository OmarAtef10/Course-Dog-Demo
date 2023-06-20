from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from authentication.serializers import UserSerializer
from django.contrib.auth.models import Group
from user_profile.models import Profile
from user_profile.views import get_user_profile
from authentication.permissions import IsOrganizationAdmin
from course.models import Course, UserCourseAdmin, MainCourse
from course.views import get_all_organization_courses
from course.serializers import CourseSerializer, CreateCourseSerializer, MainCourseSerializer, CreateMainCourseSerializer
from django.db import IntegrityError
import random
# Create your views here.
# CourseAdmin - OrganizationAdmin - Student


def generate_course_id():
    return random.randint(100000000, 999999999)


def get_organization_subdomains(organization):
    return OrganizationSubdomain.objects.filter(organization=organization)


def get_organization_admins(organization):
    return UserOrganizationAdmin.objects.filter(organization=organization)


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


class OrganizationAPIView(GenericAPIView):
    serializer_class = OrganizationFullSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = get_user_profile(request.user)
        organization = user_profile.organization
        if organization == None:
            return Response({"message": "user is not a part of an organization"}, status=status.HTTP_404_NOT_FOUND)

        subdomains = get_organization_subdomains(organization)

        serialized_organization = self.get_serializer(organization).data
        serialized_subdomains = SubdomainSerializer(subdomains, many=True).data

        return Response({'organization_info': serialized_organization, 'subdomains': serialized_subdomains}, status=status.HTTP_200_OK)


class OrganizationAdminsDataAPIView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]
    # Endpoint used to fetch all admins data of the organization and to add new admins to the organization

    def get(self, request):
        user_profile = get_user_profile(request.user)
        user_organization = user_profile.organization

        if user_organization == None:
            return Response({"message": "user is not a part of an organization"}, status=status.HTTP_404_NOT_FOUND)

        organization_admins = get_organization_admins(user_organization)
        users = [
            organization_admin.user for organization_admin in organization_admins]
        print(users)
        serialized_users = self.get_serializer(users, many=True)
        return Response(serialized_users.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        user_profile = get_user_profile(user)
        user_organization = user_profile.organization

        if user_organization == None:
            return Response({"message": "user is not a part of an organization"}, status=status.HTTP_404_NOT_FOUND)

        user_email = request.data.get('email')
        if user_email == None or user_email == '':
            return Response({"message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_user = User.objects.get(email=user_email)
            UserOrganizationAdmin.objects.create(
                user=new_user, organization=user_organization)
            new_user.groups.add(Group.objects.get(name='OrganizationAdmin'))
            new_user.groups.remove(Group.objects.get(name='Student'))
            new_user_profile = Profile.objects.get(user=new_user)
            new_user_profile.organization = user_organization
            new_user_profile.save()
            new_user.save()
        except Exception as e:
            return Response({"message": f'{e}'}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "user added successfully"}, status=status.HTTP_200_OK)


class GeneralOrganizationDataAPIView(GenericAPIView):
    serializer_class = OrganizationFullSerializer
    # Endpoint used to fetch all organization data by name and to add new subdomains to the organization

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes.append(IsOrganizationAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request, name):
        try:
            organization = Organization.objects.get(name=name)
        except Organization.DoesNotExist:
            return Response({"message": "Organization doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        subdomains = get_organization_subdomains(organization)
        serialized_organization = self.get_serializer(organization).data
        serialized_subdomains = SubdomainSerializer(subdomains, many=True).data

        return Response({'organization_info': serialized_organization, 'subdomains': serialized_subdomains}, status=status.HTTP_200_OK)

    def post(self, request, name):
        user = request.user
        user_profile = get_user_profile(user)
        user_organization = user_profile.organization

        if user_organization == None:
            return Response({"message": "user is not a part of an organization"}, status=status.HTTP_404_NOT_FOUND)

        subdomain = request.data.get('subdomain')
        if subdomain == None:
            return Response({"message": "subdomain is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            OrganizationSubdomain.objects.create(
                organization=user_organization, subdomain=subdomain)
        except:
            return Response({"message": "subdomain already exists"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "subdomain added successfully"}, status=status.HTTP_200_OK)


class ManageCourseAdminsAPIView(GenericAPIView):
    serializer_class = UserSerializer
    # Endpoint used to fetch all course admins data of a course and to add new course admins to the course and also remove course admins from the course

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes.append(IsOrganizationAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        course_admins = UserCourseAdmin.objects.filter(course=course)
        users = [course_admin.user for course_admin in course_admins]
        serialized_users = self.get_serializer(users, many=True)
        return Response(serialized_users.data, status=status.HTTP_200_OK)

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user_email = request.data.get('email')
        if user_email == None or user_email == '':
            return Response({"message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=user_email)
            user_profile = get_user_profile(user)
            if user_profile.organization != course.organization:
                return Response({"message": "user is not a part of the organization"}, status=status.HTTP_400_BAD_REQUEST)
            UserCourseAdmin.objects.create(user=user, course=course)
            user.groups.add(Group.objects.get(name='CourseAdmin'))
            user.groups.remove(Group.objects.get(name='Student'))
            user.save()
        except User.DoesNotExist:
            return Response({"message": "user doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({"message": "user is already an admin on this course"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "user added successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user_email = request.data.get('email')
        if user_email == None or user_email == '':
            return Response({"message": "email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=user_email)
            UserCourseAdmin.objects.get(user=user, course=course).delete()
            is_still_admin = UserCourseAdmin.objects.filter(user=user).exists()
            if not is_still_admin:
                user.groups.remove(Group.objects.get(name='CourseAdmin'))
                user.groups.add(Group.objects.get(name='Student'))
            user.save()
        except User.DoesNotExist:
            return Response({"message": "user doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except UserCourseAdmin.DoesNotExist:
            return Response({"message": "user is not an admin on this course"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "user deleted successfully"}, status=status.HTTP_200_OK)


class ManageOrganizationCoursesAPIView(GenericAPIView):
    serializer_class = MainCourseSerializer
    # Endpoint used to fetch all courses data of an organization and to add new courses to the organization and also remove courses from the organization

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != 'GET':
            permission_classes.append(IsOrganizationAdmin)
        return [permission() for permission in permission_classes]

    def get(self, request):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)
        courses = get_all_organization_courses(user_organization)
        serialized_courses = self.get_serializer(courses, many=True)
        return Response(serialized_courses.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        user_organization = get_user_profile(user).organization
        course_id = generate_course_id()
        course_data = CreateCourseSerializer(data=request.data)
        if course_data.is_valid():
            try:
                course_code = course_data.validated_data['code']

                main_course = MainCourse.objects.filter(
                    code=course_code, organization=user_organization)
                if not main_course.exists():
                    main_course = MainCourse(
                        code=course_code, organization=user_organization, name=course_data.validated_data['name'])
                    main_course.save()
                else:
                    main_course = main_course[0]

                course = Course(
                    id=course_id,
                    name=course_data.validated_data['name'],
                    description=course_data.validated_data['description'],
                    organization=user_organization,
                    code=course_data.validated_data['code'],
                    main_course=main_course
                )
            except IntegrityError:
                return Response({"message": "Integrity Error please resubmit the request"}, status=status.HTTP_400_BAD_REQUEST)
            course.save()
            return Response({"message": "course added successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "course data is invalid"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user_organization = get_user_profile(user).organization
        course_code = request.data.get('course_code')
        if course_code == None or course_code == '':
            return Response({"message": "course id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            MainCourse.objects.get(
                code=course_code, organization=user_organization).delete()
        except MainCourse.DoesNotExist:
            return Response({"message": "course doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "course deleted successfully"}, status=status.HTTP_200_OK)
