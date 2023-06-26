import requests
from authbroker import *
import json

headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept': 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://user.nvq1.ovp.kaltura.com/api/v1", "/user-profile", "/add")
payload_1 = {
  "appGuid": app_guid_value,
  "userId": userid_value,
  "profileData": profiledata_value,
  "loginData": logindata_json,
  "eventData": eventdata_json,
  "appData": {},
  "status": userprofile_status
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)


