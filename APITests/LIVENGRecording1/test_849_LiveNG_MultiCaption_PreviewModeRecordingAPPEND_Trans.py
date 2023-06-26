
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_849_LiveNG_MultiCaption_PreviewModeRecordingAPPEND_Trans.py
 
 @desc : This test check E2E test of new LiveNG entries transcoding + PREVIEWMODE + multi captions(English,Spanish,German) ON + Recording APPEND by Creating new live entry with explicitLive=1 enable  and start streaming and then
 Create live entry with multi KalturaStreamContainer by API.
 Playback with USER KS and ADMIN KS.
 Updating GO LIVE preview mode by API -> Verify live entry playback  + Switch Language by player selector.
 Verify that recorded entry is created only after GO LIVE.
 Verify that the recorded entry is played OK from klive by sniffer logic.
 Verify that the recorded entry stopped recording after END_LIVE and then mp4 flavors are uploaded.
 Verify actual captionAssets data(id,label,status) by API.
 Verify that the recorded entry is played OK from aws  + Switch Language by player selector.----> OPEN BUG https://kaltura.atlassian.net/browse/LIV-856
 Verify duration of the recording entry.
 Verify that the recorded entry is played ok from aws by sniffer logic + Switch Language by player selector.
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
from KalturaClient.Plugins.Caption import *
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

