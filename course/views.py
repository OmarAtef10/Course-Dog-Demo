import random
from user_profile.OAuth_helpers import list_drive_materials
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
from .tasks import download_drive_material
from material.tasks import download_materials
from announcement.tasks import load_announcements


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
        # organization = profile.organization
        courses = OAuth_helpers.get_courses(creds.token)

        for key, val in courses.items():
            for entry in val:
                try:
                    course = Course.objects.get(id=entry['id'])
                    load_user_course_material.delay(user.id, course.id)
                    load_announcement_helper.delay(user.id, course.id)
                except Course.DoesNotExist:
                    pass

        #         # if course is None:
        #         #     course = Course(id=entry['id'], name=entry['name'], organization=organization,
        #         #                     description=entry['descriptionHeading'])
        #         #     course.save()
        #         #     # load_user_course_material.delay(user.id, course.id)
        #         #     # load_announcement_helper.delay(user.id, course.id)
        return Response({"Message": "Courses Loaded!!", "Courses": courses}, status=status.HTTP_200_OK)
    else:
        return Response({"Message": "No Credentials Found maybe u didnt login with google or sth is wrong"},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_user_courses_by_phone_number(request, phone_number):
    try:
        organization = user_profile.models.Profile.objects.get(
            whatsapp_number=phone_number).organization
        courses = MainCourse.objects.filter(organization=organization)
        serializer = MainCourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


def get_all_organization_courses(organization):
    return MainCourse.objects.filter(organization=organization)


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
    serializer_class = MainCourseSerializer
    queryset = MainCourse.objects.all()

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

    serialized_courses = MainCourseSerializer(user_courses, many=True)
    return Response(serialized_courses.data, status=status.HTTP_200_OK)


class UserCourseSubscriptionsAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MainCourseSerializer

    def post(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)

        try:
            course = MainCourse.objects.get(
                code=course_code, organization=user_organization)
            user_subscription = Subscription.objects.filter(
                user=user, course=course)
            if user_subscription.exists():
                return Response({"message": "user is already subscribed to this course"},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, course=course)
        except MainCourse.DoesNotExist:
            return Response({"message": "course doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "success"}, status=status.HTTP_200_OK)

    def delete(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization

        if user_organization == None:
            return Response({"message": "user is not a part of any organization."}, status=status.HTTP_404_NOT_FOUND)
        course = MainCourse.objects.filter(
            code=course_code, organization=user_organization)
        if not course.exists():
            return Response({"message": "course doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            course = course.first()
        try:
            Subscription.objects.get(user=user, course=course).delete()
        except Subscription.DoesNotExist:
            return Response({"message": "There is no such user course subscribtion"},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_drive_materials(request):
    creds = creds_refresher(request.user)
    folder_id = request.data.get('folder_id', "")
    if folder_id == "" or folder_id == None:
        return Response({"message": "No folder_id Provided"}, status=400)

    Organization = get_user_profile(request.user).organization
    if Organization == None:
        return Response({"message": "User is not a part of any organization"}, status=400)

    name = request.data.get('name', "")
    if name == "" or name == None:
        return Response({"message": "No name Provided"}, status=400)

    code = request.data.get('code', "")
    if code == "" or code == None:
        return Response({"message": "No code Provided"}, status=400)
    try:
        ctx = list_drive_materials(creds, folder_id)
        # print(ctx)

        dirve_folders = DriveFolders.objects.filter(id=folder_id, code=code)
        organization = get_user_profile(request.user).organization

        main_course = MainCourse.objects.filter(
            code=code, organization=organization)

        if not main_course.exists():
            main_course = MainCourse.objects.create(
                name=name, code=code, organization=organization)
        else:
            main_course = main_course[0]

        if dirve_folders.exists():
            # download_files
            linked_course = Course.objects.get(
                linked_drive_folder=dirve_folders[0])
            download_drive_material.delay(
                materials=ctx, token=creds.token, course_id=linked_course.id, user=request.user.id)

        else:
            drive_folder = DriveFolders.objects.create(
                id=folder_id, name=name, code=code, organization=Organization)
            drive_folder.save()

            while True:
                id = random.randint(100, 999999)
                if not Course.objects.filter(id=id):
                    linked_course = Course(id=id, code=code, name=name, organization=Organization,
                                           description="Via Import Drive Method!", linked_drive_folder=drive_folder)
                    linked_course.save()
                    download_drive_material.delay(
                        materials=ctx, token=creds.token, course_id=linked_course.id, user=request.user.id)
                    break
        linked_course.main_course = main_course
        linked_course.save()
        main_course.materials_clusterd = False
        main_course.save()
        return Response({"message": "Rogger Rogger Importing Drive Folder!!"}, status=200)

    except Exception as e:
        print(e)
        if str(e).startswith("<"):
            return Response({"message": "Bummer, You Dont Have Access for This Drive Folder"}, status=400)
        return Response({"message": "Drive Already Linked To Something Else Please Contact Admin If You Think This Is A Mistake"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_classroom_loading(request):
    creds = creds_refresher(request.user)
    classroom_id = request.data.get('classroom_id', "")
    if classroom_id == "" or classroom_id == None:
        return Response({"message": "No classroom_id Provided"}, status=400)

    organization = get_user_profile(request.user).organization
    if organization == None:
        return Response({"message": "User is not a part of any organization"}, status=400)

    name = request.data.get('name', "")
    if name == "" or name == None:
        return Response({"message": "No name Provided"}, status=400)

    code = request.data.get('code', "")
    if code == "" or code == None:
        return Response({"message": "No code Provided"}, status=400)
    
    try:
        ctx = OAuth_helpers.get_single_course(creds.token, classroom_id)
        if ctx.status_code != 200:
            return Response({"message": "Bummer, You Dont Have Access for This ClassRoom"}, status=400)

        main_course = MainCourse.objects.filter(
            code=code, organization=organization)
        course = Course.objects.filter(
            organization=organization, id=classroom_id)

        if not main_course.exists():
            main_course = MainCourse.objects.create(
                organization=organization, code=code, name=name)
        else:
            main_course = main_course[0]

        if not course.exists():
            course = Course.objects.create(
                organization=organization, id=classroom_id, code=code, name=name, main_course=main_course)
        else:
            course = course[0]

        materials = OAuth_helpers.get_coursework(
            auth_token=creds.token, course_id=classroom_id)
        download_materials.delay(
            materials, creds.token, course.id, request.user.id)
        announcements = OAuth_helpers.get_announcements(
            auth_token=creds.token, course_id=classroom_id)
        load_announcements.delay(request.user.id, classroom_id, announcements)
        main_course.materials_clusterd = False
        main_course.save()
        return Response({"message": "Rogger Rogger Importing ClassRoom Materials!!"}, status=200)
    except Exception as e:
        print(e)
        return Response({"message": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sub_courses(request, course_code):
    user = request.user
    organization = get_user_profile(user).organization
    if organization == None:
        return Response({"message": "User is not a part of any organization"}, status=400)
    main_course = MainCourse.objects.filter(
        code=course_code, organization=organization)
    if not main_course.exists():
        return Response({"message": "No Such Course"}, status=400)
    main_course = main_course[0]
    courses = Course.objects.filter(
        main_course=main_course).distinct("name")
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=200)
