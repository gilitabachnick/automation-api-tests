from Connectors import *
import requests

request_1 = sendRequest('https://connectors.nvq1.ovp.kaltura.com/api/v1', "/instance", "/add")
header_1 = header({"Authorization": "KS Njk3OGY4ZWYzYjE0NTc5ODgwOTcxYjM0MWNiNGZkZTZmM2IzOGJlMnw5MDA2OTU4OzkwMDY5NTg7MTY2NjQzNDIxMjsyOzE2NjYzNDc4MTIuOTc4OTtnZW9yZ2UuZGlhY29uZXNjdUBrYWx0dXJhLmNvbTsqLGRpc2FibGVlbnRpdGxlbWVudDs7"})
body_1 = body({
  "configParamValues": [
    {
      "key": "external_kalturauserfields",
      "value": "{'text':'Email'},'value':'email'},{'text':'First Name','value':'firstName'},{'text':'Last Name','value':'lastName'},{'text':'Company','value':'company'}"
    }
  ],
  "name": "string",
  "description": "string",
  "templateId": "string",
  "enabledEvents": [
    {
      "name": "string",
      "eventObjectType": "registrationInfo",
      "eventTypes": [
        "kObjectCreatedEvent"
      ],
      "description": "string",
      "mandatory": False
    }
  ],
  "tags": [
    "string"
  ]
}
)
response = requests.post(request_1.url, headers=header_1.auth, json=body_1.body)

print(response.text)






