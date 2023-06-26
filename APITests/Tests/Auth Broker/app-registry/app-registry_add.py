import requests
from authbroker import *


headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest(appregistryurl, "/app-registry", "/add")
payload_1 = {
  "appCustomId": "string",
  "appType": "kms",
  "appCustomName": "string"
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




