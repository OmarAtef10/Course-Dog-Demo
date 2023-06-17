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
        fields = ['code', 'description','name']

