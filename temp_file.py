# 1. Import the requests library
import io
import os

import requests

URL = "https://lookaside.fbsbx.com/whatsapp_business/attachments/?mid=712648577170884&ext=1677517067&hash=ATs-xr2tbcwHvlCuyPlBzDg9arZDnoef4pvoxdupmMyf8w"
print(URL.split('/')[3])
filename = URL.split('/')[-1]
filename = filename.split('?')[0]
filename = "Whatsapp Doc.pdf"
print(filename)
path = os.path.join('uploads/media', filename)
# 2. download the data behind the URL
headers = {
    'Authorization': 'Bearer EAAQMJrRQMU0BAIR7hUa1A9pD4tWroJrWsDSZBJTwEktAyGcXB8ZBIW7CSHBCCCiZC5ygZAdE1aec8h0xgktYK4i69ssUKN1JEI5DEguvGiX8Dy8386IYbbOH19m22CGJQUJ8orZCKSEffEv18aoCDltnWt0I7ZBfjnZCxeoj0xeavd2txsoBqpQyO6NUJWs1EJqX1i4YtCRJwZDZD'
}
response = requests.get(URL , headers=headers)
open(path, "wb").write(response.content)
