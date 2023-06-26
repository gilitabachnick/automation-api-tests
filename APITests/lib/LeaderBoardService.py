###################################################
#
#
#
###################################################

import os
import time

import requests
import Config
import json
import ClienSession


class GameService():
    def __init__(self,isProd=True, pid=["4800142"]):
        self.pid = pid
        if isProd:
            self.baseURL = 'https://scm.kaltura.com/api/v1/'
            self.healthURL = 'https://scm.kaltura.com/api/v1/health'
            self.leaderboardURL = 'https://scm.kaltura.com/api/v1/leaderboard'
            self.ruleURL = 'https://scm.kaltura.com/api/v1/rule'
            self.userScoreURL = 'https://scm.kaltura.com/api/v1/userScore'
            self.csvURL = 'https://scm.kaltura.com/api/v1/event/sendExternalEventsFromCsv'

            self.certificateURL = 'https://scm.kaltura.com/api/v1/certificate'
            self.certificateReprtURL = 'https://scm.kaltura.com/api/v1/userCertificateReport'
        else:
            # this takes care of the Game service URL, BE URL when needed is done via host file
            self.baseURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/'
            self.healthURL = 'https://scm.nvq1.ovp.kaltura.com/health'
            self.leaderboardURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/leaderboard'
            self.ruleURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/rule'
            self.userScoreURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/userScore'
            self.csvURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/event/sendExternalEventsFromCsv'  # not tested yet

            self.certificateURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/certificate'
            self.certificateReprtURL = 'https://scm.nvq1.ovp.kaltura.com/api/v1/userCertificateReport'


        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'ini'))
        # *** this test doesn't run on QA, only STG with prod params
        self.env = 'prod'  # if isProd else 'testing'
        inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
        # ====================== Normal
        self.UserSecret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
        self.PublisherID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
        mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.UserSecret)

        try:
            self.client = mySess.OpenSession()
            self.KS = self.client.requestConfiguration['ks']
            print(self.KS)

            self.headers = {'accept': '*/*',
                            'Content-type': 'application/json',
                            'Authorization': 'Bearer ' + str(self.KS)}

        except Exception as Exp:
            print(Exp)

