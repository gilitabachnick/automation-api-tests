
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_303_LiveNGPass_PreviewMode.py
 Test #303 | Test #303 | Preview Mode - Passthrough (NO DVR)- Jump Live<->Preview
 
 @desc : This test check E2E test of new LiveNG entries Passthrough by Creating new live entry with explicitLive=1 enable  and start streaming and then
 Playback with/out USER KS and ADMIN KS
 and then updating GO LIVE preview mode -> Verify live entry playback by refreshing/opening new browser
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time
import pytest

#from StaticMethods import before_run


pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
#pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
#sys.path.insert(1,pth)

from KalturaClient.Plugins.Core import *
import QrcodeReader
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
import ast
import StaticMethods
##########
### Jenkins params ###
#===============================================================================
# cnfgCls = Config.ConfigFile("stam")
# #self.Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
# self.Practi_TestSet_ID,isProd = 11,"false"
# if str(isProd) == 'true':
#     isProd = True
# else:
#     isProd = False
# 
# isProd = False # LiveNG is just supported on testing
#==========================PublisherID=====================================================
testStatus = True
class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        StaticMethods.before_run(self)

        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')
        # Environment BE server URL
        if self.ServerURL is None:
            self.ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        print("ServerURL = " + self.ServerURL)
        # LiveNG config partner:
        if self.PartnerID != None:
            self.PublisherID = self.PartnerID
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'LIVENG_UserSecret')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'LIVENG_PublisherID')  # QA 6611/ PROD 2930571
            self.UserSecret = self.inifile.RetIniVal(self.section, 'LIVENG_UserSecret')

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"

        #***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True
        self.RestartDowntime = 60
        self.PlayerVersion = 3 # Set player version 2 or 3

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_303_LiveNGPass_PreviewMode')
        self.logi.initMsg('test_303_LiveNGPass_PreviewMode')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_303_LiveNGPass_PreviewMode(self):
        global testStatus
        try:
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
           # Create Admin ks
            self.logi.appendMsg('INFO - Going to created admin KS by API.session.start')
            user_id = "AdminKS_USER_ID" + str(datetime.datetime.now())
            k_type = KalturaSessionType.ADMIN
            expiry = None
            privileges = ""
            ksAdmin = str(self.client.session.start(self.UserSecret, user_id, k_type, self.PublisherID, expiry, privileges))
            self.logi.appendMsg('INFO - Created admin KS by API.ksAdmin = ' + ksAdmin)

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Passthrough')
            Transobj = Transcoding.Transcoding(self.client, 'Passthrough')
            self.passtrhroughId = Transobj.CreateConversionProfileFlavors(self.client, 'Passthrough', '32,36,37')
            if isinstance(self.passtrhroughId, bool):
                testStatus = False
                return

            # Create player of latest version -  Create V2/3 Player
            self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion)  + ' player')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            if self.PlayerVersion == 2:
                self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            elif self.PlayerVersion == 3:
                self.player = myplayer.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            else:
                self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
            if isinstance(self.player,bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest V'  + str(self.PlayerVersion)  + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')

            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)

            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0,explicitLive=1)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            time.sleep(2)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                if self.IsSRT == True:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primarySrtBroadcastingUrl
                    primarySrtStreamId = self.streamUrl[i].primarySrtStreamId
                    self.logi.appendMsg("INFO - ************** Going to stream SRT with entryId = " + str(self.entryId) + " *************")
                else:
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                if self.env == 'testing':
                    if self.Live_Change_Cluster == True:
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                #******* CHECK CPU usage of streaming machine
                #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
                self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#" + str(i) + ", entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))
                cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"
                rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)
                if rc == True:
                    self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
                else:
                    self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                    testStatus = False
                    return

                #****** Livedashboard - Channels tab
                time.sleep(5)
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

                time.sleep(10)

                ##################################

                # Playback verification when explicitLive=1 enable of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) of " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + " with ADMIN KS when explicitLive=1 enable - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " with ADMIN KS explicitLive=1 enable -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                ################################ SET GO LIVE
                self.logi.appendMsg("INFO - Going to perform GO LIVE viewMode = 1 to entryId= " + str(self.entryId) + "  time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 1 #Go live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)

                # Playback verification of all entries
                time.sleep(30) #Wait for GO LIVE backend cache
                self.logi.appendMsg("INFO - Going to verify playback After updating GO LIVE viewMode = 1  for " + str(self.RestartDowntime) + ", boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=True -> Meaning the entry should play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst_GoLive, True, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback(boolShouldPlay=True) of " + str(entryGoLiveState.id) + " After updating GO LIVE viewMode = 1 - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                ################################ SET END LIVE
                self.logi.appendMsg("INFO - Going to perform END LIVE viewMode = 0 to entryId= " + str(self.entryId) + "  time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 0  # END live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)

                # Playback verification of all entries
                time.sleep(30)  # Wait for GO LIVE backend cache

                ##################################

                # Playback verification when viewMode=0 END LIVE of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False viewMode=0 END LIVE--> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) and viewMode=0 END LIVE of " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + " with ADMIN KS when viewMode=0 END LIVE - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars,ServerURL=self.ServerURL)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " with ADMIN KS and viewMode=0 END LIVE -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                ####################################################
                #kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return

        except Exception as Exp:
               print(Exp)
               testStatus = False
               pass

        
    #=============================================================================
    # TEARDOWN   
    #=============================================================================
    
    def teardown_class(self):
        
        global testStatus
        
        print('#############')
        print(' Tear down')

        try:
            print('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '303','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '303','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    pytest.main(['test_303_LiveNGPass_PreviewMode.py', '-s'])
    #===========================================================================
        
        
        