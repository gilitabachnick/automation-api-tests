######################################################
#
# Zeev.Shulman 04/2022
# Auxiliary funcs & data for Leaderboard
#
######################################################


import os
import string
import sys
import time
import random
import requests

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
# ========================================================================
from KalturaClient import KalturaConfiguration, KalturaClient
import ClienSession
import Entry

def upvoteComment(self, usr, entry="1_dfvn595t", upvoters_userId_list=[], three_times=False):
    UPVOTE_EVENT_TYPE = "30003"
    if three_times:
        msgIDs = ["1647157128938", "1647157128939", "1647157128937"]
    else:
        msgIDs = ["1647157128938"]

    try:
        print("upvoters: " + str(upvoters_userId_list))
        for msgID in msgIDs:
            # +20 point after 5*upvote
            for id in upvoters_userId_list:
                upvote_url = self.analyticsUrl + "&eventType=" + UPVOTE_EVENT_TYPE + "&partnerId=" + str(
                    self.Partner_ID) + "&messageId=" + msgID + "&messageUserId=" + usr + "&userId=" + id +\
                    "&contextId=" + entry + "&reactionType=7"
                r = requests.get(upvote_url)

        if r.status_code != 200 and r.status_code != 201:
            print(str(r))
            print("Failed externalRule()")
            return False
        else:
            return True
    except Exception as Exp:
        print(Exp)
        return False

def generate_rnd_entry():
    chars = string.ascii_lowercase + string.digits
    will_be_fake_entry = "1_"
    for i in range(8):
        will_be_fake_entry += random.choice(chars)
    return will_be_fake_entry

def create_new_entry(self,file,category="__lbQuiz",name="testQuiz"):
    try:
        mySess = ClienSession.clientSession(self.Partner_ID, self.serviceUrl, self.admin_secret)
        client = mySess.OpenSession('creator@kaltura.com')
        print('creating new entry')

        # creating new entry
        myentry = Entry.Entry(client, name, "leaderboard quiz test", "leaderboard 5+ test", "admintag",
                              category, 0, open(file, 'rb+'))
        # myentry = Entry.Entry(self.client, "MetaDataTest", "MetaDataTest desc", "metadatatest tag", "admintag","metadatatest category1", 0, self.FileName)
        entry = myentry.AddEntry(creatorId='creator@kaltura.com', ownerId='not@kaltura.com')
        # self.logi.appendMsg('the new entry id is:' + self.entry.id)
        # self.logi.appendMsg('upload file to the entry')
        Tokken = myentry.UploadFileToNewEntry(entry)
        finit = myentry.WaitForEntryReady(entry.id, 60)
        if not finit:
            return False
        else:
            return entry.id
    except Exception as Exp:
        print(Exp)
        return False

def delete_entry(self,entry):

    try:
        print("INFO - Going to delete entryId = " + entry)
        mySess = ClienSession.clientSession(self.Partner_ID, self.serviceUrl, self.admin_secret)
        client = mySess.OpenSession()
        time.sleep(5)
        result = client.baseEntry.delete(entry)
        return result

    except Exception as Exp:
        print(Exp)
        return False
    
def user_country_update(self,user_id,new_value):
    try:
        from KalturaClient.Plugins.Core import KalturaUser
        print("INFO - Going to update user")
        mySess = ClienSession.clientSession(self.Partner_ID, self.serviceUrl, self.admin_secret)
        client = mySess.OpenSession()
        time.sleep(5)
        userId = user_id
        user = KalturaUser()
        user.country = new_value
        result = client.user.update(userId, user)
        return result

    except Exception as Exp:
        print(Exp)
        return False

def user_country_update(self,user_id,new_value):
    try:
        from KalturaClient.Plugins.Core import KalturaUser
        print("INFO - Going to update user")
        mySess = ClienSession.clientSession(self.Partner_ID, self.serviceUrl, self.admin_secret)
        client = mySess.OpenSession()
        time.sleep(5)
        userId = user_id
        user = KalturaUser()
        user.country = new_value
        result = client.user.update(userId, user)
        return result

    except Exception as Exp:
        print(Exp)
        return False

