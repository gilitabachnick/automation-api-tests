from Connectors import *
import requests

request_1 = sendRequest('https://connectors.nvq1.ovp.kaltura.com/api/v1', "/template", "/update")
header_1 = header({"Authorization": "KS Njk3OGY4ZWYzYjE0NTc5ODgwOTcxYjM0MWNiNGZkZTZmM2IzOGJlMnw5MDA2OTU4OzkwMDY5NTg7MTY2NjQzNDIxMjsyOzE2NjYzNDc4MTIuOTc4OTtnZW9yZ2UuZGlhY29uZXNjdUBrYWx0dXJhLmNvbTsqLGRpc2FibGVlbnRpdGxlbWVudDs7"})
body_1 = body({
  "id": "string",
  "name": "string",
  "systemName": "string",
  "description": "string",
  "integrationTags": [
    "string"
  ],
  "providerTemplateId": "string",
  "provider": "tray_kaltura",
  "integration": "marketo",
  "supportedEvents": [
    {
      "name": "string",
      "eventObjectType": "registrationInfo",
      "eventTypes": [
        "kObjectCreatedEvent"
      ],
      "description": "string",
      "mandatory": false
    }
  ],
  "instanceParams": [
    {
      "displayName": "string",
      "key": "string",
      "exampleValue": "string",
      "description": "string",
      "isRequired": true,
      "configWizardRequired": true,
      "helpDocLink": "string"
    }
  ],
  "linkParams": [
    {
      "displayName": "string",
      "key": "string",
      "exampleValue": "string",
      "description": "string",
      "isRequired": True,
      "configWizardRequired": True,
      "helpDocLink": "string"
    }
  ],
  "logoUrl": "string"
})

response = requests.post(request_1.url, headers=header_1.auth, json=body_1.body)

print(response.text)

