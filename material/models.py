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
    url = models.URLField(max_length=5000)
    file_path = models.FilePathField(max_length=500, path="uploads/media", blank=True, null=True)
    file = models.FileField(default='', blank=True, null=True)

    def __str__(self):
        return f"material for{self.parent_course}"


@receiver(pre_save, sender=Material)
def pre_save_material(sender, instance, *args, **kwargs):
    URL = instance.url
    filename = URL.split('/')[-1]
    filename = filename.split('?')[0]
    print(filename)
    path = os.path.join('uploads/media', filename)
    # 2. download the data behind the URL
    response = requests.get(URL)
    open(path, "wb").write(response.content)
    print(path)
    instance.file_path = path
    path = path.split('/')[-1]
    instance.file = path

