from Connectors import *
import requests

request_1 = sendRequest('https://connectors.nvq1.ovp.kaltura.com/api/v1', "/template", "/add")
header_1 = header({"Authorization": "KS Njk3OGY4ZWYzYjE0NTc5ODgwOTcxYjM0MWNiNGZkZTZmM2IzOGJlMnw5MDA2OTU4OzkwMDY5NTg7MTY2NjQzNDIxMjsyOzE2NjYzNDc4MTIuOTc4OTtnZW9yZ2UuZGlhY29uZXNjdUBrYWx0dXJhLmNvbTsqLGRpc2FibGVlbnRpdGxlbWVudDs7"})
body_1 = body({
  "name": "template3",
  "systemName": "MARKETO_CUSTOM_ACTIVITY",
  "provider": "tray_kaltura",
  "integration": "marketo",
  "providerTemplateId": "de922f79-f092-4bd7-b027-0d02781e9fe5",
  "supportedEvents": [
                {
                    "eventObjectType": "registrationInfo",
                    "eventTypes": [
                        "kObjectCreatedEvent",
                        "kObjectUpdatedEvent",
                        "kObjectDeletedEvent"
                    ]
                },
                {
                    "eventObjectType": "attendanceInfo",
                    "eventTypes": [
                        "kObjectCreatedEvent",
                        "kObjectUpdatedEvent",
                        "kObjectDeletedEvent"
                    ]
                },
                {
                    "eventObjectType": "sessionEngagementReport",
                    "eventTypes": "manual"
                }
 ]
})

response = requests.post(request_1.url, headers=header_1.auth, json=body_1.body)

print(response.text)



