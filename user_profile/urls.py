from django.urls import path, include
from .views import get_user_by_fb_name, get_user_by_phone_number

urlpatterns = [
    path('user-by-fb-name/<str:fb_name>', get_user_by_fb_name, name="get_user_by_fb_name"),
    path('user-by-phone-number/<str:phone_number>', get_user_by_phone_number, name="get_user_by_phone_number"),
]
