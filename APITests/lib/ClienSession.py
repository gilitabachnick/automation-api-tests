from KalturaClient import *
from KalturaClient.Plugins.Metadata import *
#from pip._vendor.requests.packages.urllib3.util.connection import select

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


class clientSession:
    def __init__(self,partnerId, dcUrl , secret, userId=None, impersonateID=None):
        self.partnerId = partnerId
        self.dcUrl = dcUrl
        self.secret = secret
        self.userId= userId
        self.impersonateID = impersonateID
    
    # send type=0 if user ks needed
    # send privileges='scenario_default:* privileges' for user KS
    def GetKs(self,type=2,privileges=None, userId=None):
        config = KalturaConfiguration(self.partnerId)
        if userId==None:
            userId = self.userId
        config.serviceUrl = self.dcUrl
        #=======================================================================
        # config.logger = self.logger
        #=======================================================================
        client = KalturaClient(config)
        result = client.session.start(self.secret, userId, type, self.partnerId, None, privileges)
        if self.impersonateID!=None:
            client.setPartnerId(self.impersonateID)
        
        dict = {1:client,2:result}
        return dict
    #Open a session
    def OpenSession(self,userID=None,type=None, privileges=None):
        if type!=None:
            dict = self.GetKs(type,privileges,userID)
        else:
            dict = self.GetKs(2, privileges, userID)
            #dict = self.GetKs( userId=userID)
            
        
        
        try:
            dict[1].setKs(dict[2])
        except Exception as exp:
            print(exp)
            
        return dict[1]
    
    def startSession(self,privileges='scenario_default:* privileges',userType=0):
        userTypeDict = {0:KalturaSessionType.USER,
                        1: KalturaSessionType.ADMIN}
        
        config = KalturaConfiguration(self.partnerId)
        config.serviceUrl = self.dcUrl
        client = KalturaClient(config)
        type = userTypeDict[userType]
        userId = None
        expiry = None
        return client.session.start(self.secret, userId, type, self.partnerId, expiry, privileges)
    
    def prettyPrint(self):
        print(("clientSession",self.partnerId,self.dcUrl,self.secret))
    