# ============ /Leaderboard/Actions ============
    def LBGet(self, LBId):
        data_json = json.dumps({"id": "" + LBId + ""})
        try:
            r = requests.post(self.leaderboardURL + '/get',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to Liderboard/get id: " + str(LBId))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - Liderboard/get")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def LBDelete(self, LBId):
        data_json = json.dumps({"id": "" + LBId + ""})
        try:
            r = requests.post(self.leaderboardURL + '/delete',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to Liderboard/delete id: " + str(LBId))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - Liderboard/delete")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            print("LB: " + LBId + " was disabled")
            return r

    def LBList(self, status="enabled"):
        if status == "enabled" or status == "disabled":
            #data_json = json.dumps({"status": "" + status + ""})
            data_json = json.dumps({"statusEqual": "" + status + ""})
        else:
            # "" gets 'enabled' and 'disabled' LBs
            data_json = ""

        try:
            r = requests.post(self.leaderboardURL + '/list',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to Liderboard/list: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - Liderboard/list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def LBCreate(self, name, description="", status=""):

        willBeLeft  = ["name"]
        willBeRight = [name]
        if len(description) > 0:
            willBeLeft.append("description")
            willBeRight.append(description)
        if len(status)>0:
            willBeLeft.append("status")
            willBeRight.append(status)

        willBeLeft.append("participationPolicy")

        willBeRight.append({
            "userDefaultPolicy": "display",
            "policies": [{"policy": "do_not_display", "matchCriteria": "byGroup", "values": ["do_not_display"]},
                         {"policy": "do_not_save", "matchCriteria": "byGroup", "values": ["do_not_save"]}]})
            # "policies": [{"policy": "do_not_display", "groupsIds": ["do_not_display"]},
            #              {"policy": "do_not_save", "groupsIds": ["do_not_save"]}]})

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)


        try:
            r = requests.post(self.leaderboardURL + '/create',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to  leaderboard/create")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - leaderboard/create")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def LBUpdate(self, LbId, name="", description="", status="", groupsParticipationList="", operation="exclude",startDate="",endDate=""):
        willBeLeft = ["id"]
        willBeRight = [LbId]
        if len(name) > 0:
            willBeLeft.append("name")
            willBeRight.append(name)
        if len(description) > 0:
            willBeLeft.append("description")
            willBeRight.append(description)
        if len(status)>0:
            willBeLeft.append("status")
            willBeRight.append(status)
        if len(startDate)>0:
            willBeLeft.append("startDate")
            willBeRight.append(startDate)
        if len(endDate)>0:
            willBeLeft.append("endDate")
            willBeRight.append(endDate)
        if len(groupsParticipationList) > 0:
            willBeLeft.append("groupsParticipationList")
            groupList = {"operation": operation, "ids": [groupsParticipationList]}
            willBeRight.append(groupList)

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.leaderboardURL + '/update',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to  leaderboard/update")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - leaderboard/update")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def leaderboardClone(self, id):
            willBeLeft = ["id"]
            willBeRight = [id]
            will_json = dict(zip(willBeLeft, willBeRight))
            data_json = json.dumps(will_json)
            try:
                r = requests.post(self.leaderboardURL + '/clone',
                                 data=data_json,
                                 headers=self.headers)
            except Exception as Exp:
                print("fail to leaderboard/clone")
                print(Exp)
                return False
            if r.status_code != 200 and r.status_code != 201:
                print("fail to leaderboard/clone")
                print("Err: " + str(r.status_code) + " text: " + str(r.text))
                return False
            else:
                return r

    def leaderboardSub(self,id,names=["sub1","sub2"],filterPaths=["path1","path2"]):
        # will use cloned subs to test this - not needed at present
        names_ = names
        filterPaths_ = filterPaths
        will_be_dict = dict(zip(names_, filterPaths_))
        will_json = {
            "id": id,
            "subLeaderboards":
            [
                will_be_dict
            ]
        }
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.leaderboardURL + '/update',
                              data=data_json,
                              headers=self.headers)
        except Exception as Exp:
            print("fail to leaderboard/update subLeaderboards")
            print(Exp)
            return False
        if r.status_code != 200 and r.status_code != 201:
            print("fail to leaderboard/update subLeaderboards")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

