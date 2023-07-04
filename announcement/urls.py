from rest_framework import routers

from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('load-announcements/<str:course_id>',
         load_course_announcements, name="load-course-announcements"),
    path('create/', add_announcement, name='announcement-create'),
    path('manage-announcements/<str:course_code>/',
         views.UploadCourseAnnouncementAPIView.as_view()),
    path('similar-announcements/<str:announcement_id>/',
         views.get_similar_announcements, name='similar_announcements'),
    path('sub-courses/<str:course_code>/<str:course_id>/',
         views.get_sub_course_announcements, name='get-sub-courses'),
]
