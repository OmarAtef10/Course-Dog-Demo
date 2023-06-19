from django.urls import path, include
from . import views

urlpatterns = [
    path('load-courses/', views.load_courses_from_user, name='load-courses'),

    path('list-courses/', views.UserOrganizationCoursesAPIView.as_view()),
    path('list-courses/<int:phone_number>/', views.list_user_courses_by_phone_number,
         name='list-user-courses-by-phone-number'),
    path('manage-user-courses/<int:course_id>/',
         views.UserCourseSubscriptionsAPIView.as_view()),
    path('list-user-courses/', views.user_subscriptions),
    path("course/<int:course_id>/", views.get_course_by_id, name="course-detail"),
]
