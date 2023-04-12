from rest_framework import routers

from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'', views.CourseViewSet)

urlpatterns = [
    path('list-courses/', views.UserOrganizationCoursesAPIView.as_view()),
    path('manage-user-courses/<int:course_id>/',
         views.UserCourseSubscribtionsAPIView.as_view()),
    path('list-user-courses/', views.user_subscriptions),

    path('', include(router.urls)),
]
