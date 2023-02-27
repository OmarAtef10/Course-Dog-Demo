from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from django.http import JsonResponse


# Create your views here.

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer

