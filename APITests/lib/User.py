from KalturaClient.Plugins.Core import *


#===============================================================================
# class name: User
# Desc: this class treat user methods
#===============================================================================

class User:
    
    def __init__(self,client):
        self.client = client
    

    def addUser(self, uId, uscreenName, umail, ufirstname, ulastName, uroleId=None, isNegative=False):
        user = KalturaUser()
        user.id = uId
        user.type = KalturaUserType.USER
        user.screenName = uscreenName
        user.email = umail
        user.firstName = ufirstname
        user.lastName = ulastName
        user.isAdmin = True
        user.roleIds = uroleId
        try:
            result = self.client.user.add(user)
        except Exception as exp:
            if isNegative == True:
                result = exp
            else:
                result = False
            
        return result
    
    def deleteUser(self, uId):
        try:
            result = self.client.user.delete(uId)
        except:
            result = False
            
        return result