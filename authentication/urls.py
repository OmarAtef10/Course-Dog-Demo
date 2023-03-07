from django.urls import path, include
from . import views

urlpatterns = [
    path('send-email/', views.send_email_api, name='send-email'),
    path('send-mass-email/', views.send_mass_email_api, name='send-mass-email'),
    path('activate-user/<str:uid>/<str:token>/', views.ActivateUser.as_view()),
    path('reset/password/<str:uid>/<str:token>/',
         views.ResetUserPassword.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
