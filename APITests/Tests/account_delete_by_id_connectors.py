from Connectors import *
import requests

request_1 = sendRequest('https://connectors.nvq1.ovp.kaltura.com/api/v1', "/account", "/delete")
header_1 = header({"Authorization": "KS Njk3OGY4ZWYzYjE0NTc5ODgwOTcxYjM0MWNiNGZkZTZmM2IzOGJlMnw5MDA2OTU4OzkwMDY5NTg7MTY2NjQzNDIxMjsyOzE2NjYzNDc4MTIuOTc4OTtnZW9yZ2UuZGlhY29uZXNjdUBrYWx0dXJhLmNvbTsqLGRpc2FibGVlbnRpdGxlbWVudDs7"})
body_1 = body({"id": "630e15dcff1002390383bb94"})

response = requests.post(request_1.url, headers=header_1.auth, json=body_1.body)

print(response.text)

#if an account has associated instances it can not be deleted, "OBJECT_IN_USE"