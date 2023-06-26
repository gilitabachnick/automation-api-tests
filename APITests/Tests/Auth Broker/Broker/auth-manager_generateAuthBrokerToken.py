import requests
from authbroker import *

#generate login request that will be sent back to the broker via redirect


headers_1 = {'Authorization': "Bearer " + KS + '"', 'Accept': 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://auth.nvq1.ovp.kaltura.com/api/v1", "/auth-manager", "/generateAuthBrokerToken")
payload_1 = {
  "authProfileId": authprofileid_value,
  "appGuid": app_guid_value,
  "origURL": "string"
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




