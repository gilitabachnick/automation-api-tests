import requests
from authbroker import *
import json

headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept': 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://user.nvq1.ovp.kaltura.com/api/v1", "/user-profile", "/getbyFilter")
payload_1 = {
  "idIn": [
    "string"
  ],
  "appGuidIn": [
    "string"
  ],
  "userIdIn": [
    "string"
  ],
  "status": "enabled",
  "attendanceStatus": "created",
  "previousAttendanceStatus": "created",
  "createdAtGreaterThanOrEqual": "2023-04-21T12:05:11.576Z",
  "createdAtLessThanOrEqual": "2023-04-21T12:05:11.576Z",
  "updatedAtGreaterThanOrEqual": "2023-04-21T12:05:11.576Z",
  "updatedAtLessThanOrEqual": "2023-04-21T12:05:11.576Z"
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)


