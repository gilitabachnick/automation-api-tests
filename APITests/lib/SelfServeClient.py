
import json
import os
import hashlib
import ClienSession
import Config

import requests

#############################################################
#    These classes are Client API to self serve
#    1) packageManager class - deals with packages actions
#    2) purchasManager class - deals with purchas actions
#
#   Authors - Adi MIller, Zeev Shulman
#
#
#############################################################

##################
'''
@CONSTANTS
'''
##################
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

EMAIL_VALIADATION_SECRET= inifile.RetIniVal('SelfServe','EMAIL_VALIADATION_SECRET')
PASSWORD = inifile.RetIniVal('SelfServe','PASSWORD')

# ===========================================================================
#   @dictionaries of arguments used as inputs in selfServe API tests
#       dict_plan: plan strings
#       dict_subscription_json: subscription jsons
#       dict_card_json: credit card, billing info jsons
# ===========================================================================
dict_plan = {
"classroom-free": "virtual-classroom-free-trial", # "prod-virtual-classroom-free-trial",
"webinars-free-isProd" : "webinars-free-trial",
"webinars-free" : "Prod_webinars-free-trial", # The kpf-dev webinars-free plan has the word prod the prod plan does not
"vpass-free"    :"media-services-free-trial",
"classroom-pro"             :"prod-virtual-classroom-pro",
"classroom-pro-addon"       :"prod-virtual-classroom-pro",
"classroom-standard-monthly":"prod-virtual-classroom-standard",#
"classroom-pro-monthly"     :"prod-virtual-classroom-pro",
"vpass-6000":"media-services-payasyougo",
"vpass-pay" :"media-services-payasyougo"
}
dict_subscription_json = {
"classroom-free":'{"partner_id":0,"plan":{"name":"kme-virtual-classroom-free-trial","quantity":1},"addons":[],"product":"KME","billing_cycle":"Monthly","currency":"USD"}',
"webinars-free" :'{"partner_id":0,"plan":{"name":"kme-webinars-free-trial","quantity":1},"addons":[],"product":"KME","billing_cycle":"Yearly","currency":"USD"}',
'vpass-free'    :'{"partner_id":0,"plan":{"name":"Media-Services-Free-Trial_v3","quantity":1},"addons":[],"product":"VPAAS","billing_cycle":"Monthly","currency":"USD"}',
"classroom-pro"             :'{"partner_id":0,"plan":{"name":"kme-virtual-classroom-pro","quantity":2},"addons":[],"product":"KME","billing_cycle":"Yearly","currency":"USD"}',
"classroom-pro-addon"       :'{"partner_id":0,"plan":{"name":"kme-virtual-classroom-pro","quantity":2},"addons":[{"name":"kme-recording-transcoding-eng","quantity":1}],"product":"KME","billing_cycle":"Yearly","currency":"USD"}',
"classroom-standard-monthly":'{"partner_id":0,"plan":{"name":"kme-virtual-classroom-basic","quantity":1},"addons":[],"product":"KME","billing_cycle":"Monthly","currency":"USD"}',
"classroom-pro-monthly"     :'{"partner_id":0,"plan":{"name":"kme-virtual-classroom-pro","quantity":3},"addons":[{"name":"kme-recording-transcoding-eng","quantity":3}],"product":"KME","billing_cycle":"Monthly","currency":"USD"}',
"vpass-6000":'{"partner_id":0,"plan":{"name":"media-services-pay-as-you-go","quantity":1},"addons":[{"name":"media-services-credit-6000","quantity":1}],"product":"VPAAS","billing_cycle":"Yearly","currency":"USD"}',
"vpass-pay" :'{"partner_id":0,"plan":{"name":"media-services-pay-as-you-go","quantity":1},"addons":[],"product":"VPAAS","billing_cycle":"Yearly","currency":"USD"}'
}
dict_card_json = {
"card_ok"      :'{"billing_info":{"countery_code":"US","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500","state_code":"WA"},"tokenId": "e81dba0a1841154920ca43c470d6e148_eyJudW1iZXIiOjQxMTExMTExMTExMTExMTEsImN2diI6OTk5LCJleHBpcnlfeWVhciI6MjYsImV4cGlyeV9tb250aCI6MTJ9Cg"}',
"card_fail"    :'{"billing_info":{"countery_code":"US","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500","state_code":"WA"},"tokenId": "e81dba0a1841154920ca43c470d6e148_eyJudW1iZXIiOjQxMTk4NjI3NjAzMzgzMjAsImN2diI6OTk5LCJleHBpcnlfeWVhciI6MjYsImV4cGlyeV9tb250aCI6MTJ9Cg"}',
#"card_no_funds":'{"billing_info":{"countery_code":"US","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500","state_code":"WA"},"tokenId": "e81dba0a1841154920ca43c470d6e148_eyJudW1iZXIiOjQwMDU1MTkyMDAwMDAwMDQsImN2diI6OTk5LCJleHBpcnlfeWVhciI6MjYsImV4cGlyeV9tb250aCI6MTJ9Cg"}',
"card_no_funds": '{"billing_info":{"countery_code":"US","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500","state_code":"WA"},"tokenId": "e81dba0a1841154920ca43c470d6e148_eyJudW1iZXIiOjQwMDAwMDAwMDAwMDk5OTUsImN2diI6OTk5LCJleHBpcnlfeWVhciI6MjYsImV4cGlyeV9tb250aCI6MTJ9Cg"}',
#---NEW--- "card_no_funds": '{"billing_info":{"countery_code":"US","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500","state_code":"WA"},"tokenId": "e81dba0a1841154920ca43c470d6e148_eyJudW1iZXIiOjQwMDAwMDAwMDAwMDk5OTUsImN2diI6OTk5LCJleHBpcnlfeWVhciI6MjYsImV4cGlyeV9tb250aCI6MTJ9Cg"}',
# "card_ok"      :'{"number":"4111 1111 1111 1111","cvv":"123","expiryMonth":1,"expiryYear":2030,"billing_info":{"countery_code":"US","state_code":"WA","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500"}}',
# "card_fail"    :'{"number":"4119 8627 6033 8320","cvv":"123","expiryMonth":1,"expiryYear":2030,"billing_info":{"countery_code":"US","state_code":"WA","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500"}}',
# "card_no_funds":'{"number":"4005 5192 0000 0004","cvv":"123","expiryMonth":1,"expiryYear":2030,"billing_info":{"countery_code":"US","state_code":"WA","city":"Washington","address":"Pennsylvania avenue 1600","zip_code":"20500"}}'
}


