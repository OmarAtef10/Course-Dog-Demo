import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request

from allauth.socialaccount.models import SocialAccount, SocialToken

from .serializers import ProfileSerializer
import pickle
from .models import Profile


# Create your views here.


def get_user_profile(user):
    return Profile.objects.get(user=user)


def update_user_profile_organization(user, organization):
    user_profile = Profile.objects.get(user=user)
    user_profile.organization = organization
    user_profile.save()


def get_user_by_fb_name(request, fb_name):
    profile = get_object_or_404(Profile, facebook_username=fb_name)
    serializer = ProfileSerializer(profile)
    return JsonResponse(serializer.data, safe=False)


def get_user_by_phone_number(request, phone_number):
    profile = get_object_or_404(Profile, whatsapp_number=phone_number)
    serializer = ProfileSerializer(profile)
    return JsonResponse(serializer.data, safe=False)


def pickle_freshness_checker(cred, pickle_file):
    CLIENT_SECRET_FILE = "client_secret_file.json"
    SCOPES = ["https://www.googleapis.com/auth/drive",
              "https://www.googleapis.com/auth/classroom.courses",
              "https://www.googleapis.com/auth/classroom.announcements.readonly",
              "https://www.googleapis.com/auth/classroom.courses.readonly",
              "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly"]

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)
    try:
        service = build("drive", "v3", credentials=cred)
        print("drive", 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def read_pickle(request):
    temp_file = Profile.objects.get(user=request.user).oAuth_file.name
    file = open(f"./uploads/{temp_file}", 'rb')
    f = pickle.load(file)
    pickle_freshness_checker(f, f"./uploads/{temp_file}")
    file = open(f"./uploads/{temp_file}", 'rb')
    f = pickle.load(file)

    jfile = json.loads(f.to_json())
    print(jfile)
    print(jfile['token'])
    return Response(jfile, status=status.HTTP_200_OK)


import io

from google.oauth2.credentials import Credentials

import shutil


SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/classroom.courses",
          "https://www.googleapis.com/auth/classroom.announcements.readonly",
          "https://www.googleapis.com/auth/classroom.courses.readonly",
          "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly"]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tokens(request):
    tokens = SocialToken.objects.get(account__user=request.user)
    social_acc = SocialAccount.objects.get(user=request.user)
    creds_data = social_acc.socialtoken_set.first()
    print(creds_data)
    ctx = {"access_token": tokens.token, "refresh_token": tokens.token_secret,
           "client_id": "854703669001-kj8rfqmeu6crm173ocsl3luueh61n16t.apps.googleusercontent.com",
           "client_secret": "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"}

    creds = Credentials.from_authorized_user_info(info=ctx, scopes=SCOPES, )
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print(creds.to_json())
            tokens.token = creds.token
            tokens.token_secret = creds.refresh_token
            tokens.save()
            print('refreshed')
        except Exception as e:
            print(e)
            print('refresh failed')
    service = build("drive", "v3", credentials=creds)
    file_id = "1kAJpel0o6gxVj2r5-6GNqkxqIvnnRxf7"
    request2 = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request2)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    file_name = "test.pdf"
    with open(os.path.join(".", file_name), "wb") as f:
        f.write(fh.read())
    shutil.move(f"./{file_name}", f"./uploads/course_material/{file_name}")

    return Response(ctx, status=200)