def rnd_unexluded_user(self, users_list, start=0):
    excluded_users = []
    exc_user_list = self.Leader_board.retGroupUserList("LBexclude")
    for i in range(start, len(exc_user_list.objects)):
        excluded_users.append(exc_user_list.objects[i].userId)
    n = random.randint(0, len(users_list) - 1)
    if users_list[n].userId in excluded_users:
        # if excluded, look for a different user - wow, recursion
        return rnd_unexluded_user(self, users_list, start)
    else:
        return n

# ====================================================
# returns true if usr is excluded, False if not
def is_excluded(self,usr):
    try:
        exc_user_list = self.Leader_board.retGroupUserList("LBexclude")
        for i in range(0, len(exc_user_list.objects)):
            if exc_user_list.objects[i].userId == usr:
                return True
        return False

    except Exception as Exp:
        print(Exp)
        return True

# returns randomized Live entry from a list
def ret_rnd_live_entry():
    live_list = ["1_z5v6jp4n", "1_78sna0pe", "1_frs90vb9", "1_hmd1dsrz", "1_doefihp5"]
    n = random.randint(0, len(live_list) - 1)
    return live_list[n]

def quizPoints(self, usr, entry, points=33):
    QUIZ_EVENT_TYPE = "30001"
    try:
        # &score is used &calculatedScore is ignored by LB/Analytics
        quiz_url = self.analyticsUrl + "&eventType=" + QUIZ_EVENT_TYPE + "&partnerId=" + str(self.Partner_ID) +\
                   "&userId="+usr+"&entryId=" + entry + "&version=0" + "&score=" + str(points) +\
                   "&calculatedScore=" + "77" + "&reactionType=7"
        r = requests.get(quiz_url)
        if r.status_code != 200 and r.status_code != 201:
            print(str(r))
            print("Failed externalRule()")
            return False
        else:
            return True
    except Exception as Exp:
        print(Exp)
        return False
def pollSubmit(self, usr, entry, points=33):
    #should pollId be unique - test if have truble
    POLL_EVENT_TYPE = "30004"
    try:
        # &score is used &calculatedScore is ignored by LB/Analytics
        poll_url = self.analyticsUrl + "&eventType=" + POLL_EVENT_TYPE + "&partnerId=" + str(self.Partner_ID) +\
                   "&userId="+usr+"&entryId=" + entry + "&version=0" + "&score=" + str(points) +\
                   "&calculatedScore=" + "77" + "&pollId=123" + "&reactionType=7"
        r = requests.get(poll_url)
        if r.status_code != 200 and r.status_code != 201:
            print(str(r))
            print("Failed externalRule()")
            return False
        else:
            return True
    except Exception as Exp:
        print(Exp)
        return False

def register_to_LB(self, usr, register_twice=False):
    #REGISTER_EVENT_TYPE = "20001"
    REGISTER_EVENT_TYPE = "20002"
    # register_str_from_Inbal = "http://analytics.kaltura.com/api_v3/index.php?service=analytics&action=trackEvent&eventType=20001&partnerId=4507363&ks=djJ8NDUwNzM2M3y5H4OV5al0WrctvJjFAhbjQsqISVHnBUJQ3hy4uhE7UmIvWvf2g69iIRuVsgU1ElqwrxG-4a7CMStofLyu7Vdzl9b8_cFGAHUopJz2mV870N_DfS0ulcFVHOrH0cmAl5St64Gf9gOMP6jOHK9dfU3qw5jml41SOxNCzVFO7K8tiA=="
    try:
        userID_str = usr  # "LB_usr" + str(n)  # "zeev_sh" #"daniel_barak" #  "LB_usr80" #
        KMS_KS = genKMS_KS(self, usr)
        print("register: " + str(userID_str))
        time.sleep(1)
        register_user_url = self.analyticsUrl + "&eventType=" + REGISTER_EVENT_TYPE + "&partnerId=" + str(
            self.Partner_ID) + "&ks=" + KMS_KS

        r = requests.get(register_user_url)
        #self.Wd.get(register_user_url)
        #time.sleep(0.5)
        # register_response = self.Wd.find_element_by_xpath("//*[*]/pre").text

        # multi times register -  getting points for registration multiple times was a thing - check it doesn't happen
        if register_twice:
            self.Wd.get(register_user_url)
            time.sleep(1)
    except Exception as Exp:
        print(Exp)
        self.logi.appendMsg("FAIL - FAILED to register_to_LB")
        return False

