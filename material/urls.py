from rest_framework import routers

from django.urls import path, include
from . import views

urlpatterns = [
    path('load-materials/<str:course_id>',
         views.load_course_materials, name='load_materials'),
    path('create/', views.add_materials_webhooks, name='material-create'),
    path('upload-material/<int:course_id>/',
         views.UploadCourseContentAPIView.as_view()),
    path('delete-material/<int:course_id>/<str:file_id>/',
         views.delete_course_content),
]
