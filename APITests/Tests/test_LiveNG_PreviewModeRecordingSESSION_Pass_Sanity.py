
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_LiveNG_PreviewModeRecordingSESSION_Pass_Sanity.py
 
 @desc : This test check E2E test of new LiveNG entries Passthrough + PREVIEWMODE ON + Recording SESSION by Creating new live entry with explicitLive=1 enable  and start streaming and then
 Playback with/out USER KS and ADMIN KS
 Updating GO LIVE preview mode -> Verify live entry playback by refreshing/opening new browser
 Verify that recorded entry is created only after GO LIVE.
 Verify that the recorded entry is played ok.
 Verify that the recorded entry stopped recording after END LIVE and then mp4 flavours are uploaed.
 Verify duration of the recording entry.

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
 '''


import datetime
import os
import sys
import time
import pytest

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

##########
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
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.sniffer_fitler_After_Mp4flavorsUpload = 'cfvod'
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
            self.sniffer_fitler_After_Mp4flavorsUpload = 'qa-nginx-vod'
            print('TESTING ENVIRONMENT') 
        self.sendto = "moran.cohen@kaltura.com;"           
          
        #***** SSH streaming server - AWS LINUX
        self.remote_host = "liveng-core3-automation.kaltura.com"#"34.201.96.171"#"liveng-core3-automation.kaltura.com"
        self.remote_user = "root"
        self.remote_pass = "testingqa" #"Vc9Qvx%J5PJNxG%$Wo@ad9xZAHJEg?P9"#"testingqa"
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4" 
        #=======================================================================
        # #***** SSH streaming server - liveng-core3-automation.kaltura.com
        # self.remote_host = "liveng-core3-automation.kaltura.com"
        # self.remote_user = "root"
        # self.remote_pass = "testingqa"  
        # self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"            
        #=======================================================================
        #=======================================================================
        # **** SSH streaming computer - Ilia computer
        # self.remote_host = "192.168.162.176"
        # self.remote_user = "root"
        # self.remote_pass = "Kaltura12#"
        # self.filePath = "/home/kaltura/tests/stream_liveNG_custom_entry_AUTOMATION.sh"
        # ***** SSH streaming computer - dev-backend4
        # self.remote_host = "dev-backend4.dev.kaltura.com"
        # self.remote_user = "root"
        # self.remote_pass = "1q2w3e4R"  
        # self.filePath = "/root/LiveNG/ffmpeg_data/entries/LongCloDvRec.mp4"
        #=======================================================================
        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.RestartDowntime = 60
        self.PlayerVersion = 3 # Set player version 2 or 3
        self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")                   
        self.logi = reporter2.Reporter2('test_212_LiveNG_PreviewModeRecordingSESSION_Pass_Sanity')
        self.logi.initMsg('test_212_LiveNG_PreviewModeRecordingSESSION_Pass_Sanity')
        self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_212_LiveNG_PreviewModeRecordingSESSION_Pass_Sanity(self):
        global testStatus
        try: 
           # create client session
            self.logi.appendMsg('INFO - start create session for partner: ' + self.PublisherID)
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
            Transobj = Transcoding.Transcoding(self.client,'Passthrough')
            self.passtrhroughId = Transobj.getTranscodingProfileIDByName('Passthrough')
            if self.passtrhroughId==None:
                self.passtrhroughId = Transobj.addTranscodingProfile(1,'32,36,37')
                if isinstance(self.passtrhroughId,bool):
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
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-AWS_LINUX_LiveEntry_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None,dvrStatus=1,explicitLive=1,recordStatus=2)  # 2 : KalturaRecordStatus.PER_SESSION,  # 1 : explicitLive enable # 1 :dvrStatus enable
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
                
            time.sleep(2)
            #**** Login LiveDashboard 
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.LiveDashboard.invokeLiveDashboardLogin(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL,self.env)
            if(rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:       
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
            time.sleep(2)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id) 
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
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

                ####### Verify that there is NO recordedEntryId before GO LIVE state - Try to Get recordedEntryId from the live entry by API
                self.logi.appendMsg("INFO - Going to verify that recordedEntryId is not created of LIVE ENTRY = " + self.entryId + "before GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                FirstRecording_EntryID = entryLiveStream.recordedEntryId
                if FirstRecording_EntryID != "":
                    self.logi.appendMsg("FAIL - Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")
                else:
                    self.logi.appendMsg("PASS - NOT Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")

                
                #****** Livedashboard - Channels tab  
                time.sleep(5)   
                navigateTo= "Channels"
                self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                    testStatus = False
                    return
                time.sleep(2)
                # Return row data from Channels
                #rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo,True)
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd, self.entryId, navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env=self.env)
                    if(rc):
                        self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on Channels tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        if self.env == 'testing':
                            testStatus = False
                else:       
                    self.logi.appendMsg("FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
                # LiveDashboard - Alerts tab
                time.sleep(2)
                navigateTo= "Alerts"
                self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo= " + navigateTo)
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd,navigateTo,env=self.env)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo + ",  entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
                 # Return row data from Alerts
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env=self.env)
                    if(rc):
                        self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    else:
                        self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False    
                else:       
                    self.logi.appendMsg("FAIL -ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
                 
                #Close LiveDashboard window
                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                self.Wd.quit()
                time.sleep(10)

                ##################################

                # Playback verification when explicitLive=1 enable of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion)
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
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of " + str(self.entryId) + " with ADMIN KS explicitLive=1 enable -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                ################################ SET GO LIVE
                self.logi.appendMsg("INFO - Going to perform GO LIVE viewMode = 1 to entryId= " + str(self.entryId) + " time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 1 #Go live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                GO_LIVE_time = datetime.datetime.now().timestamp()

                time.sleep(30)  # Wait for GO LIVE backend cache
                ####### Get recordedEntryId from the live entry by API after GO LIVE STATE
                self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + self.entryId + " after GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                recorded_entry = KalturaBaseEntry()
                recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
                FirstRecording_EntryID = entryLiveStream.recordedEntryId
                if FirstRecording_EntryID == "":
                    self.logi.appendMsg("FAIL - NOT Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId + " after GO LIVE STATE.")
                    testStatus = False
                    return
                self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(FirstRecording_EntryID) + '\')')
                self.recorded_entrieslst = []
                self.recorded_entrieslst.append(recorded_entry)
                self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)

                # Playback verification of all LIVE entries
                self.logi.appendMsg("INFO - Going to verify playback on LIVE entry After updating GO LIVE viewMode = 1 , boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entry on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=True -> Meaning the entry should play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst_GoLive, True, PlayerVersion=self.PlayerVersion)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback(boolShouldPlay=True) of Live entry " + str(entryGoLiveState.id) + " After updating GO LIVE viewMode = 1 - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                ##############

                # Waiting about 1.5 until recording entry is playable from klive
                #self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                #time.sleep(90)
                # RECORDED ENTRY - Playback verification of all entries
                self.logi.appendMsg("INFO - AFTER GO LIVE:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http")
                    # rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True, PlayerVersion=self.PlayerVersion,Protocol="http")
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                ################################ SET END LIVE
                self.logi.appendMsg("INFO - Going to perform END LIVE viewMode = 0 to entryId= " + str(self.entryId) + "  time = " + str(datetime.datetime.now()))
                live_stream_entry = KalturaLiveStreamEntry()
                # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
                # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
                live_stream_entry.viewMode = 0  # END live
                entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
                self.entrieslst_GoLive = []
                self.entrieslst_GoLive.append(entryGoLiveState)
                END_LIVE_time = datetime.datetime.now().timestamp()  # Save END LIVE time of stream

                # Playback verification of all entries
                time.sleep(30)  # Wait for GO LIVE backend cache

                ##################################

                # Playback verification when viewMode=0 END LIVE of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False viewMode=0 END LIVE for LIVE entry--> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    # boolShouldPlay=False -> Meaning the entry should not play
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) and viewMode=0 END LIVE of LIVE entry " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play LIVE entry " + str(self.entryId) + " with ADMIN KS when viewMode=0 END LIVE - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,flashvars=flashvars)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        # return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - Playback of LIVE entry " + str(self.entryId) + " with ADMIN KS and viewMode=0 END LIVE -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                #####################################*********** PLAY RECORDING after END LIVE
                # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
                self.logi.appendMsg("INFO - Wait about 1 minutes after END LIVE and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                time.sleep(60)
                # Check mp4 flavors upload of recorded entry id
                self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 15 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client, FirstRecording_EntryID, recorded_entry,expectedFlavors_totalCount=1) #expectedFlavors_totalCount=1 for passthrough
                if rc == True:
                    self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2/NA-4) .recordedEntryId" + entryLiveStream.recordedEntryId)
                    ################
                    ######## Get conversion version of VOD entry
                    # entry_id = entryLiveStream.recordedEntryId
                    context_data_params = KalturaEntryContextDataParams()
                    First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                    timeout = 0
                    while First_RecordedEntry_Version == None or First_RecordedEntry_Version == 0:
                        time.sleep(20)
                        First_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                        timeout = timeout + 1
                        if timeout >= 30:  # 10 minutes timeout for waiting to version update
                            self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId)
                            testStatus = False
                            return
                    ################
                    durationFirstRecording = int(self.client.baseEntry.get(FirstRecording_EntryID).duration)  # Save the duration of the recording entry after mp4 flavors uploaded
                    self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
                else:
                    self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return

                # Waiting about 1 minutes before playing the recorded entry after mp4 flavors uploaded with ready status
                self.logi.appendMsg("INFO - Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                time.sleep(60)
                # #####################################################
                # Create new player of latest version -  Create V2/3 Player because of cache isse
                self.logi.appendMsg('INFO - Going to create latest V' + str(self.PlayerVersion) + ' player')
                myplayer = uiconf.uiconf(self.client, 'livePlayer')
                if self.PlayerVersion == 2:
                    self.player = myplayer.addPlayer(None, self.env, False, False)  # Create latest player v2
                elif self.PlayerVersion == 3:
                    self.player = myplayer.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
                else:
                    self.logi.appendMsg('FAIL - There is no player version =  ' + str(self.PlayerVersion))
                if isinstance(self.player, bool):
                    testStatus = False
                    return
                else:
                    self.playerId = self.player.id
                self.logi.appendMsg('INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
                self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
                self.liveObj.playerId = self.playerId
                # #####################################################
                # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
                self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http")
                    # rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.recorded_entrieslst, True, PlayerVersion=self.PlayerVersion,Protocol="http")
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True:
                        seenAll = True

                self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                ########### DURATION Compare for recording entry

                # Cal recording duration after mp4 flavors are uploaded
                self.logi.appendMsg("INFO - AAFTER END LIVE:Going to verify DURATION of recorded entry.FirstRecording_EntryID = " + str(FirstRecording_EntryID))
                recordingTime1 = int(END_LIVE_time - GO_LIVE_time)
                if recordingTime1 > int(durationFirstRecording):
                    deltaRecording1=recordingTime1-durationFirstRecording
                else:
                    deltaRecording1 = durationFirstRecording - recordingTime1
                #if 0 <= int(recordingTime1) % int(durationFirstRecording) <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                if 0 <= deltaRecording1 <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                    self.logi.appendMsg("PASS - AFTER END LIVE:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
                else:
                    self.logi.appendMsg("FAIL - AFTER END LIVE:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                    testStatus = False
                #################################################### until here
                #kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
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
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        
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
           self.practitest.post(Practi_TestSet_ID, '212','1')
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID, '212','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    pytest.main(['test_LiveNG_PreviewModeRecordingSESSION_Pass_Sanity.py', '-s'])
    #===========================================================================
        
        
        