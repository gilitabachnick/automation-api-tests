import requests
from authbroker import *

headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://auth.nvq1.ovp.kaltura.com/api/v1", "/auth-profile", "/list")
payload_1 = {
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)
