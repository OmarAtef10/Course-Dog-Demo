from user_profile.views import creds_refresher
from social_django.models import UserSocialAuth
CLIENT_SECRET_FILE = "client_secret_file.json"
API_NAME = "drive"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

service = build(API_NAME, API_VERSION, 
folder_id = "oausgdiuagsdi"
query = f"parents= '{folder_id}'"

response = service.files().list(
    pageSize=10, fields="nextPageToken, files(id, name)", q=query).execute()
files = response.get("files")
nextPageToken = response.get("nextPageToken")

for item in files:
    print(u'{0} ({1})'.format(item['name'], item['id']))
