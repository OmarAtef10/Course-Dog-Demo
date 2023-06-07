from django.shortcuts import get_object_or_404
from organization.models import Organization
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *
from .models import Material
from rest_framework.decorators import api_view, permission_classes
from course.models import Course
from user_profile.views import creds_refresher
from user_profile import OAuth_helpers
from .tasks import download_materials
import uuid


# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_course_materials(request, course_id):
    token = creds_refresher(request.user)
    course = get_object_or_404(Course, id=course_id)
    materials = OAuth_helpers.get_coursework(auth_token=token.token, course_id=course_id)
    download_materials.delay(materials, token.token, course.name, request.user.id)
    # for key, val in materials.items():
    #     for entry in val:
    #         material = Material.objects.filter(id=entry['id'])
    #         if not material:
    #             material = Material(id=entry['materials'][0]['driveFile']['driveFile']['id'], parent_course=course,
    #                                 title=entry['title'],
    #                                 file_name=entry['materials'][0]['driveFile']['driveFile']['title'],
    #                                 creation_date=entry['creationTime'])
    #             OAuth_helpers.download_drive_file(creds=token, file_id=material.id, file_name=material.file_name)
    #             material.file = f"./course_material/{material.file_name}"
    #             material.save()

    return Response({"Message": "Materials Loaded!!", "Materials": materials}, status=status.HTTP_200_OK)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer


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
            course = get_object_or_404(Course, code=course_code)
            if course.organization == organization:
                id = uuid.uuid4()
                id = str(id)
                material = Material.objects.create(id=id, parent_course=course, file_name=file_name, url=url,
                                                   title="By Admin Student Via Webhooks!")
                material.save()
                return Response({'message': 'Material created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': f'Course not found for {org_name} organization'},
                                status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'message': 'Error in creating material'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        materials = Material.objects.all()
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)
