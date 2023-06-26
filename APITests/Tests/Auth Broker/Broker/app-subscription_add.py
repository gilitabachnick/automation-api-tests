import requests
from authbroker import *


headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://auth.nvq1.ovp.kaltura.com/api/v1", "/app-subscription", "/add")
payload_1 = {
  "name": app_name_value,
  "appGuid": app_guid_value,
  "authProfileIds": authprofileids_value,
  "appLandingPage": applandingpage_value,
  "appErrorPage": apperrorpage_value,
  "description": app_description_value,
  "userProfileAttributeMappings": {},
  "appLogoutPage": applogoutpage_value,
  "ksPrivileges": ksprivileges_value,
  "userIdAttribute": useridattribute_value
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