class purchasManager():

    def __init__(self, isProd=False):
        if isProd:
            self.prtnerURL = "https://subscription.kaltura.com/purchase-manager/partner"
            self.cartURL = "https://subscription.kaltura.com/purchase-manager/cart"
            self.emailValidation = "https://subscription.kaltura.com/purchase-manager/email-validation"
        else:
            self.prtnerURL = "https://kpf-dev-react.kaltura.com/purchase-manager/partner"
            self.cartURL = "https://kpf-dev-react.kaltura.com/purchase-manager/cart"
            self.emailValidation = "https://kpf-dev-react.kaltura.com/purchase-manager/email-validation"

        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9'}

        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
        if isProd:
            self.inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        else:
            self.inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))


    def placeJwtTokenInHeader(self, pId, pSecret):
        jwtToken = self.postPartnerLoginByKs(pId, pSecret)
        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9',
                        'Authorization': 'Bearer ' + str(jwtToken)}
        return self.headers

    '@createMD5Hash'
    # get_ui_hash() is used as this doesn't work yet
    def createMD5Hash(self, email, packageID, context="EmailValidation", hash_ui=""):

        # try:
        #     r = requests.get(self.packageURL+ "/hash/"+ str(phash),
        #         headers=self.headers)
        #
        # except Exception as Exp:
        #     print("fail to get package with hash: " + str(phash))
        #     print(Exp)
        #     return False


        print(hash_ui)
        strtohash = [EMAIL_VALIADATION_SECRET, email, packageID, context]
        str = '|'.join(strtohash)
        try:
            #strtohash = "iuhweiurt23452!!|ravit.shalem12121@kaltura.com|Media-Services-Free-Trial-v3-package|EmailValidation"  = 6399a1807d4572b66898d6a5879ec6b2
            hash5 = hashlib.md5(str.encode()).hexdigest()
            return hash5
        except Exception as Exp:
            print(Exp)
            return False

    "@postPartnerLogin"
    def postPartnerLogin(self, email, pwd):

        data_json = json.dumps({  "email": "" + email +"",
                                  "password": "" + pwd +""
                                })

        try:
            r = requests.post(self.prtnerURL + "/login",
                               data=data_json,
                               headers=self.headers)

        except Exception as Exp:
            print("fail to post login : with the useremail =" + str(email) + " and password=" + str(pwd))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to post login : with the useremail =" + str(email) + " and password=" + str(pwd))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@postPartnerRegister"
    def putPartnerRegister_UIhash(self, firstName, lastName, email, company, jobTitle, pwd, ui_hash, allow_marketing=False):

        data_json = json.dumps({"firstName": "" + firstName + "",
                                "lastName": "" + lastName + "",
                                "company": "" + company + "",
                                "jobTitle": "" + jobTitle + "",
                                "password": "" + pwd + "",
                                "allowRecivingMarketingData": allow_marketing
                                })

        phash = ui_hash
        try:
            r = requests.put(self.prtnerURL + "/register/" + phash,
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to post login : with the useremail =" + str(email) + " and password=" + str(pwd))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - putPartnerRegister")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@putPartnerCard"
    def putPartnerCard_UIhash(self, billing_json, jwtToken):
        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9',
                        'Authorization': 'Bearer ' + str(jwtToken)}
        try:
            r = requests.put(self.prtnerURL + "/card",
                             data=billing_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to put partner card")
            print(Exp)
            return False

        if r.status_code == 406 and "insufficient funds" in r.text:
            insufficient_funds = True
        else:
            insufficient_funds = False

        if (r.status_code != 200 and r.status_code != 201) and insufficient_funds != True:
            print("fail to put partner card")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@getPartnerCredit"
    def getPartnerCredit(self, partnerID, pSecret):

        ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')

        self.mySess = ClienSession.clientSession(partnerID, ServerURL, pSecret)

        ks = self.mySess.GetKs()[2]

        try:
            r = requests.get(self.prtnerURL + "/credit/" + str(partnerID) + "/" + ks,
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to get partner credit : with the partner id =" + str(partnerID) )
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get partner credit : with the partner id =" + str(partnerID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@getPartnerPaymentInfo"
    def getPartnerPaymentInfo(self, partnerID, pSecret):

        ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        self.mySess = ClienSession.clientSession(partnerID, ServerURL, pSecret)
        ks = self.mySess.GetKs()[2]
        try:
            r = requests.get(self.prtnerURL + "/paymentInfo/" + str(partnerID) + "/" + ks,
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to get partner payment info : with the partner id =" + str(partnerID))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get partner payment info : with the partner id =" + str(partnerID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@postPartnerLoginByKs"  # this will create the tokken to put in headers of all methods
    def postPartnerLoginByKs(self, partnerID, pSecret):

        ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')

        self.mySess = ClienSession.clientSession(partnerID, ServerURL, pSecret)

        ks = self.mySess.GetKs()[2]

        data_json = json.dumps({"ks": "" + ks + ""})

        try:
            r = requests.get(self.prtnerURL + "/paymentInfo/" + str(partnerID) + "/long",
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to get partner payment info : with the partner id =" + str(partnerID))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get partner payment info : with the partner id =" + str(partnerID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@patchUpdatePartnerStatus"
    def patchUpdatePartnerStatus(self, partnerID, istatus):

        try:
            r = requests.patch(self.prtnerURL + "/updatePartnerStatus/" + str(partnerID) + "/" + istatus,
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to update partner status : with the partner id =" + str(partnerID))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to update partner status : with the partner id =" + str(partnerID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@postCart"
    def postCart(self, cartID, scheme):

        try:
            r = requests.post(self.cartURL,
                               data=scheme,
                               headers=self.headers)

        except Exception as Exp:
            print("fail to post cart : with the partner id =" + str(cartID))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to post cart with the cartID id =" + str(cartID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@getCart"
    def getCart(self):

        try:
            r = requests.get(self.cartURL,
                               data="",
                               headers=self.headers)

        except Exception as Exp:
            print("fail to get cart")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get cart")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@getCartByEmail"
    def getCartByEmail(self, email):
        hash = self.createMD5Hash(email)
        try:
            r = requests.get(self.cartURL + "/" + str(hash),
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to get cart by email: " + str(email))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get cart by email: " + str(email))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@patchCartId"
    def patchCartId(self, cartId):
        try:
            r = requests.get(self.cartURL + "/" + str(cartId),
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to patch cart by Id: " + str(cartId))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to patch cart by Id: " + str(cartId))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@deleteCartById"
    def deleteCartById(self, cartId):

        try:
            r = requests.delete(self.cartURL + "/" + str(cartId),
                             data="",
                             headers=self.headers)

        except Exception as Exp:
            print("fail to delete cart by Id: " + str(cartId))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to delete cart by Id: " + str(cartId))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@postEmailValidation"
    def postEmailValidation(self, scheme):

        data_jason = scheme

        try:
            r = requests.post(self.emailValidation,
                                data=data_jason,
                                headers=self.headers)

        except Exception as Exp:
            print("fail to post email validation for: " + str(scheme))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:# or r.status_code != 201:
            print("fail to post email validation for: " + str(scheme))
            print("Err: " + str(r.status_code) + " text: " +str(r.text))
            return False
        else:
            return r


class packageManager():

    def __init__(self, isProd=False):
        if isProd:
            self.packageURL              = "https://subscription.kaltura.com/package-manager/package"
            self.planURL                 = "https://subscription.kaltura.com/package-manager/plan"
            self.subscriptionURL         = "https://subscription.kaltura.com/package-manager/subscription"
            self.subscriptionCreateURL   = "https://subscription.kaltura.com/package-manager/subscription/create"
            self.subscriptionOverViewURL = "https://subscription.kaltura.com/package-manager/subscription-overview"
        else:
            self.packageURL              = "https://kpf-dev-react.kaltura.com/package-manager/package"
            self.planURL                 = "https://kpf-dev-react.kaltura.com/package-manager/plan"
            self.subscriptionURL         = "https://kpf-dev-react.kaltura.com/package-manager/subscription"
            self.subscriptionCreateURL   = "https://kpf-dev-react.kaltura.com/package-manager/subscription/create" # "http://kpf-dev.kaltura.com/package-manager/subscription"#
            self.subscriptionOverViewURL = "https://kpf-dev-react.kaltura.com/package-manager/subscription-overview"

        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9'}

    def placeJwtTokeninHeader(self, pId, Psecret):
        purchmanager = purchasManager(self.isProd)
        self.headers = purchmanager.placeJwtTokenInHeader(pId, Psecret)


    '@postPackage'
    def postPackage(self, dataJson):

        data_json = json.dumps(dataJson)

        try:
            r = requests.post(self.packageURL,
                   data=data_json,
                   headers=self.headers)


        except Exception as Exp:
            print("fail to post package with the folowing json: " + dataJson)
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to post package with the folowing json: " + dataJson)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r



    '@getPackageList'
    def getPackageList(self):

        try:
            r = requests.get(self.packageURL,
                headers=self.headers)

        except Exception as Exp:
            print("fail to get package list")
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to get package list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            print(r.json())
            return r


    '@getPackageById'
    def getPackageById(self,pid):

        try:
            r = requests.get(self.packageURL+ "/"+ str(pid),
                headers=self.headers)

        except Exception as Exp:
            print("fail to get package with ID: " + str(pid))
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to get package with ID: " + str(pid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@getPackageByName'
    def getPackageByName(self,pname):

        try:
            r = requests.get(self.packageURL+ "/name/"+ str(pname),
                headers=self.headers)

        except Exception as Exp:
            print("fail to get package name: " + str(pname))
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to get package name: " + str(pname))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@getPackageHash'
    def getPackageHash(self,email):

        phash = self.createMD5Hash(email)

        try:
            r = requests.get(self.packageURL+ "/hash/"+ str(phash),
                headers=self.headers)

        except Exception as Exp:
            print("fail to get package with hash: " + str(phash))
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to get package with hash: " + str(phash))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@patchPackage'
    def patchPackage(self, pid, scheme):

        data_json = json.dumps(scheme)

        try:
            r = requests.patch(self.packageURL+ "/"+ str(pid),
                data=data_json,
                headers=self.headers)

        except Exception as Exp:
            print("fail to patch package ID: " + str(pid) + " with the json=" + scheme)
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to patch package ID: " + str(pid) + " with the json=" + scheme)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@deletePackage'
    def deletePackage(self,pid):

        try:
            r = requests.delete(self.packageURL+ "/"+ str(pid),
                headers=self.headers)

        except Exception as Exp:
            print("fail to delete package ID = " + pid)
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to delete package ID = " + pid)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '-------- @@ PLAN Methods @@ ------'

    '@postPlan'
    def postPlan(self, dataJson):

        data_json = json.dumps(dataJson)

        try:
            r = requests.post(self.planURL,
                   data=data_json,
                   headers=self.headers)

        except Exception as Exp:
            print("fail to post plan with the following jason=" + dataJson)
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to post plan with the following jason=" + dataJson)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@getPlanList'
    def getPlanList(self):

        try:
            r = requests.get(self.planURL,
                headers=self.headers)

        except Exception as Exp:
            print("fail to get plan list")
            print(Exp)
            return False

        if r.status_code!=200:
            print("fail to get plan list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@getPlanList'
    def getPlanByName(self, plname):

        try:
            r = requests.get(self.planURL + "/" + str(plname),
                headers=self.headers)

        except Exception as Exp:
            print("fail to get plan with name=" + str(plname))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get plan with name=" + str(plname))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@patchPlan'
    def patchPlan(self, plname, scheme):

        data_json = json.dumps(scheme)

        try:
            r = requests.patch(self.planURL + "/" + str(plname),
                data=data_json,
                headers=self.headers)

        except Exception as Exp:
            print("fail to patch plan name: " + str(plname) + " with the json=" + scheme)
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to patch plan name: " + str(plname) + " with the json=" + scheme)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@deletePlanById'
    def deletePlanById(self, plid):

        try:
            r = requests.delete(self.planURL + "/" + str(plid),
                             headers=self.headers)

        except Exception as Exp:
            print("fail to delete plan with ID=" + str(plid))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to delete plan with ID=" + str(plid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@postingPlanPricingInfo'
    def postingPlanPricingInfoByName(self, plname):

        try:
            r = requests.post(self.planURL + "/pricinginfo/" + str(plname),
                                headers=self.headers)

        except Exception as Exp:
            print("fail to post plan name=" + str(plname))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to post plan name=" + str(plname))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@getPlanAnaliticsRef'
    def getPlanAnaliticsRef(self, refid):

        try:
            r = requests.get(self.planURL + "/kaltura_analytic_ref/" + str(refid),
                headers=self.headers)

        except Exception as Exp:
            print("fail to get plan analytics with refID=" + str(refid))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get plan analytics with refID=" + str(refid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@postSubscription'
    def postSubscription_UIhash(self, ui_hash, is_json, jwtToken):
        data_json = is_json
        phash = ui_hash
        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9',
                        'Authorization': 'Bearer ' + str(jwtToken)}

        try:
            r = requests.post(self.subscriptionCreateURL + "/" + str(phash),
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to post subscription : with the json=" + is_json)
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to post subscription : with the json=" + is_json)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    '@getSubscriptionByPartner'
    def getSubscriptionPartner(self, partnerID, jwtToken):
        self.headers = {'accept': '*/*',
                        'Content-type': 'application/json',
                        'kalturainternalheader': 'ainternal_secret9',
                        'Authorization': 'Bearer ' + str(jwtToken)}
        try:
            # 'https://kpf-dev.kaltura.com/package-manager/subscription/partner/1928' "/"
            r = requests.get(self.subscriptionURL + "/partner/"+partnerID,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to put partner card")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get partner credit : with the partner id =" + str(partnerID))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    '@getSubscriptionById'
    def getSubscriptionById(self, sid):

        try:
            r = requests.get(self.subscriptionURL + "/id/" + str(sid),
                             headers=self.headers)

        except Exception as Exp:
            print("fail to get subscription with subscription ID=" + str(sid))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get subscription with subscription ID=" + str(sid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@patchSubscriptionById'
    def patchSubscriptionById(self, sid, scheme):

        data_json = json.dumps(scheme)

        try:
            r = requests.patch(self.subscriptionURL + "/" + str(sid),
                               data=data_json,
                               headers=self.headers)

        except Exception as Exp:
            print("fail to patch subscription with id= " + str(sid) + " with the json=" + scheme)
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to patch subscription with id= " + str(sid) + " with the json=" + scheme)
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    '@deleteSubscriptionById'
    def deleteSubscriptionById(self, sid):

        try:
            r = requests.delete(self.subscriptionURL + "/" + str(sid),
                             headers=self.headers)

        except Exception as Exp:
            print("fail to delete subscription with subscription ID=" + str(sid))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to delete subscription with subscription ID=" + str(sid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@increasePlanUsage"
    def postIncreasePlanUsage(self, sid, pname):

        try:
            r = requests.post(self.subscriptionURL + "/inreasePlanUsage/" + str(sid) + "/" + str(pname),
                             headers=self.headers)

        except Exception as Exp:
            print("fail to increase plan usage subscription ID=" + str(sid) + " and plan name=" + str(pname))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to increase plan usage subscription ID=" + str(sid) + " and plan name=" + str(pname))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    "@decreasePlanUsage"
    def decreasePlanUsage(self, sid, pname):

        try:
            r = requests.post(self.subscriptionURL + "/decreasePlanUsage/" + str(sid) + "/" + str(pname),
                              headers=self.headers)

        except Exception as Exp:
            print("fail to decrease plan usage subscription ID=" + str(sid) + " and plan name=" + str(pname))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to decrease plan usage subscription ID=" + str(sid) + " and plan name=" + str(pname))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


    "@getLoginUrl"
    def getLoginUrl(self, sid):

        try:
            r = requests.get(self.subscriptionURL + "/getLoginUrl/" + str(sid),
                              headers=self.headers)

        except Exception as Exp:
            print("fail to get login url with subscription ID=" + str(sid))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to get login url with subscription ID=" + str(sid))
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    '@postSubscriptionOverView'
    def postSubscriptionOverView(self):

        try:
            r = requests.post(self.subscriptionOverViewURL,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to Subscription Over View")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("fail to Subscription Over View")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r


# ============================================
# Gets hash from email
# ============================================
import MySelenium
import time
def get_ui_hash(self, user):
    try:
        Wdobj = MySelenium.seleniumWebDrive()
        Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
        usr = user.replace("@mailinator.com", "") + "\n"
        Wd.get("https://www.mailinator.com/v4/public/inboxes.jsp?to=" + usr)
        reg_mail_xp = "//*[contains(text(),'Kaltura')]"
        link_txt_xp = '//*[@id="pills-json-content"]/pre'
        time.sleep(5)
        Wd.find_element_by_xpath(reg_mail_xp).click()
        time.sleep(3)
        Wd.find_element_by_xpath("//*[contains(text(),'JSON')]").click()
        time.sleep(1)
        txt = str(Wd.find_element_by_xpath(link_txt_xp).text)
        txt_chunks = txt.split("validation/")
        ui_hash = txt_chunks[1][:32]
        Wd.quit()
        return ui_hash
    except Exception as Exp:
        print(Exp)
        return False

def email_validation_form1(self, email, package):
    try:

        recaptcha_token = self.inifile.RetIniVal('SelfServe', 'recaptcha_token')

        will_be_jason = {"email": email, "desiredPackageId": package, "recaptchaToken": recaptcha_token}
        is_jason = json.dumps(will_be_jason)
        rc = self.PurcheseManager.postEmailValidation(is_jason)
        if rc:
            return rc
        else:
            return False
    except Exception as Exp:
        print(Exp)
        return False

# def chargeBe_CC_UI(self, UI_hash, data=""):
#     import pickle
#     try:
#         Wdobj = MySelenium.seleniumWebDrive()
#         Wd = Wdobj.RetWebDriverLocalOrRemote("chrome")
#         Wd.get('https://kpf-dev.kaltura.com/purchase/plan/' + UI_hash)
#         Wd.find_element_by_xpath("//span[contains(text(),'Continue')]").click()
#         # Wd.get("https://kpf-dev.kaltura.com/purchase/checkout")
#
#         Wd.find_element_by_xpath('//input[@id="address"]').send_keys('aaa')
#         Wd.find_element_by_xpath('//input[@id="city"]').send_keys('Washington')
#         # Wd.find_element_by_xpath("//span[contains(text(),'Select')]").send_keys('Afghanistan')
#         Wd.find_element_by_xpath('//input[@id="zip"]').send_keys("1234")
#         Wd.switch_to.frame("cb-component-number-0")
#         Wd.find_element_by_xpath('//input[@id="cardnumber"]').send_keys("4111111111111111")
#         Wd.switch_to.parent_frame()
#         Wd.switch_to.frame("cb-component-expiry-1")
#         Wd.find_element_by_xpath('//input[@id="exp-date"]').send_keys('0230')
#
#         Wd.switch_to.parent_frame()
#         Wd.switch_to.frame("cb-component-cvv-2")
#         Wd.find_element_by_xpath('//input[@name="cvv"]').send_keys('123')
#         Wd.switch_to.default_content()
#         Wd.find_element_by_xpath('//input[@id="nameOnCard"]').send_keys('Ploni the younger')
#
#         Wd.find_element_by_xpath("//span[contains(text(),'Purchase Now')]").click()
#        #<span class="p-button-label">Purchase Now</span>  //input[@name="cvv"]
#
#         print("x")
#         return True
#     except Exception as Exp:
#         print(Exp)
#         return False