def playEntry(self, usr, entry="1_qo2empqb", seconds=60):
    PLAY_EVENT_TYPE = "99"
    sessionId = "a5153359-7c64-4ad5-015c-3727ca5ae7cf"
    KMS_KS = genKMS_KS(self, usr)

    try:
        for i in range(0, int(seconds/10)):
            play_url = self.analyticsUrl + "&eventType=" + PLAY_EVENT_TYPE + "&partnerId=" + str(self.Partner_ID) +\
                "&ks=" + KMS_KS + "&sessionId="+sessionId +\
                "&entryId=" + entry + "&reactionType=7"
            r = requests.get(play_url)
            time.sleep(10)
        # https://analytics.kaltura.com/api_v3/index.php?service=analytics&action=trackEvent&eventType=99&partnerId=4507363&ks=djJ8NDUwNzM2M3wK5tzTKxDyR-cMJASsIKHnEmwEW0sdSKk3jHiGjF9ijc_bTSzTOz3uDeR2OOhjhauXrtueWw4YBbtIvn2eKmrKB2fMfHVoVug31fMUhnRSg3xaoW2evPa_QQ9mcNvkJqa1GmzFV8WgEGEFzjckMx0EfgiX4naMr_T2y5_u2n6ywA==&sessionId=a5153359-7c64-4ad5-015c-3727ca5ae7cf&entryId=1_av8kzatt&reactionType=7
        print(usr + " Viewed " +entry + " " + str(seconds) + " seconds")
        # sleep(20) because sleep(10) was not enough for analytics to always pass on the event
        time.sleep(20)
        if r.status_code != 200 and r.status_code != 201:
            print(str(r))
            print("Failed externalRule()")
            return False
        else:
            return True
    except Exception as Exp:
        print(Exp)
        return False

# ===============================================================================
# Create Session (KS) emulating KMS user using API
# ===============================================================================
def genKMS_KS(self, usr="LB_usr80"):
    from KalturaClient.Plugins.Game import KalturaSessionType
    try:
        config = KalturaConfiguration()
        config.serviceUrl = self.serviceUrl
        client = KalturaClient(config)
        secret = self.user_secret
        userID_str = usr  # LB_usr" + str(n)  # "zeev_sh" #"daniel_barak" #  "LB_usr80" #
        KSType = KalturaSessionType.USER
        partnerId = self.Partner_ID
        expiry = None
        privileges = self.privileges

        KMS_KS = client.session.start(secret, userID_str, KSType, partnerId, expiry, privileges)
        # print(userID_str)
        # print(KMS_KS)
        return KMS_KS
    except Exception as Exp:
        print(Exp)
        print("Failed KS")
        return False

def externalRule(self, usr, score="10", rule="Additional_Score", scoreAction="delta"):
    # scoreAction proper values = 'delta', 'upsert'
    EXTERN_EVENT_TYPE = "30002"
    print("externalRule:" + usr + " " + score + " " + rule + " " + scoreAction)
    try:
        external_url = self.analyticsUrl + "&eventType=" + EXTERN_EVENT_TYPE + "&partnerId=" + str(self.Partner_ID) + \
                "&userId=" + usr + "&externalRuleId=" + rule + "&scoreAction=" + scoreAction + "&score=" + score +\
                "&reactionType=7"
        r = requests.get(external_url)
        if r.status_code != 200 and r.status_code != 201:
            print(str(r))
            print("Failed externalRule()")
            return False
        else:
            return True
    except Exception as Exp:
        print(Exp)
        print("Failed externalRule()")
        return False
