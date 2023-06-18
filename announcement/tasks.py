from celery import shared_task
from djoser.conf import User
from .models import Announcement
from course.models import Course
from user_profile import OAuth_helpers
from user_profile.views import creds_refresher


@shared_task()
def load_announcement_helper(user_id, course_id):
    user = User.objects.get(id=user_id)
    token = creds_refresher(user)
    try:
        course = Course.objects.get(id=course_id)
        annoouncements = OAuth_helpers.get_announcements(
            auth_token=token.token, course_id=course_id)
        load_announcements.delay(user.id, course.id, annoouncements)
        return True
    except Course.DoesNotExist:
        return False


@shared_task()
def load_announcements(user_id, course_id, announcements):
    user = User.objects.get(id=user_id)
    token = creds_refresher(user)
    course = Course.objects.get(id=course_id)
    for key, val in announcements.items():
        for entry in val:
            announcement = Announcement.objects.filter(id=entry['id'])
            if not announcement:
                announcement = Announcement(id=entry['id'], course=course, announcement=entry['text'],
                                            title=entry.get('title', 'New Announcement'),
                                            creation_date=entry['creationTime'])
                announcement.save()
