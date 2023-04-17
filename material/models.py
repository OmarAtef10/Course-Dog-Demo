import io
import os

from django.db import models
from django.db.models.signals import pre_save
from rest_framework import status
from rest_framework.response import Response
from django.dispatch import receiver
import requests
from course.models import Course
from django.core.files import File


# Create your models here.

class Material(models.Model):
    parent_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=5000)
    file_path = models.FilePathField(max_length=500, path="uploads/media", blank=True, null=True)
    file = models.FileField(default='', blank=True, null=True)

    def __str__(self):
        return f"material for {self.parent_course}"


@receiver(pre_save, sender=Material)
def pre_save_material(sender, instance, *args, **kwargs):
    if not instance.file:
        URL = instance.url
        filename = instance.file_name
        filename += ".pdf"
        print(filename)
        path = os.path.join('uploads/media', filename)
        # 2. download the data behind the URL
        try:
            headers = {
                'Authorization': 'Bearer EAAQMJrRQMU0BAL0xo09uCaZBndyoOEp8YInbWW4ERjZCdfMufWBK7pZBVfMqsYCNNP5EMFwwV4O6PeIMFHWBGyiRP5lkWO3Is6n2GSZBTBAREa36RTlZBGQxWPLrge9orgpox9RFBaG0nI6vjtXpjtkAZClQOgZB5Bz2pu4bxEZBwxPGA8A5ZAxZAwNv51KDXdDZB9qtN2NipcXOgZDZD'
            }
            response = requests.get(URL, headers=headers)
            open(path, "wb").write(response.content)
            print(path)
            instance.file_path = path
            path = path.split('/')[-1]
            instance.file = path
        except:
            print("Error in downloading file")
