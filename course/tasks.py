import allauth.socialaccount.models
from course.models import Course
from celery import shared_task
from djoser.conf import User
from material.models import Material
from user_profile import OAuth_helpers
from user_profile.views import creds_refresher
from material.utilities import calculate_file_hash


@shared_task
def download_drive_material(materials, token, course_id, user):
    print("We are inside download materials")
    user = User.objects.get(id=user)
    token = creds_refresher(user)
    course_id = Course.objects.get(id=course_id)
    # print(materials['courseWorkMaterial'][0]['materials'])
    for key, val in materials.items():
        print("KEY :- ", key, "VALUE :- ", val)

        material = Material.objects.filter(
            id=val)
        if not material:
            try:
                if key.split('.')[-1] == 'mp4':
                    continue

                print("HERE!!")
                material = Material(id=val,
                                    parent_course=course_id,
                                    title=key,
                                    file_name=key)
                print("Downloading file!!")
                OAuth_helpers.download_drive_file(creds=token, file_id=material.id,
                                                  file_name=material.file_name)
                filepath = f"./course_material/{material.file_name}"
                material.file = filepath
                material.hash_code = calculate_file_hash(material.file)
                if course_id.main_course.materials_clusterd == False:
                    material.save()
                else:
                    course_id.main_course.materials_clusterd = False
                    course_id.main_course.save()
                    material.save()
            except Exception as e:
                print(e)
                pass
