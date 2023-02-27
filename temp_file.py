# 1. Import the requests library
import io
import os

import requests

URL = "https://cdn.fbsbx.com/v/t59.2708-21/316149989_1727538644298619_4412847868712000302_n.pdf/Lecture01_Introduction.pdf?_nc_cat=103&ccb=1-7&_nc_sid=0cab14&_nc_ohc=pdAehx51NgsAX-oI99C&_nc_ht=cdn.fbsbx.com&oh=03_AdR7OjyVH43_BRA9DuIfoTdczl8P7qABxt_Rvo8Pu0wUJQ&oe=63FD2198"
filename = URL.split('/')[-1]
filename = filename.split('?')[0]
print(filename)
path = os.path.join('uploads/media', filename)
# 2. download the data behind the URL
response = requests.get(URL)
open(path, "wb").write(response.content)
