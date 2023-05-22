import allauth.socialaccount.models
import course.models
from celery import shared_task
from djoser.conf import User
from material.models import Material
from user_profile import OAuth_helpers
from user_profile.views import creds_refresher


@shared_task
def download_materials(materials, token, course_name, user):
    user = User.objects.get(id=user)
    token = creds_refresher(user)
    course_name = course.models.Course.objects.get(name=course_name)
    for key, val in materials.items():
        for entry in val:
            print("Finding material")
            material = Material.objects.filter(id=entry['id'])
            if not material:
                try:
                    print("HERE!!")
                    material = Material(id=entry['materials'][0]['driveFile']['driveFile']['id'],
                                        parent_course=course_name,
                                        title=entry['title'],
                                        file_name=entry['materials'][0]['driveFile']['driveFile']['title'],
                                        creation_date=entry['creationTime'])
                    print("Downloading file!!")
                    OAuth_helpers.download_drive_file(creds=token, file_id=material.id, file_name=material.file_name)
                    material.file = f"./course_material/{material.file_name}"
                    material.save()
                except:
                    print("File is Not DOWNLOADABLE!!!")
                    pass


@shared_task
def add(x, y):
    return x + y
