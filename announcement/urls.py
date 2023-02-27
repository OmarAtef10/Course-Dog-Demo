from rest_framework import routers

from django.urls import path, include
from .views import *

urlpatterns = [
    path(r'', AnnouncementViewSet.as_view({'get': 'list', "post": "create"})),
    path('create/', add_announcement, name='announcement-create'),
]
