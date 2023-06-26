'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen
@test_name: test_x881_MultiAudioKorTur_Trans_PreviewMode_SESSIONRecording_RestartAbove5min_redirectEntry.py
 @desc : this test check E2E test of new LiveNG entries multi audio + SESSION recording with RTMP streaming by new logic function - host access run ffmpeg cmd
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 Create live entry with multi audio
 LIVE entry playback by Capture2Text  + Switch Language by player selector.
 VOD/RECORDED entry playback from klive sniffer  + Switch Language by player selector.
 flavorAssets status (mp4 flavor upload) by API
 VOD/RECORDED entry1 playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
 Restart streaming above 5 minutes
 VOD/RECORDED entry2 playback after mp4 flavor uploaded by checking sniffer verification from aws/cfvod/qa-nginx-vod
 Compare duration - Cal recording duration after mp4 flavors are uploaded.
 VOD/RECORDED entry playback from aws sniffer  + Switch Language by player selector. --- > BUG When playing recording entry with multi-audio from AWS->Espanol appears instead of Spanish(from klive Spanish)
 https://kaltura.atlassian.net/browse/LIV-868
 The bug occurs only on QA env - I added code for it
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
from KalturaClient.Plugins.Core import *
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
isProd = os.getenv('isProd')
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
            #self.playerId = "48120213"# DASH v3 player
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL') #"http://52.90.42.173/dashboard/channels"
            self.sniffer_fitler_After_Mp4flavorsUpload = 'cfvod'
            print('PRODUCTION ENVIRONMENT')
            
        else:
            section = "Testing"
            inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
            self.env = 'testing'
            # Streaming details
            self.url= "qa-apache-php7.dev.kaltura.com"
            #self.playerId = "15236707" #dash player v3
            self.PublisherID = inifile.RetIniVal(section, 'LIVENG_PublisherID')
            self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
            self.UserSecret = inifile.RetIniVal(section, 'LIVENG_UserSecret')
            self.LiveDashboardURL = inifile.RetIniVal(section, 'LiveDashboardURL')
            self.sniffer_fitler_After_Mp4flavorsUpload = 'qa-nginx-vod'#'qa-aws-vod'c
            print('TESTING ENVIRONMENT') 
        self.sendto = "moran.cohen@kaltura.com;"           
        #***** SSH streaming server - AWS LINUX
        self.remote_host = "54.91.159.104"#"34.201.96.171"
        self.remote_user = "root"
        self.remote_pass = "uZc^hii4TRJjQv2ZBM0O962Vqx*!A4m"
        self.filePath = "/home/kaltura/entries/disney_ma.mp4"

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.PlayerVersion = 3 # player version 2 or 3
        self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        self.RestartDowntime = 300 # 5 minutes
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()         
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_881_MultiAudioKorTur_Trans_PreviewMode_SESSIONRecording_RestartAbove5min_redirectEntry')
        self.logi.initMsg('test_881_MultiAudioKorTur_Trans_PreviewMode_SESSIONRecording_RestartAbove5min_redirectEntry')
        self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)


    def test_881_MultiAudioKorTur_Trans_PreviewMode_SESSIONRecording_RestartAbove5min_redirectEntry(self):
        global testStatus
        try:

           # create client session
            self.logi.appendMsg('start create session for partner: ' + self.PublisherID)
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

            ''' RETRIEVE TRANSCODING ID AND CREATE MULTI AUDIO Eng+SPA partner 0 profile IF NOT EXIST'''
            Transobj = Transcoding.Transcoding(self.client, 'AUTOMATION_cloud hd kor tur')
            self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('AUTOMATION_cloud hd kor tur')
            if self.CloudtranscodeId == None:
                self.CloudtranscodeId = Transobj.addTranscodingProfile(1, '32,33,34,35,42,43,112,113')
                if isinstance(self.CloudtranscodeId, bool):
                    testStatus = False
                    return

            #Create player of latest version -  Create V2/3 Player
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-MULTIAUDIO_RECORDING_SESSION_DVR_RESTART_5_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(recordStatus=2,dvrStatus=1,explicitLive=1) # 2 : KalturaRecordStatus.PER_SESSION , dvrStatus 1 for enable , explicitLive enable 1
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
            
            time.sleep(2)
            #**** Login LiveDashboard 
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.LiveDashboard.invokeLiveDashboardLogin(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL,env=self.env)
            if(rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:       
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
            time.sleep(5)
            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id) 
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                #ffmpegCmdLine=self.liveObj.ffmpegCmdString(self.filePath, str(self.streamUrl[i].primaryBroadcastingUrl), self.entryId)
                ffmpegCmdLine = self.liveObj.ffmpegCmdString_MultiAudio(self.filePath,str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId,languages="KoreanTurkish")
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return
                # ******* CHECK CPU usage of streaming machine
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
                navigateTo= "Channels"
                self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
                rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo,env=self.env)
                if(rc):
                    self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                else:       
                    self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                    testStatus = False
                    return
                # Return row data from Channels
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
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
            try:
                self.logi.appendMsg("INFO - Going to close the LiveDashboard.")
                self.Wd.quit()
                time.sleep(2)
            except Exception as Exp:
                print(Exp)
                pass

            ####### Verify that there is NO recordedEntryId before GO LIVE state - Try to Get recordedEntryId from the live entry by API
            self.logi.appendMsg("INFO - Going to verify that recordedEntryId is not created of LIVE ENTRY = " + self.entryId + "before GO LIVE STATE.")
            entryLiveStream = self.client.liveStream.get(self.entryId)
            FirstRecording_EntryID = entryLiveStream.recordedEntryId
            if FirstRecording_EntryID != "":
                self.logi.appendMsg("FAIL - Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")
            else:
                self.logi.appendMsg("PASS - NOT Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")

            ###########################**********************************************ADDD WORKING ON

            # Playback verification when explicitLive=1 enable of all entries - USER KS-->NO playback
            self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                # boolShouldPlay=False -> Meaning the entry should not play
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst,False,PlayerVersion=self.PlayerVersion)
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
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True, PlayerVersion=self.PlayerVersion,flashvars=flashvars,MultiAudio=True,languageList="Korean;Turkish")
                time.sleep(5)
                if not rc:
                    testStatus = False
                    # return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of " + str(
                self.entryId) + " with ADMIN KS explicitLive=1 enable -  live entries on preview&embed page during - MinToPlay=" + str(
                self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ################################ SET GO LIVE
            self.logi.appendMsg("INFO - Going to perform GO LIVE viewMode = 1 to entryId= " + str(self.entryId) + " time = " + str(datetime.datetime.now()))
            live_stream_entry = KalturaLiveStreamEntry()
            # Example , genks 6602 | kalcli livestream update entryId=0_991f880v liveStreamEntry:objectType=KalturaLiveStreamAdminEntry liveStreamEntry:viewMode=1
            # viewMode is 1 for ALLOW (go live) and 0 for PREVIEW
            live_stream_entry.viewMode = 1  # Go live
            entryGoLiveState = self.client.liveStream.update(str(self.entryId), live_stream_entry)
            self.entrieslst_GoLive = []
            self.entrieslst_GoLive.append(entryGoLiveState)
            GO_LIVE_time = datetime.datetime.now().timestamp()

            time.sleep(30)  # Wait for GO LIVE backend cache
            ####### Get recordedEntryId from the live entry by API after GO LIVE STATE
            self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + str(self.entryId) + " after GO LIVE STATE.")
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


            #################################*****************************************************

            # LIVE ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play LIVE ENTRY " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    #rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion)
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True,languageList="Korean;Turkish")
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True

            self.logi.appendMsg("PASS - LIVE ENTRY Playback of " + str(self.entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### Get recordedEntryId from the live entry by API
            self.logi.appendMsg("INFO - Going to take recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            FirstRecording_EntryID=entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(FirstRecording_EntryID) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - Waiting 1.5 mintues until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http")
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            #kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                testStatus = False
                return
            stop_time = datetime.datetime.now().timestamp() # Save stop time of stream

            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,FirstRecording_EntryID, recorded_entry,expectedFlavors_totalCount=3) # 3 expectedFlavors_totalCount is multi audio
            if rc == True:
                self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
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
                durationFirstRecording = int(self.client.baseEntry.get(FirstRecording_EntryID).duration)#Save the duration of the recording entry after mp4 flavors uploaded
                self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
            else:
                self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            # Waiting about 1 minutes before playing the recored entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # #####################################################
            #Create new player of latest version -  Create V2/3 Player because of cache isse
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
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",languageList=languageList)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ###############################################################
            deltaTime = datetime.datetime.now().timestamp() - stop_time
            deltaTime = int(deltaTime)
            if deltaTime <= self.RestartDowntime:
                deltaTime = self.RestartDowntime - deltaTime
                time.sleep(deltaTime)

            # Get entryId and start streaming primaryBroadcastingUrl live entries
            for i in range(0, self.NumOfEntries):
                self.entryId = str(self.entrieslst[i].id)
                self.logi.appendMsg("INFO - ************** AFTER RESTART STREAMING above " + str(self.RestartDowntime) + " seconds - Going to ssh Start_StreamEntryByffmpegCmd.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                start_streaming2 = datetime.datetime.now().timestamp()
                #ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath,str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
                ffmpegCmdLine = self.liveObj.ffmpegCmdString_MultiAudio(self.filePath,str(self.streamUrl[i].primaryBroadcastingUrl),self.entryId)
                rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host,self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=self.streamUrl[i].primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                    testStatus = False
                    return
            ######################################## START
            # LIVE ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING: Going to play LIVE ENTRY " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll==False:
                    #rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion)
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True)
                    time.sleep(5)
                    if not rc:
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag ==True:
                        seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:LIVE ENTRY Playback of " + str(self.entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

            ####### AFTER RESTART STREAMING:Get recordedEntryId from the live entry by API
            OLD_Recording_entryId= str(recorded_entry.id) # Save the previous vod/recording entry id
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to take NEW recordedEntryId of LIVE ENTRY = " + self.entryId)
            entryLiveStream = self.client.liveStream.get(self.entryId)
            recorded_entry = KalturaBaseEntry()
            recorded_entry = self.client.baseEntry.update(entryLiveStream.recordedEntryId, recorded_entry)
            SecondRecording_EntryID = entryLiveStream.recordedEntryId
            self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(SecondRecording_EntryID) + '\')')
            self.recorded_entrieslst = []
            self.recorded_entrieslst.append(recorded_entry)
            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Found recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " of LIVE ENTRY = " + self.entryId)
            # Waiting about 1.5 until recording entry is playable from klive
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Waiting 1.5 minutes until recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            # Compare old vod entry to new vod entry
            if OLD_Recording_entryId == str(recorded_entry.id):
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:New recordedEntryId is NOT created.OLD_Recording_entryId = " + OLD_Recording_entryId + ", New recording entryId = " + str(recorded_entry.id) + ", LIVE ENTRY = " + self.entryId)
                testStatus = False
            else:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:New recordedEntryId is created.OLD_Recording_entryId = " + OLD_Recording_entryId + ", New recording entryId = " + str(recorded_entry.id) + ", LIVE ENTRY = " + self.entryId)
            time.sleep(90)
            # RECORDED ENTRY - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_Before_Mp4flavorsUpload +  " for  recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="http")
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_Before_Mp4flavorsUpload + " for  recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " on the FLY - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


            #kill ffmpeg ps
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + self.url)
                testStatus = False
                return
            stop_time2 = datetime.datetime.now().timestamp() # Save stop time of stream

            # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
            self.logi.appendMsg("INFO - Wait about 1.5 minutes after stopping streaming and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(90)
            # Check mp4 flavors upload of recorded entry id
            self.logi.appendMsg("INFO - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
            rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client,entryLiveStream.recordedEntryId, recorded_entry,expectedFlavors_totalCount=3) # expectedFlavors_totalCount=4 is for multi audio
            if rc == True:
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:Recorded Entry mp4 flavors uploaded with status OK (ready-2) .recordedEntryId" + entryLiveStream.recordedEntryId)
                ################
                ######## Get conversion version of VOD entry
                # entry_id = entryLiveStream.recordedEntryId
                context_data_params = KalturaEntryContextDataParams()
                Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId, context_data_params).flavorAssets[0].version
                timeout = 0
                while Second_RecordedEntry_Version == None or Second_RecordedEntry_Version == 0:
                    time.sleep(20)
                    Second_RecordedEntry_Version = self.client.baseEntry.getContextData(entryLiveStream.recordedEntryId,context_data_params).flavorAssets[0].version
                    timeout = timeout + 1
                    if timeout >= 30:  # 10 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Version is not updated on baseEntry.getContextData after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId + ", Second_RecordedEntry_Version = " + str(Second_RecordedEntry_Version))
                        testStatus = False
                        return
                ################
                durationSecondRecording = int(self.client.baseEntry.get(SecondRecording_EntryID).duration)#Save the duration of the second recorded entry id after mp4 flaovrs uploaded
                timeout = 0
                while durationSecondRecording == 0:
                    time.sleep(30)
                    durationSecondRecording = int(self.client.baseEntry.get(SecondRecording_EntryID).duration)#Save the duration of the second recorded entry id after mp4 flaovrs uploaded
                    timeout = timeout + 1
                    if timeout >= 10:  # 5 minutes timeout for waiting to version update
                        self.logi.appendMsg("FAIL - TIMEOUT - Duration of Second Recording is not updated on baseEntry.get.duration after mp4 flavors are uploaded. recordedEntryId = " + entryLiveStream.recordedEntryId + " , durationSecondRecording" + str(durationSecondRecording))
                        testStatus = False
                        return
                self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - Second_RecordedEntry_Version = " + str(Second_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                testStatus = False
                return

            # Waiting about 1 minutes before playing the recored entry after mp4 flavors uploaded with ready status
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Wait about 1 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
            time.sleep(60)
            # #####################################################
            #Create new player of latest version -  Create V2/3 Player because of cache isse
            self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Going to create latest V' + str(self.PlayerVersion) + ' player')
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
            time.sleep(10)
            self.logi.appendMsg('INFO - AFTER RESTART STREAMING:Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
            self.liveObj.playerId = self.playerId
            # #####################################################
            # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                if self.env == 'prod':
                    languageList = "Spanish;English"
                else:  # testing
                    languageList = "Español;English"
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,MultiAudio=True,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",languageList=languageList)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - AFTER RESTART STREAMING:RECORDED ENTRY Playback from " + self.sniffer_fitler_After_Mp4flavorsUpload + " of " + str(entryLiveStream.recordedEntryId) + " after MP4 flavors uploaded - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            # Cal recording duration after mp4 flavors are uploaded
            self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Going to verify DURATION of both recorded entries.FirstRecording_EntryID = " + str(FirstRecording_EntryID) + " , SecondRecording_EntryID = " + str(SecondRecording_EntryID))
            recordingTime1=int(stop_time-start_streaming)
            recordingTime2=int(stop_time2-start_streaming2)
            Expected_TotalRecordingTime=int(recordingTime1 + recordingTime2) # Expected total duration of the two vod entries
            Actual_TotalRecordingTime=int(durationFirstRecording + durationSecondRecording) # Actual total duration of the two vod entries
            if 0 <= int(recordingTime1) % int(durationFirstRecording) <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                testStatus = False
            if 0 <= int(recordingTime2) % int(durationSecondRecording) <= 40:  # Until 40 seconds of delay between expected to actual duration of the second vod entry2
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:VOD entry2:durationSecondRecording duration is ok Actual_durationSecondRecording=" + str(durationSecondRecording) + " , Expected_recordingTime1 = " + str(recordingTime2) + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:VOD entry2:durationSecondRecording is NOT as expected -  Actual_durationSecondRecording=" + str(durationSecondRecording)) + " , Expected_recordingTime1 = " + str(recordingTime2) + ", SecondRecording_EntryID = " + str(SecondRecording_EntryID)
                testStatus = False
            #Compare total duration of the two vod entries
            if 0 <= int(Expected_TotalRecordingTime) % int(Actual_TotalRecordingTime) <= 80:#Until 80 seconds of delay between expected to actual duration
                self.logi.appendMsg("PASS - AFTER RESTART STREAMING:TOTAL recording duration is OK for two VOD entries. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime))
            else:
                self.logi.appendMsg("FAIL - AFTER RESTART STREAMING:TOTAL recording duration is NOT as expected for two VOD entries. Actual_TotalRecordingTime=" + str(Actual_TotalRecordingTime) + " , Expected_TotalRecordingTime = " + str(Expected_TotalRecordingTime))
                testStatus = False

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
        try:
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        print('Tear down - testTeardownclass')
        
        try:
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
        except Exception as Exp:
           print(Exp)
           pass
        print('#############')
        if testStatus == False:
           print("fail")
           self.practitest.post(Practi_TestSet_ID,'881','1')
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(Practi_TestSet_ID,'881','0')
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_x881_MultiAudioKorTur_Trans_PreviewMode_SESSIONRecording_RestartAbove5min_redirectEntry.py -s')
    #===========================================================================
        
        
        