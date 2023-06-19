import io
import os
import shutil

import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


def get_courses(auth_token):
    url = 'https://classroom.googleapis.com/v1/courses'
    headers = {
        'Authorization': 'Bearer ' + auth_token}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        # print(res.json())
        return (res.json())
    else:
        print(res.json())
        return (res.json())


def get_announcements(course_id, auth_token):
    url = 'https://classroom.googleapis.com/v1/courses/' + str(course_id) + '/announcements'
    headers = {
        'Authorization': 'Bearer ' + auth_token
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        # print(res.json())
        return (res.json())
    else:
        print(res.json())
        return (res.json())


def get_coursework(course_id, auth_token):
    url = 'https://classroom.googleapis.com/v1/courses/' +str(course_id) + '/courseWorkMaterials'
    headers = {
        'Authorization': 'Bearer ' + auth_token
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        # print(res.json())
        return (res.json())
    else:
        print(res.json())
        return (res.json())


def download_drive_file(creds, file_name, file_id):
    service = build("drive", "v3", credentials=creds)
    request2 = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request2)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    with open(os.path.join(".", file_name), "wb") as f:
        f.write(fh.read())
    shutil.move(f"./{file_name}", f"./uploads/course_material/{file_name}")


def list_drive_materials(creds,folder_id):
    service = build("drive", "v3", credentials=creds)
    query = f"parents= '{folder_id}'"
    response = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)", q=query).execute()
    files = response.get("files")
    nextPageToken = response.get("nextPageToken")
    ctx = {}
    for item in files:
        print(u'{0} ({1})'.format(item['name'], item['id']))
        ctx[item['name']] = item['id']
    return ctx
