import allauth.socialaccount.models
from course.models import Course
from celery import shared_task
from djoser.conf import User
from material.models import Material
from user_profile import OAuth_helpers
from user_profile.views import creds_refresher
from .utilities import calculate_file_hash


@shared_task
def load_user_course_material(user_id, course_id):
    user = User.objects.get(id=user_id)
    token = creds_refresher(user)
    try:
        course = Course.objects.get(id=course_id)
        materials = OAuth_helpers.get_coursework(
            auth_token=token.token, course_id=course_id)
        download_materials.delay(materials, token.token, course.id, user.id)
        return True
    except Course.DoesNotExist:
        return False


@shared_task
def download_materials(materials, token, course_id, user):
    print("We are inside download materials")
    user = User.objects.get(id=user)
    token = creds_refresher(user)
    course_id = Course.objects.get(id=course_id)
    # print(materials['courseWorkMaterial'][0]['materials'])
    for key, val in materials.items():
        for entry in val:
            print("ENTRY :- ", entry)
            print("ENTRY ID :- ", entry['id'])
            print("Finding material")
            for file in entry['materials']:
                print("FILE :- ", file)
                print("FILE ID :- ", file['driveFile']['driveFile']['id'])
                material = Material.objects.filter(
                    id=file['driveFile']['driveFile']['id'])
                if not material:
                    try:
                        if file['driveFile']['driveFile']['title'].split('.')[-1] == 'mp4':
                            continue

                        print("HERE!!")
                        material = Material(id=file['driveFile']['driveFile']['id'],
                                            parent_course=course_id,
                                            title=entry['title'],
                                            file_name=file['driveFile']['driveFile']['title'],
                                            creation_date=entry['creationTime'])
                        print("Downloading file!!")
                        OAuth_helpers.download_drive_file(creds=token, file_id=material.id,
                                                          file_name=material.file_name)
                        filepath = f"./course_material/{material.file_name}"
                        material.file = filepath
                        material.hash_code = calculate_file_hash(material.file)
                        material.save()
                    except Exception as e:
                        print(e)
                        pass
