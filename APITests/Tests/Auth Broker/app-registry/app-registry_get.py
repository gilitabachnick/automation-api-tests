import requests
from authbroker import *


headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest(appregistryurl, "/app-registry", "/get")
payload_1 = {
  "id": appregistryid_value
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




