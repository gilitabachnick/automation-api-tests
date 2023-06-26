import requests
from authbroker import *


headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest(appregistryurl, "/app-registry", "/update")
payload_1 = {
  "appCustomId": "string",
  "appCustomName": "string",
  "id": appregistryid_value,
  "appType": "kms"
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




