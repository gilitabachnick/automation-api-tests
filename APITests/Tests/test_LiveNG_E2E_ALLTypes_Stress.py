'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_LiveNG_E2E_ALLTypes_Stress.py
 
 @desc : This test check is stress tests on all types: transcoding  + transcoding HD + Passthrough + multi audio
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
#sys.path.insert(1,pth)


import ClienSession
import reporter2
import Config
import Practitest
import Entry
import uiconf
import tearDownclass
import MySelenium

import live
import LiveDashboard
import Transcoding
import QrcodeReader
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# Practi_TestSet_ID,isProd = 11,"false"
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False
# 
# isProd = False # LiveNG is just supported on testing
#==========================PublisherID=====================================================
testStatus = True

Practi_TestSet_ID = os.getenv('Practi_TestSet_ID')
isProd =  os.getenv('isProd')
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False



class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        os.system("taskkill /IM chromedriver.exe /F")
        os.system("taskkill /IM chrome.exe /F")
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        if isProd:
            section = "Production"
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            self.env = 'prod'
            # Streaming details
            self.url= "www.kaltura.com"
            self.playerId = "46022611"# v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print('PRODUCTION ENVIRONMENT')
            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
             # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            print('TESTING ENVIRONMENT') 
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.remote_host = "3.220.44.72"#"liveng-core3-automation.kaltura.com" #"34.201.96.171"#"3.220.44.72"#"liveng-core3-automation.kaltura.com"
        self.remote_user = "root"
        self.remote_pass = "Vc9Qvx%J5PJNxG%$Wo@ad9xZAHJEg?P9"#"Vc9Qvx%J5PJNxG%$Wo@ad9xZAHJEg?P9"#"testingqa"
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"      
        #**** SSH streaming computer - Ilia computer
        #self.remote_host = "192.168.162.176"
        #self.remote_user = "root"
        #self.remote_pass = "Kaltura12#"
        #self.filePath = "/home/kaltura/tests/stream_liveNG_custom_entry_AUTOMATION.sh"
        #***** SSH streaming computer - dev-backend4
        #self.remote_host = "dev-backend4.dev.kaltura.com"
        #self.remote_user = "root"
        #self.remote_pass = "1q2w3e4R"  
        #self.filePath = "/root/LiveNG/ffmpeg_data/entries/LongCloDvRec.mp4"
        self.NumOfEntries = 20
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        #self.PlayerVersion = 2 # Player version 2 or 3
        #self.AllPlayers = True # If True running the two version in a loop/ If False running just self.PlayerVersion
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_497_LiveNG_E2E_ALLTypes_Stress')
        self.logi.initMsg('test_497_LiveNG_E2E_ALLTypes_Stress')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)

    def test_497_LiveNG_E2E_ALLTypes_Stress(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for partner: ' + self.PublisherID)
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
            # Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V2')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            self.player = myplayer.addPlayer(None, self.env, False, False)  # Create latest player v2
            if isinstance(self.player, bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest player V2 ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)

            self.logi.appendMsg('INFO - Going to create latest V3')
            myplayer3 = uiconf.uiconf(self.client, 'livePlayer')
            self.player_v3 = myplayer3.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
            if isinstance(self.player_v3, bool):
                testStatus = False
                return
            else:
                self.playerId_v3 = self.player_v3.id
            # Create live object with current player_v3
            self.logi.appendMsg('INFO - Created latest player V3 ' + str(self.player_v3))
            self.testTeardownclass.addTearCommand(myplayer3, 'deletePlayer(' + str(self.player_v3.id) + ')')
            # Create live object with current player
            self.liveObj_v3 = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID,self.playerId_v3)

            '''############### Audio only ###########################################################################
            self.filePath = "/home/kaltura/entries/LongCloDvRec.aac"  # Required audio only file
            ## RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            '''Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('Cloud transcode')
            if self.CloudtranscodeId == None:
                self.CloudtranscodeId = Transobj.addTranscodingProfile(1, '32,33,34,35')
                if isinstance(self.CloudtranscodeId, bool):
                    testStatus = False
                    return
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client,'AUTOMATION-AudioONLY_' + str(i) + '_' + str(datetime.datetime.now()),"Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(self.streamUrl[i].primaryBroadcastingUrl))
                ffmpegCmdLine = self.liveObj.ffmpegCmdString_AudioOnly(self.filePath,str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
                # ffmpegCmdLine=ffmpegCmdLine.replace("rtmp-0.qa1.qa.live.ovp.kaltura.com", "rtmp-0.nvq1-live-cluster.nvq1.live.ovp.kaltura.com")
                rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return
            print("end audio only")'''
           ############### Transcoding HD ###########################################################################'''
            # self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
            # ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            # Transobj = Transcoding.Transcoding(self.client,'TranscodingHD')
            # self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('TranscodingHD')
            # if self.CloudtranscodeId==None:
            #     self.CloudtranscodeId = Transobj.addTranscodingProfile(1,'32,33,34,35,42,43')
            #     if isinstance(self.CloudtranscodeId,bool):
            #         testStatus = False
            #         return
            #
            #
            # self.entrieslst = []
            # self.streamUrl = []
            # # Create self.NumOfEntries live entries
            # for i in range(0, self.NumOfEntries):
            #     Entryobj = Entry.Entry(self.client, 'AUTOMATION-Transcoding_HD_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
            #     self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
            #     self.entrieslst.append(self.entry)
            #     self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
            #     streamUrl = self.client.liveStream.get(self.entry.id)
            #     self.streamUrl.append(streamUrl)
            #
            # # Get entryId and primaryBroadcastingUrl from live entries
            # for i in range(0, self.NumOfEntries):
            #     self.entryId = str(self.entrieslst[i].id)
            #     self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(self.streamUrl[i].primaryBroadcastingUrl))
            #     ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)
            #     #ffmpegCmdLine=ffmpegCmdLine.replace("rtmp-0.qa1.qa.live.ovp.kaltura.com", "rtmp-0.nvq1-live-cluster.nvq1.live.ovp.kaltura.com")
            #     rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
            #     if rc == False:
            #         self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
            #         testStatus = False
            #         return
            #
            # print("end trans HD")
            # ############### Transcoding ###########################################################################
            # self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
            # ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            # Transobj = Transcoding.Transcoding(self.client,'Cloud transcode')
            # self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('Cloud transcode')
            # if self.CloudtranscodeId==None:
            #     self.CloudtranscodeId = Transobj.addTranscodingProfile(1,'32,33,34,35')
            #     if isinstance(self.CloudtranscodeId,bool):
            #         testStatus = False
            #         return
            #
            # self.entrieslst = []
            # self.streamUrl = []
            # # Create self.NumOfEntries live entries
            # for i in range(0, self.NumOfEntries):
            #     Entryobj = Entry.Entry(self.client,'AUTOMATION_Transcoding_' + str(i) + '_' + str(datetime.datetime.now()),"Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.CloudtranscodeId)
            #     self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
            #     self.entrieslst.append(self.entry)
            #     self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entry.id) + '\')')
            #     streamUrl = self.client.liveStream.get(self.entry.id)
            #     self.streamUrl.append(streamUrl)
            #
            # # Get entryId and primaryBroadcastingUrl from live entries
            # for i in range(0, self.NumOfEntries):
            #     self.entryId = str(self.entrieslst[i].id)
            #     self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(self.streamUrl[i].primaryBroadcastingUrl))
            #     ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
            #     # ffmpegCmdLine=ffmpegCmdLine.replace("rtmp-0.qa1.qa.live.ovp.kaltura.com", "rtmp-0.nvq1-live-cluster.nvq1.live.ovp.kaltura.com")
            #     rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
            #     if rc == False:
            #         self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
            #         testStatus = False
            #         return
           ############### Passthrough ###########################################################################
            self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            Transobj = Transcoding.Transcoding(self.client, 'Passthrough')
            self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
            if self.passtrhroughId == None:
                self.passtrhroughId = Transobj.addTranscodingProfile(1, '32,36,37')
                if isinstance(self.passtrhroughId, bool):
                    testStatus = False
                    return

            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client,'AUTOMATION-STRESS_Passthrough_' + str(i) + '_' + str(datetime.datetime.now()),"Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(self.streamUrl[i].primaryBroadcastingUrl))
                #ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
                # ffmpegCmdLine=ffmpegCmdLine.replace("rtmp-0.qa1.qa.live.ovp.kaltura.com", "rtmp-0.nvq1-live-cluster.nvq1.live.ovp.kaltura.com")
                #rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
                ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath,str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
                rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return

           # ############### MULTI AUDIO ###########################################################################
           #  self.filePath = "/home/kaltura/entries/disney_ma.mp4"
           #  ''' RETRIEVE TRANSCODING ID AND CREATE MULTI AUDIO Eng+SPA partner 0 profile IF NOT EXIST'''
           #  Transobj = Transcoding.Transcoding(self.client, 'Eng+SPA partner 0 profile')
           #  self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('Eng+SPA partner 0 profile')
           #  if self.CloudtranscodeId == None:
           #      self.CloudtranscodeId = Transobj.addTranscodingProfile(1, '32,583728,583734')
           #      if isinstance(self.CloudtranscodeId, bool):
           #          testStatus = False
           #          return
           #
           #  self.entrieslst = []
           #  self.streamUrl = []
           #  # Create self.NumOfEntries live entries
           #  for i in range(0, self.NumOfEntries):
           #      Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_MultiAudio_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.CloudtranscodeId)
           #      self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
           #      self.entrieslst.append(self.entry)
           #      self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entry.id) + '\')')
           #      streamUrl = self.client.liveStream.get(self.entry.id)
           #      self.streamUrl.append(streamUrl)
           #
           #  # Get entryId and primaryBroadcastingUrl from live entries
           #  for i in range(0, self.NumOfEntries):
           #      self.entryId = str(self.entrieslst[i].id)
           #      self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url + " , primaryBroadcastingUrl = " + str(self.streamUrl[i].primaryBroadcastingUrl))
           #      # ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)
           #      ffmpegCmdLine = self.liveObj.ffmpegCmdString_MultiAudio(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)
           #      rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host,self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl,FoundByProcessId=True)
           #      if rc == False:
           #          self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
           #          testStatus = False
           #          return

            # time.sleep(2)
            # for CurrentplayerVersion in range(2,4):
            #     #Playback verification of all entries with all player version = 2 and 3
            #     self.logi.appendMsg("INFO - ************** Going to play live entries on PlayerVersion= "+ str(CurrentplayerVersion) +"  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            #     limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            #     seenAll = False
            #     while datetime.datetime.now() <= limitTimeout and seenAll==False:
            #             if CurrentplayerVersion == 3:
            #                 rc = self.liveObj_v3.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion)
            #             else:
            #                 rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion)
            #             time.sleep(5)
            #             if not rc:
            #                 testStatus = False
            #                 return
            #             if self.seenAll_justOnce_flag ==True:
            #                 seenAll = True
            #
            #     self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(CurrentplayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            print("End")
            '''# kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID)
            if rc != False:
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId) + " , url= " + self.url)
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId) + " , url= " + self.url)
                testStatus = False
                return'''

            
            '''try:
                self.logi.appendMsg("INFO - Going to close browser")
                self.Wd.quit()
            except Exception as Exp:
                print (Exp)
                pass'''
                           
        except Exception as e:
            print(e)
            testStatus = False
            pass
             
        
    #===========================================================================
    # TEARDOWN   
    #===========================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down')
        # try:
        #     self.Wd.quit()
        # except Exception as Exp:
        #     print(Exp)
        #     pass
        
        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
            print('#############')
        except Exception as Exp:
           print(Exp)
           pass
        
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID, '497','1')
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '497','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_LiveNG_E2E_ALLTypes_Stress.py -s')
    #===========================================================================
        
        
        