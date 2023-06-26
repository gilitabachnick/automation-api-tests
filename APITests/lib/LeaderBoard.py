###################################################
#                                                 #
# this class is for leader board use              #
# for now allowed only on testing                 #
# environment.                                    #
# uses only for admin side settings prerun        #
#                                                 #
###################################################
import os
from KalturaClient.Plugins.Game import *

import ClienSession
import Config


class LeaderBoard():

    def __init__(self,env='testing',userId=None, impersonateID=None):

        pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'ini'))
        self.env = env
        if env == 'testing':
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        else:
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))

        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURLleaderboard')
        self.UserSecret = inifile.RetIniVal('Environment', 'LeaderBoardAdminSecret')
        self.PublisherID = inifile.RetIniVal('Environment', 'LeaderBoardPID')
        mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.UserSecret)
        try:
            self.client = mySess.OpenSession()
            self.KS = self.client.requestConfiguration['ks']
            print(self.KS)
        except Exception as Exp:
            print(Exp)

    def getLeaderBoardList(self, gameObjectId, userIdEqual, pageSize=100):

        filter = KalturaUserScorePropertiesFilter()
        filter.gameObjectId = gameObjectId
        filter.gameObjectType = KalturaGameObjectType.LEADERBOARD
        if userIdEqual != None:
            filter.userIdEqual = userIdEqual
            pager = None
        else:
            pager = KalturaFilterPager()
            pager.pageSize = pageSize #changed for API, might bug old Google set [was pageSize=None]
        try:
            result = self.client.game.userScore.list(filter, pager)
            return result
        except Exception as Exp:
            print(str(Exp))
            return False

    def DeleteGameUserScore(self, gameObjectId=1, userId=None):

        gameObjectId = gameObjectId
        gameObjectType = KalturaGameObjectType.LEADERBOARD
        try:
            result = self.client.userscore.delete(gameObjectId, gameObjectType, userId)
            return result
        except Exception as Exp:
            print(str(Exp))
            return False

    def UpdateUserScore(self, gameObjectId = 0, userId=None, score=100):
        gameObjectId = gameObjectId
        gameObjectType = KalturaGameObjectType.LEADERBOARD
        try:
            result = self.client.userscore.update(gameObjectId, gameObjectType, userId, score)
            return result
        except Exception as Exp:
            print(str(Exp))
            return False

    def addUserToGroup(self,userId, groupId):

        group_user = KalturaGroupUser()
        group_user.creationMode = KalturaGroupUserCreationMode.MANUAL
        group_user.groupId = groupId
        group_user.userRole = KalturaGroupUserRole.MEMBER
        group_user.userId = userId
        try:
            result = self.client.groupUser.add(group_user)
            return result
        except Exception as Exp:
            print(str(Exp))


    def removeUserFromeGroup(self, userId, groupId):

        try:
            result = self.client.groupUser.delete(userId, groupId)
            return result
        except Exception as Exp:
            print(str(Exp))


    def retGroupUserList(self, groupId):

        filter = KalturaGroupUserFilter()
        filter.groupIdEqual = groupId
        pager = KalturaFilterPager()
        try:
            result = self.client.groupUser.list(filter, pager)
            return result
        except Exception as Exp:
            print(str(Exp))




# def main():
#
#     print("dd")
#     try:
#         x = LeaderBoard("prod", "LB_usr80@@mailinator.com")
#         r = x.retGroupUserList("LBexclude")
#         print(r)
#     except Exception as Exp:
#         print(Exp)
#
# if __name__ == "__main__":
#     main()
