from rest_framework import routers

from django.urls import path, include
from . import views

urlpatterns = [
    path(r'', views.MaterialViewSet.as_view({'get': 'list', "post": "create"})),
    path('create/', views.add_materials, name='material-create'),
]
