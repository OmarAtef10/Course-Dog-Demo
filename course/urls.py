from rest_framework import routers

from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'', views.CourseViewSet)

urlpatterns = [
    path('load-courses/', views.load_courses_from_user, name='load-courses'),
    path('list-courses/', views.UserOrganizationCoursesAPIView.as_view()),
    path('manage-user-courses/<int:course_id>/',
         views.UserCourseSubscribtionsAPIView.as_view()),
    path('list-user-courses/', views.user_subscriptions),
    path('upload-material/<int:course_id>/',
         views.UploadCourseContentAPIView.as_view()),
    path('delete-material/<int:course_id>/<int:file_id>/',
         views.delete_course_content),
    path('', include(router.urls)),
]