# ============ /Rule/Actions ============
    def ruleCreate(self, ruleType, gameObjectId, name, description="", status="disabled", points="", maxPoints=""):

        willBeLeft = ["gameObjectType","gameObjectId","name"]
        willBeRight = ["leaderboard", gameObjectId, name]

        if len(description) > 0:
            willBeLeft.append("description")
            willBeRight.append(description)
        if len(status) > 0:
            willBeLeft.append("status")
            willBeRight.append(status)

        if ruleType == "confirmation":
            print("creating a rule: "+ruleType)
            willBeLeft.append("conditions")
            willBeRight.append([
                {
                    "fact": "eventType",
                    "operator": "equal",
                    "value": "confirmed"
                }
            ])
            willBeLeft.append("type")
            willBeRight.append("count") # === significant
            willBeLeft.append("metric")
            willBeRight.append("")
            willBeLeft.append("goal")
            willBeRight.append("1")
            willBeLeft.append("groupBy")
            willBeRight.append("kuserId")
            willBeLeft.append("points")
            willBeRight.append(points)
            willBeLeft.append("maxPoints")
            willBeRight.append(maxPoints)

        elif ruleType == "confirmBonus":
            print("creating a rule: " + ruleType)
            willBeLeft.append("conditions")
            willBeRight.append([
                {
                    "fact": "eventType",
                    "operator": "equal",
                    "value": "confirmed"
                }
            ])
            willBeLeft.append("type")
            willBeRight.append("countUnique") # === significant
            willBeLeft.append("metric")
            willBeRight.append("kuserId")
            willBeLeft.append("goal")
            willBeRight.append("1")
            willBeLeft.append("groupBy")
            willBeRight.append("")
            willBeLeft.append("points")
            willBeRight.append(points)
            willBeLeft.append("maxPoints") # maxPoints/points = num of users to get bonus
            willBeRight.append(maxPoints)

        elif ruleType == "external":
            print("creating a rule: " + ruleType)
            willBeLeft.append("conditions")
            willBeRight.append([
                {
                    "fact": "eventType",
                    "operator": "equal",
                    "value": "external"
                },
                {
                    "fact": "externalRuleId",
                    "operator": "equal",
                    "value": "first_external_rule"
                }
            ])
            willBeLeft.append("type")
            willBeRight.append("external")
            willBeLeft.append("metric")
            willBeRight.append("score")
            willBeLeft.append("groupBy")
            willBeRight.append("kuserId")

        elif ruleType == "vod":
            print("creating a rule: " + ruleType)
            willBeLeft.append("conditions")
            willBeRight.append([
                {
                    "fact": "eventType",
                    "operator": "equal",
                    "value": "viewPeriod"
                },
                {
                    "fact": "playbackType",
                    "operator": "equal",
                    "value": "vod"
                }
            ])
            willBeLeft.append("type")
            willBeRight.append("sum")
            willBeLeft.append("metric")
            willBeRight.append("playTime")
            willBeLeft.append("groupBy")
            willBeRight.append("kuserId,entryId")

            willBeLeft.append("goal")
            willBeRight.append("60")
            willBeLeft.append("points")
            willBeRight.append(points)
            willBeLeft.append("maxPoints")
            #willBeRight.append("duration,Math.floor(@MAX_POINTS@/60)*@POINTS@")
            willBeRight.append("duration,inMinutesMultiplyByPoints")

        elif ruleType == "quiz":
            print("creating a rule: " + ruleType)
            willBeLeft.append("conditions")
            willBeRight.append([
                {
                    "fact": "eventType",
                    "operator": "equal",
                    "value": "quizSubmitted"
                }
            ])
            willBeLeft.append("type")
            willBeRight.append("count")
            willBeLeft.append("metric")
            willBeRight.append("")
            willBeLeft.append("groupBy")
            willBeRight.append("kuserId,entryId")
            willBeLeft.append("goal")
            willBeRight.append("1")
            willBeLeft.append("points")
            willBeRight.append("score")
            willBeLeft.append("maxPoints")
            willBeRight.append("score")
        else:
            print("not a recognised rule: [confirm, confirmBonus, external, vod, quiz]")

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.ruleURL + '/create',
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to  rule/create")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - rule/create")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def ruleUpdate(self, id, name="", description="", status="", points="", maxPoints=""):
        # more attributes can be added as needed
        willBeLeft = ["id"]
        willBeRight = [id]
        if len(name) > 0:
            willBeLeft.append("name")
            willBeRight.append(name)
        if len(description) > 0:
            willBeLeft.append("description")
            willBeRight.append(description)
        if len(status)>0:
            willBeLeft.append("status")
            willBeRight.append(status)
        if len(points) > 0:
            willBeLeft.append("points")
            willBeRight.append(points)
        if len(maxPoints) > 0:
            willBeLeft.append("maxPoints")
            willBeRight.append(maxPoints)

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.ruleURL + '/update',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to  rule/update")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - rule/update")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def ruleList(self, gameObjectId="", gameObjectType="leaderboard", status="enabled", pageSize="", pageIndex="1"):
        willBeLeft = []
        willBeRight = []
        if len(gameObjectId) > 0:
            willBeLeft.append("gameObjectId")
            willBeRight.append(gameObjectId)
        if len(status) > 0:
            willBeLeft.append("status")
            willBeRight.append(status)
        if len(gameObjectType) > 0:
            willBeLeft.append("gameObjectType")
            willBeRight.append(gameObjectType)
        if len(pageSize) > 0:
            willBeLeft.append("pager")
            i_pager =  {"pageSize":  int(pageSize) ,"pageIndex": int(pageIndex)}
            willBeRight.append(i_pager)


        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.ruleURL + '/list',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to rule/list: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - rule/list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def ruleGet(self, id):
        data_json = json.dumps({"id": "" + id + ""})
        try:
            r = requests.post(self.ruleURL + '/get',
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - rule/get")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def ruleDelete(self, id):
        data_json = json.dumps({"id": "" + id + ""})
        try:
            r = requests.post(self.ruleURL + '/delete',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to rule/delete id: " + str(id))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - rule/delete")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

# ============ /userScore/Actions ============
    def userScoreList(self, gameObjectId="", gameObjectType="leaderboard", pageSize="", pageIndex="1", subGameid=0, option=""):
            willBeLeft = ["gameObjectId"]
            willBeRight = [gameObjectId]

            if len(gameObjectType) > 0:
                willBeLeft.append("gameObjectType")
                willBeRight.append(gameObjectType)
            if len(pageSize) > 0:
                willBeLeft.append("pager")
                i_pager =  {"pageSize":  int(pageSize) ,"pageIndex": int(pageIndex)}
                willBeRight.append(i_pager)
            if len(option) > 0:
                willBeLeft.append("subGameProperties")
                i_sub = {"id": int(subGameid), "option": option}
                willBeRight.append(i_sub)

            will_json = dict(zip(willBeLeft, willBeRight))
            data_json = json.dumps(will_json)
            try:
                r = requests.post(self.userScoreURL + '/list',
                                 data=data_json,
                                 headers=self.headers)

            except Exception as Exp:
                print("fail to userScore/list: ")
                print(Exp)
                return False

            if r.status_code != 200 and r.status_code != 201:
                print("Failed - userScore/list")
                print("Err: " + str(r.status_code) + " text: " + str(r.text))
                return False
            else:
                return r

    def userScoreGet(self, gameObjectId, userId, gameObjectType="leaderboard"):

            willBeLeft = ["gameObjectId", "userId"]
            willBeRight = [gameObjectId, userId]

            if len(gameObjectType) > 0:
                willBeLeft.append("gameObjectType")
                willBeRight.append(gameObjectType)

            will_json = dict(zip(willBeLeft, willBeRight))
            data_json = json.dumps(will_json)
            try:
                r = requests.post(self.userScoreURL + '/get',
                                 data=data_json,
                                 headers=self.headers)

            except Exception as Exp:
                print("fail to userScore/get: ")
                print(Exp)
                return False

            if r.status_code != 200 and r.status_code != 201:
                # print("Failed - userScore/get")
                # print("Err: " + str(r.status_code) + " text: " + str(r.text))
                return False
            else:
                return r

    def userScoreReport(self, gameObjectId="", email="",gameObjectType="leaderboard", usersOpting="out", additionalHeaders=""):
            if len(email) == 0:
                will_be_email = gameObjectId+"@mailinator.com"
            else:
                will_be_email = email

            if len(additionalHeaders) > 0:

                will_json = {
                        "gameObjectType": gameObjectType,
                        "gameObjectId": gameObjectId,
                        "usersOpting": usersOpting,
                        "email": will_be_email,
                        "additionalHeaders": additionalHeaders
                }
            else:
                willBeLeft = ["gameObjectId", "email", "gameObjectType", "usersOpting"]
                willBeRight = [gameObjectId, will_be_email, gameObjectType, usersOpting]
                will_json = dict(zip(willBeLeft, willBeRight))

            data_json = json.dumps(will_json)
            try:
                r = requests.post(self.userScoreURL + '/report',
                                 data=data_json,
                                 headers=self.headers)

            except Exception as Exp:
                print("fail to userScore/report: ")
                print(Exp)
                return False

            if r.status_code != 200 and r.status_code != 201:
                print("Failed - userScore/report")
                print("Err: " + str(r.status_code) + " text: " + str(r.text))
                return False
            else:
                return r

    def userScoregetSubGameOptions(self, gameObjectId="",gameObjectType="leaderboard", subGameId=0):
            willBeLeft = ["gameObjectId", "gameObjectType", "subGameId"]
            willBeRight = [gameObjectId, gameObjectType, subGameId]
            will_json = dict(zip(willBeLeft, willBeRight))
            data_json = json.dumps(will_json)
            try:
                r = requests.post(self.userScoreURL + '/getSubGameOptions',
                                 data=data_json,
                                 headers=self.headers)

            except Exception as Exp:
                print("fail to userScore/getSubGameOptions: ")
                print(Exp)
                return False

            if r.status_code != 200 and r.status_code != 201:
                print("Failed - userScore/getSubGameOptions")
                print("Err: " + str(r.status_code) + " text: " + str(r.text))
                return False
            else:
                return r

    def errHandler(self, will_json="",extra_url=""):
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.baseURL + extra_url,
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to userScore/getSubGameOptions: ")
            print(Exp)
            return False

        return str(r.text)

# ============ /certificateURL/Actions ============
    def certificateUpdate(self, id,status="enabled",host="",dictToJson=""):
        willBeLeft = ["id", "status"]
        willBeRight = [id, status]
        if len(host) > 0:
            willBeLeft.append(str("host"))
            willBeRight.append(str(host))
        # willBeLeft = ["id", "status", "certifiedCreditsThreshold"]
        # willBeRight = [id, status, 1]
        if len(dictToJson) > 0:
            if dictToJson == "dispaly":
                willBeLeft.append(str("participationPolicy"))
                willBeRight.append({
                    "userDefaultPolicy": "display",
                    "policies": [
                        {
                            "policy": "do_not_save",
                            "matchCriteria": "byGroup",
                            "values": [
                                "do_not_save"
                            ]
                        }
                    ]
                })
            elif dictToJson == "PDF":
                willBeLeft.append(str("outputFileConfiguration"))
                willBeRight.append({
                    "outputFileElements": [
                        {
                            "url": "https://cfvod.kaltura.com/p/2174101/sp/217410100/thumbnail/entry_id/1_2agxbpyp/version/100001/width/1397/height/1080"
                        },
                        {
                            "textElementType": "entryName",
                            "y": 570
                        },
                        {
                            "textElementType": "userFullName",
                            "y": 440
                        },
                        {
                            "textElementType": "credits",
                            "x": 1060,
                            "y": 699
                        },
                        {
                            "textElementType": "certificationDate",
                            "x": 695,
                            "y": 632
                        },
                        {
                            "textElementType": "metadataField",
                            "x": 150,
                            "y": 699,
                            "xPath": "/metadata/FieldOfStudy",
                            "metadataProfileId": 20261362
                        }
                    ]
                })
                #         }]})
                # willBeRight.append({
                #     "outputFileElements": [
                #         {"url": "https://cfvod.kaltura.com/p/2174101/sp/217410100/thumbnail/entry_id/1_2agxbpyp/def_height/480/def_width/640/version/100001/type/1"}, #OLD bad resolution
                #         #{"url": "https://cfvod.kaltura.com/p/2174101/sp/217410100/thumbnail/entry_id/1_2agxbpyp/version/100001/def_width/1397/def_height/1080"},# hi
                #         {
                #             "textElementType": "entryName",
                #             "x": 280,
                #             "y": 320
                #         },
                #         {
                #             "textElementType": "userFullName",
                #             "x": 280,
                #             "y": 270
                #         },
                #         {
                #             "textElementType": "credits",
                #             "x": 550,
                #             "y": 380
                #         },
                #         {
                #             "textElementType": "certificationDate",
                #             "x": 380,
                #             "y": 350
                #         },
                #         {
                #             "textElementType": "metadataField",
                #             "x": 150,
                #             "y": 380,
                #             "xPath": "/metadata/FieldOfStudy",
                #             "metadataProfileId": 20169722
                #         }]})


        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)
        try:
            r = requests.post(self.certificateURL + '/update',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to certificate/update id: " + str(id))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificate/update")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def certificateClone(self, id):
        data_json = json.dumps({"id": "" + id + ""})
        try:
            r = requests.post(self.certificateURL + '/clone',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to certificate/clone id: " + str(id))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificate/clone")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def certificateGet(self, id):
        data_json = json.dumps({"id": "" + id + ""})
        try:
            r = requests.post(self.certificateURL + '/get',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to certificate/get id: " + str(id))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificate/get")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def certificateDelete(self, id):
        data_json = json.dumps({"id": "" + id + ""})
        try:
            r = requests.post(self.certificateURL + '/delete',
                             data=data_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to certificate/delete id: " + str(id))
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificate/delete")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def certificateList(self, status="",externalId ="",pageSize ="",pageIndex="1"):
        willBeLeft = []
        willBeRight = []
        if len(status) > 0:
            willBeLeft.append("statusEqual")
            willBeRight.append(status)
        if len(externalId) > 0:
            willBeLeft.append("externalIdEqual")
            willBeRight.append(externalId)
        if len(pageSize) > 0:
            willBeLeft.append("pager")
            i_pager = {"pageSize": int(pageSize), "pageIndex": int(pageIndex)}
            willBeRight.append(i_pager)

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)

        try:
            r = requests.post(self.certificateURL + '/list',
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to certificate/list: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificate/list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

# ============ /userCertificateReport/Actions ============
    def certificateReportList(self, gameObjectId="",entryId="",userId="",status="",pageSize ="",pageIndex="1"):
        willBeLeft = []
        willBeRight = []
        if len(status) > 0:
            willBeLeft.append("status")
            willBeRight.append(status)
        if len(gameObjectId) > 0:
            willBeLeft.append("gameObjectId")
            willBeRight.append(gameObjectId)
        if len(entryId) > 0:
            willBeLeft.append("entryId")
            willBeRight.append(entryId)
        if len(userId) > 0:
            willBeLeft.append("userId")
            willBeRight.append(userId)
        if len(pageSize) > 0:
            willBeLeft.append("pager")
            i_pager = {"pageSize": int(pageSize), "pageIndex": int(pageIndex)}
            willBeRight.append(i_pager)

        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)

        try:
            r = requests.post(self.certificateReprtURL + '/list',
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to certificateReport/list: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificateReport/list")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

    def certificateReportServe(self, id, filePath=""):
        will_json = {"id":str(id)}
        data_json = json.dumps(will_json)

        try:
            r = requests.post(self.certificateReprtURL + '/serveCertificate',
                              data=data_json,
                              headers=self.headers)

            if len(filePath) == 0:
                cerPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UploadData'))
                self.cerPathFull = os.path.join(cerPath, 'testFile.pdf')
            else:
                self.cerPathFull = filePath

            with open(self.cerPathFull, 'wb') as f:
                f.write(r.content)

        except Exception as Exp:
            print("fail to certificateReport/serveCertificate: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificateReport/serveCertificate")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False

            # try:
            #     self.logi.appendMsg("TEARDOWN - Going to Delete pdf")
            #     os.remove(self.cerPathFull)
            #     time.sleep(1)
            #     if os.path.exists(self.cerPathFull):
            #         testStatus = False
            #         self.logi.appendMsg("TEARDOWN - FAILED to to Delete pdf")
            #     else:
            #         self.logi.appendMsg("TEARDOWN - PASS, pdf Deleted")
            # except Exception as Exp:
            #     print(Exp)
            #     testStatus = False
            #     self.logi.appendMsg("TEARDOWN - FAILED to to Delete pdf")

        else:
            return r
    def certificateReportReport(self, gameObjectId,entryId="",userId="",status="",email=""):

        if len(email) == 0:
            will_be_email = gameObjectId + "@mailinator.com"
            #will_be_email = gameObjectId + "@dispostable.com"

        else:
            will_be_email = email

        willBeLeft = ["gameObjectId", "email"]
        willBeRight = [gameObjectId, will_be_email]
        if len(status) > 0:
            willBeLeft.append("status")
            willBeRight.append(status)
        if len(entryId) > 0:
            willBeLeft.append("entryId")
            willBeRight.append(entryId)
        if len(userId) > 0:
            willBeLeft.append("userId")
            willBeRight.append(userId)


        will_json = dict(zip(willBeLeft, willBeRight))
        data_json = json.dumps(will_json)

        try:
            r = requests.post(self.certificateReprtURL + '/report',
                              data=data_json,
                              headers=self.headers)

        except Exception as Exp:
            print("fail to certificateReport/Report: ")
            print(Exp)
            return False

        if r.status_code != 200 and r.status_code != 201:
            print("Failed - certificateReport/Report")
            print("Err: " + str(r.status_code) + " text: " + str(r.text))
            return False
        else:
            return r

# ============ /userScore/Actions ============
    def eventSendExternalEventsFromCsv(self,delta=True,csv_path=""):
        try:
            csv = """"UserID,Schedule_training,Bonus_Schedule_Training_Score,first_external_rule,Bonus_Conduct_Training_Score,Additional_Score
                    inbal.bendavid@kaltura.com,,,112,,
                    danielba01@gmail.com,,,,,
                    inbal.bendavid@kaltura.com,40,,0,,
                    inbal.bendavid@kaltura.com,30,,,,
                    daniel.barak@kaltura.com,,,11,,
                    avichai.noach@kaltura.com,,,12,,
                    LB_usr9@mailinator.com,,,100,,
                    LB_usr9,,,22,,
                    usr0,10,20,30,40,
                    opt1,10,20,30,40,
                    opt2,10,20,30,40,
                    opt3,10,20,30,40,
                    opt4,10,20,30,40,
                    opt5,10,20,30,40,
                    opt6,10,20,30,40,
                    update1,10,20,30,40,
                    update2,10,20,30,40,
                    update3,10,20,30,40,"""
            csv_text = ''.join(format(ord(i), '08b') for i in csv)
            files = {
                            'scoreAction': 'upsert',
                            'csvFile': csv_text,
                        }
            file_json = json.dumps(files)
            r = requests.post(self.csvURL,
                             files=file_json,
                             headers=self.headers)

        except Exception as Exp:
            print("fail to csv: ")
            print(Exp)
            return False

#userScore/report
# ============ misc ============
    def disableAllLbs(self,dontDisable=""):
        try:
            response = self.LBList("enabled")
            if response.status_code == 200:
                response = str(response.text)
            else:
                print("Fail - failed to get LBList")
                return False
            print(response)
            i_dict = json.loads(response)
            total = i_dict["totalCount"]
            print(total)
            print(i_dict["objects"])
            objects = i_dict["objects"]
            for obj in objects:
                print(obj)
                print(obj["id"])
                if obj["id"] in dontDisable:
                    print("don't delete "+obj["id"])
                else:
                    r = self.LBDelete(obj["id"])
                    if r.status_code == 200: print("deleted "+ str(obj["id"]))

            print("-----")
        except Exception as Exp:
            print("Fail - failed to disableAllLbs")
            print(Exp)
            return False

def main():
    try:
        game_service = GameService(True)#63cd1c42beaf781f1cfe72c3  63c67b875abc6762557ef82b

        r = game_service.certificateUpdate('63da259780f5e5a3e235c76d',host="https://certification-vault-demo.events.kaltura.com")
        #r = game_service.certificateUpdate('63f5e3b94554491658c16784', dictToJson="PDF")#ep prod
        #r = game_service.certificateUpdate('63fb34e912aa3a46726f28ee', dictToJson="PDF")

        # r = game_service.certificateUpdate('63f38c1e4554491658c12786', status="disabled")
        #r = game_service.certificateUpdate('63f3add44feee2d440083648', status="enabled")
        #r = game_service.certificateReportServe('63f1defcf818be00943c4fff')#('63eb82945a58f972e57225fb')#('63eb7ff15a58f972e572257d')#('63ea34e10c4f0219454745a8')#('63e913b0d6dd7aaec6356cf6')#("63e913b7d6dd7aaec6356d36")

        #r = game_service.certificateUpdate('63f1f58b6bfd88e0fb576748', status="enabled")
        #r = game_service.certificateReportServe('63c7c0f65abc6762557f19af')#stg
        #r = game_service.certificateUpdate('63f38c1e4554491658c12786', dictToJson={"bal":"balbal"})
        # r= game_service.disableAllLbs()
        # r = game_service.certificateReportList("63da55dd80f5e5a3e235d2f0","1_jdt4q2a1")
        # rr = game_service.certificateReportReport("63da55dd80f5e5a3e235d2f0","1_jdt4q2a1")

        r = game_service.certificateUpdate('63eb64735a58f972e5722096', dictToJson={"bal":"balbal"})
        #r = game_service.certificateUpdate('63da55dd80f5e5a3e235d2f0',status="enabled")
        #r = game_service.certificateClone("63c5a4925abc6762557edf07")  http://daniels/my-certificates
        # r = game_service.certificateUpdate("63c67b875abc6762557ef82b",status="enabled",dictToJson={"name": "oldCert"}) 63ce8dcd9601cca51660e893
        # r = game_service.certificateUpdate("63ce8dcd9601cca51660e893", status="enabled", dictToJson={"host": "http://www.mailinator.com"})
        #### 63d0f7949601cca516614217

        r = game_service.certificateUpdate("63d240d680f5e5a3e234db9f", status="disabled",
                                           dictToJson={"externalId": "NaN"})
        # r = game_service.certificateUpdate("63d0f7949601cca516614217", status="enabled",
        #                                    dictToJson={"host": "https://4800142-2.events.dev.kaltura.com"})
        #r = game_service.certificateUpdate("63cf89ab9601cca51661108e", status="enabled", dictToJson={"creditsMapping": "credits,63cf89ab9601cca516611092,63cf89ab9601cca516611098\n10,60,1\n20,120,2\n30,180,3\n40,240,4\n50,300,5\n60,360,6\n60,420,8"})
#"63cf89ab9601cca516611092" "63cf89ab9601cca516611098"
        #time.sleep(0.5)  "creditsMapping": "credits,,\n10,60,1\n20,120,2\n30,180,3\n40,240,4\n50,300,5\n60,360,6\n60,420,8"
        #r = game_service.certificateList(status="disabled")
        #r = game_service.certificateGet("63c67b875abc6762557ef82b")
        # 63c5a4925abc6762557edf07 63c67b875abc6762557ef82b
        ### 63cd1c42beaf781f1cfe72c3
        #r = game_service.certificateList(status="enabled")
        r = game_service.certificateList(externalId="certificate2")
        print(r.text)
        print(r)
    except Exception as Exp:
            print(Exp)

if __name__ == "__main__":
    main()


# def parseLbList(response):
#     # this is an example on how to get to the data from game services /list responses
#     print(response)
#     i_dict = json.loads(str(response))
#     total = i_dict["totalCount"]
#     print(total)
#     print(i_dict["objects"])
#     objects = i_dict["objects"]
#     for obj in objects:
#         print(obj)
#         print(obj["id"])
#     print("-----")

