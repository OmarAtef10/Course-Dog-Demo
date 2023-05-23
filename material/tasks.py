import allauth.socialaccount.models
import course.models
from celery import shared_task
from djoser.conf import User
from material.models import Material
from user_profile import OAuth_helpers
from user_profile.views import creds_refresher


@shared_task
def download_materials(materials, token, course_name, user):
    print("We are inside download materials")
    user = User.objects.get(id=user)
    token = creds_refresher(user)
    course_name = course.models.Course.objects.get(name=course_name)
    # print(materials['courseWorkMaterial'][0]['materials'])
    for key, val in materials.items():
        for entry in val:
            print("ENTRY :- ", entry)
            print("ENTRY ID :- ", entry['id'])
            print("Finding material")
            for file in entry['materials']:
                print("FILE :- ", file)
                print("FILE ID :- ", file['driveFile']['driveFile']['id'])
                material = Material.objects.filter(id=file['driveFile']['driveFile']['id'])
                if not material:
                    try:
                        if file['driveFile']['driveFile']['title'].split('.')[-1] == 'mp4':
                            continue

                        print("HERE!!")
                        material = Material(id=file['driveFile']['driveFile']['id'],
                                            parent_course=course_name,
                                            title=entry['title'],
                                            file_name=file['driveFile']['driveFile']['title'],
                                            creation_date=entry['creationTime'])
                        print("Downloading file!!")
                        OAuth_helpers.download_drive_file(creds=token, file_id=material.id,
                                                          file_name=material.file_name)
                        material.file = f"./course_material/{material.file_name}"
                        material.save()
                    except:
                        print("File is Not DOWNLOADABLE!!!")
                        pass


@shared_task
def add(x, y):
    return x + y
