import requests
from authbroker import *

headers_1 = {'Authorization' : "Bearer " + KS + '"', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
request_1 = sendRequest("https://auth.nvq1.ovp.kaltura.com/api/v1", "/auth-profile", "/update")
payload_1 = {
      "id": id_value,
     "name": name_value,
  "providerType": providerType_value,
  "authStrategy": authStrategy_value,
  "userIdAttribute": useridattribute_value,
  "authStrategyConfig": authstrategyconfig_json,
  "description": description_value,
  "groupAttributeName": groupAttributeName_value,
  "userAttributeMappings": {},
  "ksPrivileges": ksprivileges_value,
  "userGroupMappings": usergroupmappings_json
}

r = requests.post (request_1.url, headers=headers_1, json=payload_1)

print(r.text)
