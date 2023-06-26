import os

from KalturaClient.Plugins.Core import *


class uiconf():
    
    def __init__(self,client, confName=None):
        self.client = client
        self.confName = confName
        
    def getLastPlayerVer(self,env='testing'):
        # pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        # if env =='testing':
        #     inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        #     startSess = ClienSession.clientSession(inifile.RetIniVal('Environment', 'PublisherID'),inifile.RetIniVal('Environment', 'ServerURL'),inifile.RetIniVal('Environment', 'UseruserSecret'))
        # else:
        #     inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
        #     startSess = ClienSession.clientSession(inifile.RetIniVal('Environment', 'PublisherID'),inifile.RetIniVal('Environment', 'ServerURL'),inifile.RetIniVal('Environment', 'UseruserSecret'))
        #
        #
        # userKS = startSess.GetKs(type=0,privileges='scenario_default:*')[2]
        # dataU = 'kmcks='+str(userKS)
        # url = inifile.RetIniVal('Environment', 'ServerURL')+'/index.php/kmc/kmc4'
        # f = urllib2.urlopen(urllib2.Request(url, headers={'Cookie':dataU}))
        # resp = f.read()
        # print resp
        # #print resp
        # ind = resp.find('html5_version":')
        # htmlver = resp[ind:ind+40].split('"')[2]
        # #=======================================================================
        # # htmlver = resp[ind:ind+40].replace('\\"','').split(':')[1].split(',')[0]
        # #=======================================================================
        htmlver = '{latest}'
        print(('THE HTML VERSION IS: ' + htmlver))
        return htmlver
        
    
    def addPlayer(self,plugin=None,env='testing', isNegative=False, isDrm=True, Pvervion=None):
        # this case is only for testing permissions deny- version is not important
        if isNegative:
            playerCurrVer = '2.4'
        else:
            playerCurrVer = self.getLastPlayerVer(env)
            
        uiConf = KalturaUiConf()

        if self.confName == None:
            uiConf.name = "autoDRM"
        else:
            uiConf.name = self.confName



        if Pvervion == 'v3':
            uiConf.description = "automation V3 player"
            uiConf.objType = KalturaUiConfObjType.PLAYER_V3
            uiConf.width = 560
            uiConf.height = 395
            uiConf.swfUrl = '/flash/kdp3/v3.9.9/kdp3.swf'
            uiConf.tags = 'kalturaPlayerJs,player,ovp'
            uiConf.confVars = "{\"versions\":{\"kaltura-ovp-player\":\"{latest}\"},\"langs\":[\"en\"]}"
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            uiConf.config = open(os.path.join(pth, 'playerConfV3.txt')).read()
        else:
            uiConf.description = "auto play ready"
            uiConf.objType = KalturaUiConfObjType.PLAYER
            uiConf.width = 560
            uiConf.height = 395
            if plugin!=None:
                uiConf.pluginsData = plugin

            #FmwEmbedLoader.php
            uiConf.tags = 'html5studio,player'
            uiConf.swfUrl = '/flash/kdp3/v3.9.9/kdp3.swf'
            uiConf.html5Url = '/html5/html5lib/' + playerCurrVer + '/mwEmbedLoader.php'
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'XML'))
            uiConf.confFile = open(os.path.join(pth,'PlayerConfFile.xml')).read()
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isDrm == True:
                uiConf.config = open(os.path.join(pth,'playerConf.txt')).read()
            else:
                uiConf.config = open(os.path.join(pth,'playerConfLive.txt')).read()
        
        uiConf.creationMode = KalturaUiConfCreationMode.WIZARD
        try:
            result = self.client.uiConf.add(uiConf)
            
        except Exception as exp:
            print(exp)
            if isNegative == True:
                result = exp
            else:
                result = False
        
        return result
        
    def deletePlayer(self,playerId):
        try:
            self.client.uiConf.delete(playerId)
        except:
            print('delete player failed')