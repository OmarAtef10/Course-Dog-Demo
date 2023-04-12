from django.urls import path
from .views import *

urlpatterns = [
    path("", OrganizationViewSet.as_view(), name="organization"),
    path('user-organization-details/', OrganizationAPIView.as_view(),
         name='user-organization-details'),
    path('organization-admins/', OrganizationAdminsDataAPIView.as_view()),
    path('organization-data/<str:name>/',
         GeneralOrganizationDataAPIView.as_view()),
    path("<str:name>/", get_organization, name="get_organization"),
]
