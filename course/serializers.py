from rest_framework import serializers

from .models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ('organization', 'name', 'id')


class CreateCourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256, required=True)

    class Meta:
        model = Course
        fields = ['code', 'description', 'name']


class MainCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCourse
        fields = ['id', 'code', 'name', 'organization']
        depth = 1


class CreateMainCourseSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=50, required=True)
    name = serializers.CharField(max_length=256, required=True)

    class Meta:
        model = MainCourse
        fields = ['code', 'name']


class DriveFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriveFolders
        fields = "__all__"
