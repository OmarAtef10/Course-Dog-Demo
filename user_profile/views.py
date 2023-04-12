from django.shortcuts import render
from .models import Profile
# Create your views here.


def get_user_profile(user):
    return Profile.objects.get(user=user)


def update_user_profile_organization(user, organization):
    user_profile = Profile.objects.get(user=user)
    user_profile.organization = organization
    user_profile.save()
