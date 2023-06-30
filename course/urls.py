from django.urls import path, include
from . import views

urlpatterns = [
    path('load-courses/', views.load_courses_from_user, name='load-courses'),
    path('course-admins/<str:course_code>/',views.course_admins_view),
    path('list-courses/', views.UserOrganizationCoursesAPIView.as_view()),
    path('list-courses/<int:phone_number>/', views.list_user_courses_by_phone_number,
         name='list-user-courses-by-phone-number'),
    path('manage-user-courses/<str:course_code>/',
         views.UserCourseSubscriptionsAPIView.as_view()),
    path('list-user-courses/', views.user_subscriptions),
    path("load-drive/", views.handle_drive_materials, name="load-drive"),
    path("load-classroom/", views.handle_classroom_loading, name="load-classroom"),
    path("sub-courses/<str:course_code>/", views.get_sub_courses, name="get-sub-courses"),
]
