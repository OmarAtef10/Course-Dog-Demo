from rest_framework import routers

from django.urls import path, include
from . import views

urlpatterns = [
    path('load-materials/<str:course_id>',
         views.load_course_materials, name='load_materials'),
    path('create/', views.add_materials_webhooks, name='material-create'),
    path('upload-material/<str:course_code>/',
         views.UploadCourseContentAPIView.as_view()),
    path('delete-material/<str:course_code>/<str:file_id>/',
         views.delete_course_content),
    path('similar-materials/<str:material_id>/',
         views.get_similar_to_materials, name='similar_materials'),
    path('sub-courses/<str:course_code>/<str:course_id>/',
         views.get_sub_course_materials, name='get-sub-courses-materials'),
]
