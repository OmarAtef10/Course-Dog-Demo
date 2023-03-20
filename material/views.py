from django.shortcuts import get_object_or_404
from organization.models import Organization
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import *
from .models import Material
from rest_framework.decorators import api_view
from course.models import Course


# Create your views here.
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer


@api_view(["POST", "GET"])
def add_materials(request):
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
                material = Material.objects.create(parent_course=course, file_name=file_name, url=url)
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
