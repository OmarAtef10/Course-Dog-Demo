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
        print("CWD!:- ", os.getcwd())
        print("PATH!:- ", path)
        final_path = os.path.join(os.getcwd(), path)
        print("FINAL PATH!:- ", final_path)
        # 2. download the data behind the URL
        print("Downloading from ", URL)
        try:
            print("setting headers")
            headers = {
                'Authorization': 'Bearer EAAQMJrRQMU0BAB3YQsfIzBGtPlCZCOtZCZAmEF9MZCgMAZCqb2ElX4kHgoLYi2y2BZBQD3yoPxYX4fnWMTPdAwcAZAL6tG2yQ0KfqpLqzEg8zkGedPChz1SPuQZCabXIJI4yz1rTChRdRjDFvvvouH0gE1Qk8fqdVQztjhibjEseZCCizukrLtvJR1oqDcAXgnzvqzq0NUnc6kXN7WwMXl00cdt2d3PFkpLoZD'
            }
            print("getting response")
            response = requests.get(URL, headers=headers)
            open(path, "wb").write(response.content)
            print(path)
            instance.file_path = path
            print("setting file")
            path = path.split('/')[-1]
            print(path)
            final_path = final_path.split("/")[-2:]
            print(final_path)
            instance.file = "/".join(final_path)
            instance.hash_code = calculate_file_hash(instance.file)
            print("file set")

        except Exception as e:
            print(e)
            print("Error in downloading file")
