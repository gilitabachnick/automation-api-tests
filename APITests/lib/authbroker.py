import json
class sendRequest:
    def __init__(self, baseUrl, service, action,):
        self.baseUrl = baseUrl
        self.service = service
        self.action = action
        self.url = baseUrl + service + action

class header():
    def __init__(self, auth):
        self.auth = auth


# class body():
#     def __init__(self, body, ):
#         self.body = body
#         # self.body1 = body1


# def get_data():
#     with open('auth.json') as f:
#         data = json.load(f)
#     return data

#json dict with variables for auth-profile

auth_name_value = "test name updated"
providerType_value = "azure"
authStrategy_value = "saml"
#userIdAttribute_value = "idpNameId"
authstrategyconfig_json = {
    "issuer": "external-auth-broker",
    "entryPoint": "https://login.microsoftonline.com/1253f608-fa77-4826-85e7-8f1ba732f457/saml2",
    "callbackUrl": "https://auth.nvq1.ovp.kaltura.com/api/v1/auth-manager/saml/ac",
    "logoutUrl": "logouturl_value",
    "logoutCallbackUrl": "logoutcallbackurl_value",
    "cert": "MIIC8DCCAdigAwIBAgIQXxuvW+Tyf6RDp3/wK6Zf4DANBgkqhkiG9w0BAQsFADA0MTIwMAYDVQQDEylNaWNyb3NvZnQgQXp1cmUgRmVkZXJhdGVkIFNTTyBDZXJ0aWZpY2F0ZTAeFw0yMjEyMDgxNDQ5NTJaFw0yNTEyMDgxNDQ5NTJaMDQxMjAwBgNVBAMTKU1pY3Jvc29mdCBBenVyZSBGZWRlcmF0ZWQgU1NPIENlcnRpZmljYXRlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9RAcNdqpsBZAMQ4rtasuS3iGmmNObtsHckgG7iApQK/obdZOMq8hs3HuqVj/Dg/dcazFCYIqCfkDWhQ5gV1ZGWFL2Tdks/M7iDc05x15ZHyL7GvjX6ciE/h0PwNXE99JPrnXkxFf0CrH9Evh8TFRakg3d/Fl0TtnzaCfiTMicbFVVLIYTNuyG+GUihQWHzbNMbAP2/UmP1WIBWfeV7+iZpKHf8ditmWLQvNUv+7EyvmCFJbx55Gk8vi1H0mRoZy8rFYEGHsH2ajCyV1mqQ0PWCLzG4X8abl99gnkhStghLG9Y8uJzIOyZ6mDw4F+dL811hRgQII3nE8i0aIHpN+srQIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCL3/8xri0cDQlzvWsZQVSC4rXbT6lcROKDrJhmOMXtAhEsHcLvQefb9l3/QyAvp96Blzo28/1u5+yUCi99zCU1pIQemhy5gJvumVcFqLentkOOZ28YQvxHbilvlLr3kVw2Q9NHtsMJnyPqETlkZjjN7yjTS6VmunUMPCyNRClB41JB+2Ls16JrUyn4/dynLDNtHbNnH9/HxBgfDphRZoaLoRne7ToiAHjeT7J5maqTesFGeWCsA2C1SqiuzW+8Me1OgrmEKAmhjfmYbZx8K9yB8oGyksAA+V1IHnUYdzLYc7IMqRBwynClg4taZxHaHXQqrANpDv2gMgmm04n4Xybp",
}
usergroupmappings_json = {
    "http://schemas.microsoft.com/identity/claims/tenantid": "dor_tenant_id",
    "http://schemas.microsoft.com/identity/claims/objectidentifier": "dor_object_dentifier",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "Core_User_FirstName",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "Core_User_LastName",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "Core_User_Email",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "Core_User_FullName",
    "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups": "IDP_Groups"
  }
description_value = "test description"
groupAttributeName_value = "IDP_Groups"
useridattribute_value = "idpNameId"
ksprivileges_value = "string"
#id_value = "64410da86b3aefdd45ff6afb"
app_description_value = "string"
app_name_value = "string"
app_guid_value = "string"
authprofileids_value = [
    "string"
]
authprofileid_value = "64410da86b3aefdd45ff6afb"
applandingpage_value = "string"
apperrorpage_value = "string"
applogoutpage_value = "string"
#permissionlist_value = [
#    "string"
app_id_value = "63ce74ada41ce0726cbae516"
permissionliststatus_value = "allow"
permissionlist_value = [
    "string"
    ]

#json with variables for app-registry@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

appregistryurl = 'string'
userid_value = 'george.diaconescu@kaltura.com'
appregistryid_value = "63c67a22e13849909cb5d286"

#json with variables for user-profile@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

eventdata_json = {
    "regOrigin": "registration",
    "attendanceStatus": "created",
    "previousAttendanceStatus": "created",
    "isRegistered": True
  }
profiledata_value = {}
userprofile_status = "enabled"
logindata_json = {
    "lastLoginDate": "2023-04-21T11:03:58.798Z",
    "lastLoginType": "sso"
  }
userprofileid_value = "63d24b3e5622d20b5ddeaf20"


from KalturaClient import KalturaClient as kClient
# The following constants shall be stored in AWS secret vault later
secret = '2e154b50f7e5f930ada5e6354f49a0f3'
user = 'george.diaconescu@kaltura.com'
partner = 9006958
sessionType = 2  # 2 = admin, 1 = user. If you're generating user KS, use user secret instead of admin
expiry = 86400
privileges = 'disableentitlement'  # Optional. 'disableentitlement' is normal admin privilege
try:
    KS = kClient.generateSession(secret, user, sessionType, partner, expiry, privileges).decode("utf-8")
except Exception as Exp:
    print(Exp)
else:
    print(KS)