import requests
from authbroker import *


headers_1 = {'Authorization': "Bearer " + KS + '"', 'Accept': 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://auth.nvq1.ovp.kaltura.com/api/v1", "/app-subscription", "/updatePermissionList")
payload_1 = {
    "id": app_id_value,
    "permissionListStatus": permissionliststatus_value,
    "permissionList": permissionlist_value
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)




