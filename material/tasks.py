import allauth.socialaccount.models
import course.models
from celery import shared_task
from material.models import Material
from user_profile import OAuth_helpers


@shared_task
def download_materials(materials, token, course_name):
    token = allauth.socialaccount.models.SocialToken.objects.get(token=token)
    course_name = course.models.Course.objects.get(name=course_name)
    for key, val in materials.items():
        for entry in val:
            material = Material.objects.filter(id=entry['id'])
            if not material:
                print("HERE!!")
                material = Material(id=entry['materials'][0]['driveFile']['driveFile']['id'], parent_course=course_name,
                                    title=entry['title'],
                                    file_name=entry['materials'][0]['driveFile']['driveFile']['title'],
                                    creation_date=entry['creationTime'])
                print("Downloading file!!")
                OAuth_helpers.download_drive_file(creds=token, file_id=material.id, file_name=material.file_name)
                material.file = f"./course_material/{material.file_name}"
                material.save()

