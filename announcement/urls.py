from rest_framework import routers

from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('load-announcements/<str:course_id>', load_course_announcements, name="load-course-announcements"),
    path(r'', AnnouncementViewSet.as_view({'get': 'list', "post": "create"})),
    path('create/', add_announcement, name='announcement-create'),
    path('manage-announcements/<int:course_id>/', views.UploadCourseAnnouncementAPIView.as_view())
]
