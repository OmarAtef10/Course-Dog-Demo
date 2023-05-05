import requests

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
    url = 'https://classroom.googleapis.com/v1/courses/' + course_id + '/announcements'
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
    url = 'https://classroom.googleapis.com/v1/courses/' + course_id + '/courseWorkMaterials'
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