class TestClass:
        
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):

        StaticMethods.before_run(self)

        # set live LiveDashboard URL
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')

        # Recording after mp4 files are uploaded
        self.sniffer_fitler_After_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_After_Mp4flavorsUpload')  # QA 'qa-aws-vod'  # PROD 'cfvod'
        self.sniffer_fitler_Before_Mp4flavorsUpload = self.inifile.RetIniVal(self.section+self.ConfigId,'sniffer_fitler_Before_Mp4flavorsUpload')  # QA and Prod klive->regular DP (cflive ->DP CF)
        # Environment BE server URL
        if self.ServerURL is None:
            self.ServerURL = self.inifile.RetIniVal('Environment', 'ServerURL')
        print("ServerURL = " + self.ServerURL)
        # LiveNG config partner:
        if self.PartnerID != None:
            self.PublisherID = self.PartnerID
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'LIVENG_UserSecret')
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
        # Jenkis run LIVENGRecording1
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGRecording1')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENGRecording1')
        self.remote_pass = ""
        #self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        self.filePath = "/home/kaltura/entries/close-caption_k_ts.txt"
        # Update KalturaStreamContainer with the following order in array - id,type,language,label
        '''
        id = SERVICE1 for eng
        SERVICE2 for spa
        SERVICE3 for deu
        '''
        #Caption assets
        self.KalturaStreamContainerArray = [["SERVICE1", "closedCaptions","eng","English"], ["SERVICE2", "closedCaptions","spa","Spanish"],["SERVICE3", "closedCaptions","deu","German"]]
        self.ASSET_STATUS_READY = 2 # status ready of captionAsset
        self.CntOfCaptions = 3
        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.RestartDowntime = 60
        self.PlayerVersion = 3 # Set player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
        self.ClosedCaption_PlayerV7_config = ClosedCaption_PlayerV7_config = '{\
                             "disableUserCache": false,\
                             "text": {\
                               "enableCEA708Captions": true\
                             },\
                             "plugins": {\
                               "kava": {},\
                               "kaltura-live": {}\
                             },\
                             "viewability": {\
                               "playerThreshold": 50\
                             },\
                             "provider": {\
                               "env": {}\
                             },\
                             "playback": {\
                               "enabled": true\
                             }\
                           }'
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_849_LiveNG_MultiCaption_PreviewModeRecordingAPPEND_Trans')
        self.logi.initMsg('test_849_LiveNG_MultiCaption_PreviewModeRecordingAPPEND_Trans')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_849_LiveNG_MultiCaption_PreviewModeRecordingAPPEND_Trans(self):
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

            ''' RETRIEVE TRANSCODING ID AND CREATE cloud transcode IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Cloud transcode')
            Transobj = Transcoding.Transcoding(self.client, 'Cloud transcode')
            self.CloudtranscodeId = Transobj.CreateConversionProfileFlavors(self.client, 'Cloud transcode', '32,33,34,35')
            if isinstance(self.CloudtranscodeId, bool):
                testStatus = False
                return

            # Create player of latest version -  Create V2/3 Player
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
                # Update the config with closed caption of the new player v3/7
                id = int(self.player.id)
                ui_conf = KalturaUiConf()
                ui_conf.config = self.ClosedCaption_PlayerV7_config
                result = self.client.uiConf.update(id, ui_conf)

            self.logi.appendMsg('INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')

            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-MULTI_Caption_ENTRY_PEVIEWMODE_RECORDING_APPEND_DVR_trans' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None,dvrStatus=1,explicitLive=1,recordStatus=1)  # 1 : KalturaRecordStatus.APPENDED,,  # 1 : explicitLive enable # 1 :dvrStatus enable
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)
                ######## ADD adminTag and Containers to liveStream entry - It is required for VOD captions
                # entry_id = self.entry.id
                rc=self.liveObj.CreateStreamContainer(self.client,self.KalturaStreamContainerArray,self.entry.id)
                if rc == False:
                    self.logi.appendMsg("FAIL - Update StreamContainer.EntryID = " + str( self.entry.id))

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
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT_ClosedCaption(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString_ClosedCaption(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                start_streaming = datetime.datetime.now().timestamp()
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

                ####### Verify that there is NO recordedEntryId before GO LIVE state - Try to Get recordedEntryId from the live entry by API
                self.logi.appendMsg("INFO - Going to verify that recordedEntryId is not created of LIVE ENTRY = " + self.entryId + "before GO LIVE STATE.")
                entryLiveStream = self.client.liveStream.get(self.entryId)
                FirstRecording_EntryID = entryLiveStream.recordedEntryId
                if FirstRecording_EntryID != "":
                    self.logi.appendMsg("FAIL - Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")
                else:
                    self.logi.appendMsg("PASS - NOT Found recordedEntryId of LIVE ENTRY = " + self.entryId + " before GO LIVE STATE.")


                time.sleep(5)
                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

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

                time.sleep(15)
                if self.env == 'prod':
                    time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + " with ADMIN KS when explicitLive=1 enable - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll == False:
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,flashvars=flashvars,languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
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
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst_GoLive, True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
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
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,PlayerVersion=self.PlayerVersion,ClosedCaption=True,Protocol="http",languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
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
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, False, PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
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
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,flashvars=flashvars,languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
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
                self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client, FirstRecording_EntryID, recorded_entry,expectedFlavors_totalCount=4) #expectedFlavors_totalCount=1 for transcoding
                if rc == True:
                    self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2/NA-4) .recordedEntryId" + entryLiveStream.recordedEntryId)
                    ################
                    ######## Get conversion version of VOD entry
                    # entry_id = entryLiveStream.recordedEntryId
                    context_data_params = KalturaEntryContextDataParams()
                    filter = KalturaAssetFilter()
                    pager = KalturaFilterPager()
                    filter.entryIdEqual= FirstRecording_EntryID
                    First_RecordedEntry_Version = self.client.flavorAsset.list(filter, pager).objects[0].version
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
                    self.logi.appendMsg("INFO - AFTER END LIVE:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
                else:
                    self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return
                ########### DURATION Compare for recording entry
                # Cal recording duration after mp4 flavors are uploaded
                self.logi.appendMsg("INFO - AFTER END LIVE:Going to verify DURATION of recorded entry.FirstRecording_EntryID = " + str(
                        FirstRecording_EntryID))
                recordingTime1 = int(END_LIVE_time - GO_LIVE_time)
                if recordingTime1 > int(durationFirstRecording):
                    deltaRecording1 = recordingTime1 - durationFirstRecording
                else:
                    deltaRecording1 = durationFirstRecording - recordingTime1
                if 0 <= deltaRecording1 <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                    self.logi.appendMsg("PASS - AFTER END LIVE:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
                else:
                    self.logi.appendMsg("FAIL - AFTER END LIVE:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                    testStatus = False

                #######################CAPTION ASSETS ON VOD entry
                self.logi.appendMsg("INFO -  AFTER END LIVE:Going to verify captionAssetList_result on recordedEntryId = " + entryLiveStream.recordedEntryId)
                rc = self.liveObj.captionAssetOnVODentry(self.client,self.KalturaStreamContainerArray,entryLiveStream.recordedEntryId,CntOfCaptions=self.CntOfCaptions)
                if rc != True:
                    self.logi.appendMsg("FAIL -  AFTER END LIVE:VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                    testStatus = False
                    return
                self.logi.appendMsg("PASS -  AFTER END LIVE:VOD entry captionAssetList_result verification.recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                #######################
                # Waiting about 1 minutes before playing the recorded entry after mp4 flavors uploaded with ready status
                self.logi.appendMsg("INFO - AFTER END LIVE:Wait about 1.5 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                time.sleep(90)
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
                self.logi.appendMsg("INFO - AFTER END LIVE:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
                while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 2:  # Change condition
                    # BUG Protocol="https" - Need to user https for playing caption on VOD entry
                    ##################***** Because of the bug I changed it from sniffer_fitler_After_Mp4flavorsUpload to sniffer_fitler_Before_Mp4flavorsUpload
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler_Before_Mp4flavorsUpload,Protocol="https",languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
                    time.sleep(5)
                    timeout = timeout + 1
                    if rc == False and timeout < 2:
                        self.logi.appendMsg("INFO - ****** AFTER END LIVE:Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                        time.sleep(60) #Time for player cache issue
                    if not rc and timeout >= 2:  # Change condition
                        print("FAIL - AFTER END LIVE:Going to play RECORDED ENTRY with caption after mp4 conversion - Retry count:timeout = " + str(timeout))
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True and rc != False:  # Change condition
                        seenAll = True
                        break

                #################################################### until here
                #kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by kill by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return

                ##############################################################
                time.sleep(120)
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
                self.logi.appendMsg(
                    'INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
                self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')
                self.liveObj.playerId = self.playerId
                # #####################################################
                time.sleep(60)
                # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
                self.logi.appendMsg("INFO - AFTER STOP/KILL STREAMING:Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
                seenAll = False
                timeout = 0  # ************ ADD timeout for refresh player issue - No caption icon
                while (datetime.datetime.now() <= limitTimeout and seenAll == False) or timeout < 3:  # Change condition
                    # BUG Protocol="https" - Need to user https for playing caption on VOD entry
                    rc = self.liveObj.verifyAllEntriesPlayOrNoBbyOnlyPlayback(self.recorded_entrieslst, True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="https",languageList_Caption="Spanish;English;German",ServerURL=self.ServerURL)
                    time.sleep(5)
                    timeout = timeout + 1
                    if rc == False and timeout < 2:
                        self.logi.appendMsg("INFO - ****** AFTER STOP/KILL STREAMING:Going to play AGAIN after player CACHE ISSUE (No caption ICONF on the PLAYER)RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - Try timeout_Cnt=" + str(timeout) + " , Start time = " + str(datetime.datetime.now()))
                        time.sleep(90) #Time for player cache issue
                    if not rc and timeout >= 3:  # Change condition
                        print("FAIL - AFTER STOP/KILL STREAMING:Going to play RECORDED ENTRY with caption after mp4 conversion - Retry count:timeout = " + str(timeout))
                        testStatus = False
                        return
                    if self.seenAll_justOnce_flag == True and rc != False:  # Change condition
                        seenAll = True
                        break

                ########### DURATION Compare for recording entry
                # Cal recording duration after mp4 flavors are uploaded
                self.logi.appendMsg("INFO - AFTER STOP/KILL STREAMING::Going to verify DURATION of recorded entry.FirstRecording_EntryID = " + str(FirstRecording_EntryID))
                recordingTime1 = int(END_LIVE_time - GO_LIVE_time)
                if recordingTime1 > int(durationFirstRecording):
                    deltaRecording1 = recordingTime1 - durationFirstRecording
                else:
                    deltaRecording1 = durationFirstRecording - recordingTime1
                if 0 <= deltaRecording1 <= 40:  # Until 40 seconds of delay between expected to actual duration of the first vod entry1
                    self.logi.appendMsg("PASS - AFTER STOP/KILL STREAMING:VOD entry1:durationFirstRecording duration is ok Actual_durationFirstRecording=" + str(durationFirstRecording) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID))
                else:
                    self.logi.appendMsg("FAIL - AFTER STOP/KILL STREAMING:VOD entry1:durationFirstRecording is NOT as expected -  Actual_durationFirstRecording=" + str(durationFirstRecording)) + " , Expected_recordingTime1 = " + str(recordingTime1) + ", FirstRecording_EntryID = " + str(FirstRecording_EntryID)
                    testStatus = False
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
           self.practitest.post(self.Practi_TestSet_ID,'849','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID,'849','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    #pytest.main(['test_849_LiveNG_MultiCaption_PreviewModeRecordingAPPEND_Trans.py', '-s'])
    #===========================================================================
        
        
        