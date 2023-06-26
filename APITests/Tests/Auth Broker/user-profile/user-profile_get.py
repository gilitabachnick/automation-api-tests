import requests
from authbroker import *
import json

headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept': 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://user.nvq1.ovp.kaltura.com/api/v1", "/user-profile", "/get")
payload_1 = {
    "id": userprofileid_value
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)


