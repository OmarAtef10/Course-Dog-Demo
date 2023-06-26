from django.shortcuts import get_object_or_404

from announcement.views import generate_announcement_id
from organization.models import Organization
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .serializers import *
from .models import Material
from rest_framework.decorators import api_view, permission_classes
from course.models import Course, UserCourseAdmin
from course.serializers import CourseSerializer
from user_profile.views import get_user_profile
from user_profile.views import creds_refresher
from user_profile import OAuth_helpers
from .tasks import download_materials
import uuid
from .utilities import calculate_file_hash
from course.views import is_course_admin
from authentication.permissions import IsCourseAdmin
from course.models import MainCourse
from course.serializers import MainCourseSerializer


# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_course_materials(request, course_id):
    token = creds_refresher(request.user)
    course = get_object_or_404(Course, id=course_id)
    materials = OAuth_helpers.get_coursework(
        auth_token=token.token, course_id=course_id)
    download_materials.delay(materials, token.token,
                             course.id, request.user.id)

    return Response({"Message": "Materials Loaded!!", "Materials": materials}, status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
def add_materials_webhooks(request):
    if request.method == "POST":
        print("We are inside post request")
        url = request.data['url']
        org_name = request.data['org_name']
        organization = get_object_or_404(Organization, name=org_name)
        course_code = request.data['course_code']
        file_name = request.data.get('file_name', 'default.pdf')
        print(course_code)
        try:
            main_course = MainCourse.objects.get(
                code=course_code, organization=organization)
        except:
            return Response({'message': f'Course not found for {org_name} organization'},
                            status=status.HTTP_404_NOT_FOUND)

        course = Course.objects.create(code=course_code, organization=organization, main_course=main_course,
                                       id=generate_announcement_id(), name="Via Webhooks")
        id = uuid.uuid4()
        id = str(id)
        material = Material.objects.create(id=id, parent_course=course, file_name=file_name, url=url,
                                           title="By Admin Student Via Webhooks!")
        material.save()
        main_course.materials_clusterd = False
        main_course.save()
        return Response({'message': 'Material created successfully'}, status=status.HTTP_201_CREATED)

    if request.method == "GET":
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)


class UploadCourseContentAPIView(GenericAPIView):
    serializer_class = MaterialSerializer
    queryset = Material.objects.all()

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

        main_course = get_object_or_404(
            MainCourse, code=course_code, organization=user_organization)

        serialized_course = MainCourseSerializer(main_course).data

        courses = Course.objects.filter(main_course=main_course)
        courses_files = []
        for course in courses:
            files = Material.objects.filter(
                parent_course=course, similar_to=None)
            for file in files:
                courses_files.append(file)

        serialized_files = MaterialSerializer(courses_files, many=True).data
        is_admin = is_course_admin(user, main_course)
        return Response({"course": serialized_course, "is_course_admin": is_admin, "materials": serialized_files}, 200)

    def post(self, request, course_code):
        user = request.user
        user_organization = get_user_profile(user).organization
        if user_organization == None:
            return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
        main_course = get_object_or_404(
            MainCourse, code=course_code, organization=user_organization)
        try:
            UserCourseAdmin.objects.get(course=main_course, user=user)
        except UserCourseAdmin.DoesNotExist:
            return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

        file = request.FILES.get('file')
        if file == None:
            return Response({"message": "No file was uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        file_name = request.POST.get('file_name')
        if file_name == None:
            file_name = file.name
        file_hash = calculate_file_hash(file)
        id = uuid.uuid4()
        id = str(id)

        course = Course.objects.create(code=course_code, organization=user_organization, main_course=main_course,
                                       id=generate_announcement_id(), name="Via Create Material by Course Admin!")
        material = Material(id=id, parent_course=course,
                            file=file, file_name=file_name, hash_code=file_hash)
        material.save()
        main_course.materials_clusterd = False
        main_course.save()
        return Response({}, 200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsCourseAdmin])
def delete_course_content(request, course_code, file_id):
    user = request.user
    user_organization = get_user_profile(user).organization
    if user_organization == None:
        return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
    main_course = get_object_or_404(
        MainCourse, code=course_code, organization=user_organization)
    try:
        is_course_admin = UserCourseAdmin.objects.get(
            course=main_course, user=user)
    except UserCourseAdmin.DoesNotExist:
        return Response({"message": "User is not an admin on this course"}, status=status.HTTP_401_UNAUTHORIZED)

    material = get_object_or_404(Material, id=file_id)
    material.delete()

    return Response({}, 200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_similar_to_materials(request, material_id):
    try:
        material = Material.objects.get(id=material_id)
    except Material.DoesNotExist:
        return Response({"message": "Material does not exist"}, status=status.HTTP_404_NOT_FOUND)

    similar_materials = Material.objects.filter(similar_to=material)
    serialized_materials = MaterialSerializer(
        similar_materials, many=True).data
    ctx = {"original_material": MaterialSerializer(
        material).data, "similar_materials": serialized_materials}
    return Response(ctx, 200)


def handle_multi_course_material_loading(name, main_course):
    courses = Course.objects.filter(main_course=main_course, name=name)
    materials = Material.objects.filter(parent_course__in=courses)
    serialized_materials = MaterialSerializer(materials, many=True).data
    return serialized_materials


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_sub_course_materials(request, course_code, course_id):
    user = request.user
    user_organization = get_user_profile(user).organization
    if user_organization == None:
        return Response({"message": "User is not a member of an organization"}, status=status.HTTP_404_NOT_FOUND)
    try:
        main_course = MainCourse.objects.get(
            code=course_code, organization=user_organization)
    except MainCourse.DoesNotExist:
        return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

    if course.main_course != main_course:
        return Response({"message": "Course does not exist"}, status=status.HTTP_404_NOT_FOUND)

    if course.name == "Via Create Material by Course Admin!":
        ctx = {
            "course": CourseSerializer(course).data,
            "materials": handle_multi_course_material_loading(name="Via Create Material by Course Admin!", main_course=main_course)
        }
        return Response(ctx, 200)
    if course.name == "Via Webhooks":
        ctx = {
            "course": CourseSerializer(course).data,
            "materials": handle_multi_course_material_loading(name="Via Webhooks", main_course=main_course)
        }
        return Response(ctx, 200)

    materials = Material.objects.filter(parent_course=course)
    serialized_materials = MaterialSerializer(materials, many=True).data
    ctx = {
        "course": CourseSerializer(course).data,
        "materials": serialized_materials
    }
    return Response(ctx, 200)
