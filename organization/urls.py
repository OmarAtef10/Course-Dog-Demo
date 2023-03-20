from django.urls import path
from .views import *

urlpatterns = [
    path("", OrganizationViewSet.as_view(), name="organization"),
    path("<str:name>/", get_organization, name="get_organization")
]
