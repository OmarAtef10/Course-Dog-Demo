from rest_framework import serializers

from .models import *
from course.serializers import CourseSerializer


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'


class AnnouncementFullSerializer(serializers.ModelSerializer):
    announcement = serializers.CharField(required=True)
    creation_date = serializers.DateTimeField(required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Announcement
        fields = ['announcement', 'creation_date', 'id','title']
        depth = 1


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['announcement', 'creation_date']
