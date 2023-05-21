from django.urls import path, include
from .views import get_user_by_fb_name, get_user_by_phone_number, read_pickle, get_tokens, check_user, logged_out

urlpatterns = [
    path('user-by-fb-name/<str:fb_name>', get_user_by_fb_name, name="get_user_by_fb_name"),
    path('user-by-phone-number/<str:phone_number>', get_user_by_phone_number, name="get_user_by_phone_number"),
    path('read-pickle/', read_pickle, name="read_pickle"),
    path('get-tokens/', get_tokens, name="get_tokens"),
    path('check/', check_user, name="check_user"),
    path('logged-out/', logged_out, name="logged_out"),

]
