from django.urls import path
from .views import *

urlpatterns = [
    path("", OrganizationViewSet.as_view(), name="organization"),
    path('organization-details/', OrganizationAPIView.as_view(),
         name='organization-details'),
    path('organization-admins/', OrganizationAdminsDataAPIView.as_view()),
    path("<str:name>/", get_organization, name="get_organization"),
]
