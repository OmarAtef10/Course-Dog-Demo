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
from .utilities import calculate_file_hash
from organization.models import Organization


# Create your models here.


class Material(models.Model):
    id = models.CharField(primary_key=True, db_index=True,
                          unique=True, max_length=100)
    parent_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, default="New Material")
    file_name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=5000, default="", blank=True, null=True)
    file_path = models.FilePathField(
        max_length=500, path="uploads/course_material", blank=True, null=True)
    file = models.FileField(default='', blank=True,
                            null=True, upload_to='course_material/')
    creation_date = models.DateTimeField(auto_now=True)
    hash_code = models.CharField(max_length=512, null=True, blank=True)
    similar_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"material for {self.parent_course}"


@receiver(pre_save, sender=Material)
def pre_save_material(sender, instance, *args, **kwargs):
    if not instance.file:
        URL = instance.url
        if URL == "":
            return
        filename = instance.file_name
        filename += ".pdf"
        print(filename)
        path = os.path.join('uploads/course_material', filename)
        # 2. download the data behind the URL
        print("Downloading from ", URL)
        try:
            headers = {
                'Authorization': 'Bearer EAAQMJrRQMU0BAHoSY92hN0V1Ez3VGjogyui2uTv6o9voHBwZBZAOVEMrh6pp80t5cVyayhwvOmTNmW8KYZAHzZBIvJaCESGCUgdsfxkzAfB5uNELvYhIOwmjThpWL6WfFIft9m00c7iQZBycy8LBvxurHFGdGdu75jKsz1EYv5AXayNZBUhjdoTReh4ZBe254oBRyB0StFyKkFlduXzLYblC2YnC9voRksZD'
            }
            print("headers set")
            response = requests.get(URL, headers=headers)
            open(path, "wb").write(response.content)
            print(path)
            instance.file_path = path
            path = path.split('/')[-1]
            instance.file = path
            instance.hash_code = calculate_file_hash(instance.file)
            print("file saved")
        except:
            print("Error in downloading file")
