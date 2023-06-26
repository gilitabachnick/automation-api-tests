
'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_961_LiveNG_CheckPlaybackForAllDP_TransDVRPreviewRecSESSION.py

Precondition:
1.Create manually access control profile that contain the wanted Delivery profile on QA and PROD env
2.Set for QA and PROD env-->self.DP_table = [['access control profile id','name of DP','dp_id1,dp_id2'],['access control profile id','name of DP','dp_id1,dp_id2']]
3.You need to add for any access control profile id also delivery profile of VOD playback (ALLOW VOD ->PROD - 20821 , QA - 29124)

 @desc : This test check E2E test of new LiveNG entries transcoding + PREVIEWMODE ON + Recording SESSION by Creating new live entry with explicitLive=1 enable  and start streaming and then
 Playback with/out USER KS and ADMIN KS -- > checkPlaybackFoAllDP (list below)
 Updating GO LIVE preview mode -> Verify live entry playback by refreshing/opening new browser.-- > checkPlaybackFoAllDP (list below)
 Verify that recorded entry is created only after GO LIVE.
 Verify that the recorded entry is played ok.-- > checkPlaybackFoAllDP (list below)
 Verify that the recorded entry stopped recording after END LIVE and then mp4 flavours are uploaded.
 Verify duration of the recording entry.

----------------- pseudocode
checkPlayBackDP:
  createEntry - DVR + rec + Explicit + transcoding...
  startStream - preview
  checkPlaybackFoAllDP() -> expect to failed
  checkPlaybackFoAllDP(ks admin) -> expect to pass
  move to Go-Live
  checkPlaybackFoAllDP() -> expect to pass
  on recording entry checkPlaybackFoAllDP()
  stop stream
checkPlaybackFoAllDP(ks = null, exclude ACP = []):
  checkPlayback()
  default ACP = getFromEntry
  for each ACP from conf:
    baseentry update with ACP
    checkPlayback() -> if in exclude ACP -> expect to fail -> else to Pass

 baseentry update with default ACP

checkPlayback: (how you do today) - you can ignore from step - E2E aka playback is good
  playmanifest -> BE
  master.m3u8 (BE/Live/...)
  index-3X.m3u8 (few index)
  seg-X.ts file playback
1095 - Live NG         -     https://klive-stg.kaltura.com/{DC}/live/hls        [AC=29392]        - PROD: 15282 [AC=5949322]--------- DONE
1033 - Live Packager HLS - redirect     - https://klive-stg.kaltura.com/{DC}/live/hls  [AC=29391]  -   PROD: 23752 [AC=5949312]--------- DONE
1119 - Live NG - dash -   http://klive-stg.kaltura.com/{DC}/live/dash             [AC=29390]     -     PROD: 16921 [AC=5949302] --------- DONE
1129 - Live NG - CF Tokenized HLS - https://cflive-qa.kaltura.com/scf/{DC}/live/hls     [AC=29389]     -   PROD: 20691 [AC=5949292](no token) --------- DONE
1132 - Live NG - CF - Redirect - HLS     - https://cflive-qa.kaltura.com/{DC}/live/hls   [AC=29388]       -   Only on QA --------- DONE
1133 - HLS - tokenized (akami)   [AC=29038,29124-VOD allow]  -   https://klive-stg.kaltura.com/s/{DC}/live/hls      - PROD: 16951  [ACP=5928562-VOD allow]  <deliveryProfileIds>16951[akami],20821[VOD allow]</deliveryProfileIds> ---- DONE

1131 - LLHLS - NG - https://klive-stg.kaltura.com/{DC}/live/llhls [AC=29293]   - PROD: give after 2.4.7 deploy ---- DONE on QA, waiting for PROD https://kaltura.atlassian.net/browse/LIV-1008

point to discuess (QA internally)
PROD: 21863:  Live AES with KMS & tokenization : http://klive.kaltura.com/s/{DC}/live/ekmshls
PROD: 19262: Live HLS - Encrypted + Tokenized      : http://klive.kaltura.com/s/{DC}/live/ehls
PROD: 10932: Live HLS - Akamai     : http://klive-a.akamaihd.net/{DC}/live/hls     (*5 for ehls, /s/, hds, dash...)
DRM ?

Because of bug https://kaltura.atlassian.net/browse/LIV-1007 - VOD entry doesn't play
The ACP-> allow delivery profiles
QA env:
Create accessControlProfile:rules:0:actions:0:deliveryProfileIds=1133[akami for example],1096[vod playback]
PROD env:
Try to add 20821 as VOD default DP (to the ACP with the dp 16951)
Notice that adding the vod DP to the ACP is true for all ACP you create if you using recording
 Create ACP with <deliveryProfileIds>16951,20821</deliveryProfileIds>
-----------------------------
PROD env - VOD:
   HLS DP of live automation --> VOD/Recording Entry DP = 15282,13952(recommended) OR just add 20821
   Dash - DP=20811
   * remove lowLatency DP/accessControl , just need adminTag=lowlatency

QA env - VOD:
  HLS DP of live automation --> VOD/recording entry DP =1096
  redirect DP= 1103
  dash DP=1097

  Examples:
  Live NG - CF - Redirect - HLS (1132) -> vod 1103
  Live NG - CF Tokenized HLS','1129'], -> vod 1103
  Live NG - dash','1119'], -> vod 1097
  Live Packager HLS - redirect','1033'], -> vod 1096
  Live NG 1095 -> 1096
  LLHLS - NG -1131 -> 1096
  LLHLS - NG - CF,'1134 -> vod 1103
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
import ast
import StaticMethods
from tabulate import tabulate
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

        # Get delivery profiles list with access control limit
        self.DP_table = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'DP_table')
        self.DP_table=ast.literal_eval(self.DP_table)# Convert string to array

        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.sendto = "moran.cohen@kaltura.com;"
        self.adminTags = "lowlatency"
        #***** SSH streaming server - AWS LINUX
        # Jenkis run LIVENGRecording
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGRecording1')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENGRecording1')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"

        self.NumOfEntries = 1
        self.NumOfDeliveryProfiles=1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        self.RestartDowntime = 60
        self.PlayerVersion = 3 # Set player version 2 or 3
        #self.sniffer_fitler_Before_Mp4flavorsUpload = 'klive'
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_961_LiveNG_CheckPlaybackForAllDP_TransDVRPreviewRecSESSION')
        self.logi.initMsg('test_961_LiveNG_CheckPlaybackForAllDP_TransDVRPreviewRecSESSION')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_961_LiveNG_CheckPlaybackForAllDP_TransDVRPreviewRecSESSION(self):
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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_CheckPlaybackDP_PEVIEWMODE_RecSESSION_DVR_Trans' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None,dvrStatus=1,explicitLive=1,recordStatus=2)  # 2 : KalturaRecordStatus.PER_SESSION,  # 1 : explicitLive enable # 1 :dvrStatus enable
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            time.sleep(5)

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
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                #******* CHECK CPU usage of streaming machine
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

                time.sleep(5)

                # Playback verification when explicitLive=1 enable of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False --> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc= self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table,client=self.client,entryList=self.entrieslst, boolShouldPlay=False,env=self.env,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) of " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(15)#Add wait for start playing
                if self.env == 'prod':
                    time.sleep(10)
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play " + str(self.entryId) + " with ADMIN KS when explicitLive=1 enable - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.entrieslst, boolShouldPlay=True,env=self.env,PlayerVersion=self.PlayerVersion,flashvars=flashvars)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
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

                # Playback verification of all LIVE entries
                self.logi.appendMsg("INFO - Going to verify playback on LIVE entry After updating GO LIVE viewMode = 1 , boolShouldPlay=True --> Going to PLAY " + str(self.entryId) + "  live entry on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.entrieslst_GoLive, boolShouldPlay=True,env=self.env,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - Playback(boolShouldPlay=True) of Live entry " + str(entryGoLiveState.id) + " After updating GO LIVE viewMode = 1 - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))


                # RECORDED ENTRY - Playback verification of all entries
                self.logi.appendMsg("INFO - AFTER GO LIVE:Going to play RECORDED ENTRY for recordedEntryId =" + entryLiveStream.recordedEntryId + "  on the FLY(before mp4) - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.recorded_entrieslst, boolShouldPlay=True,env=self.env,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
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
                time.sleep(35)  # Wait for GO LIVE backend cache

                ##################################

                # Playback verification when viewMode=0 END LIVE of all entries - USER KS-->NO playback
                self.logi.appendMsg("INFO - boolShouldPlay=False viewMode=0 END LIVE for LIVE entry--> Going to verify NO playback on with USER KS " + str(self.entryId) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.entrieslst, boolShouldPlay=False,env=self.env,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - NO Playback(boolShouldPlay=False) and viewMode=0 END LIVE of LIVE entry " + str(self.entryId) + " USER KS live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                time.sleep(10)
                ####here
                # Playback verification when explicitLive=1 enable of all entries - Send admin KS->playback ok
                flashvars = "flashvars[ks]=" + ksAdmin
                self.logi.appendMsg("INFO - Going to play LIVE entry " + str(self.entryId) + " with ADMIN KS when viewMode=0 END LIVE - live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.entrieslst, boolShouldPlay=True,env=self.env,PlayerVersion=self.PlayerVersion,flashvars=flashvars,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - Playback of LIVE entry " + str(self.entryId) + " with ADMIN KS and viewMode=0 END LIVE -  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))

                #####################################*********** PLAY RECORDING after END LIVE
                # Waiting about 1 minutes after stopping streaming and then start to check the mp4 flavors upload status
                self.logi.appendMsg("INFO - Wait about 1 minutes after END LIVE and then start to check the mp4 flavors upload status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
                time.sleep(60)
                # Check mp4 flavors upload of recorded entry id
                self.logi.appendMsg("PASS - Going to WAIT For Flavors MP4 uploaded (until 20 minutes) on recordedEntryId = " + str(entryLiveStream.recordedEntryId))
                rc = self.liveObj.WaitForFlavorsMP4uploaded(self.client, FirstRecording_EntryID, recorded_entry,expectedFlavors_totalCount=4) # 4 expectedFlavors_totalCount is transcoding
                if rc == True:
                    self.logi.appendMsg("PASS - Recorded Entry mp4 flavors uploaded with status OK (ready-2/NA-4) .recordedEntryId" + entryLiveStream.recordedEntryId)
                    ################
                    ######## Get conversion version of VOD entry
                    filter = KalturaAssetFilter()
                    pager = KalturaFilterPager()
                    filter.entryIdEqual = FirstRecording_EntryID
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
                    self.logi.appendMsg("INFO - AFTER RESTART STREAMING:Verify VERSION - First_RecordedEntry_Version = " + str(First_RecordedEntry_Version) + ", recordedEntryId = " + entryLiveStream.recordedEntryId)
                else:
                    self.logi.appendMsg("FAIL - MP4 flavors did NOT uploaded to the recordedEntryId = " + entryLiveStream.recordedEntryId)
                    testStatus = False
                    return

                # Waiting about 1 minutes before playing the recorded entry after mp4 flavors uploaded with ready status
                self.logi.appendMsg("INFO - Wait about 1.5 minute before playing the recored entry after mp4 flavors uploaded with ready status recordedEntryId = " + str(entryLiveStream.recordedEntryId) + " is playable. ")
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

                # ##################################################### here!
                # RECORDED ENTRY after MP4 flavors are uploaded - Playback verification of all entries
                self.logi.appendMsg("INFO - Going to play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId) + "  - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                rc = self.liveObj.CheckPlaybackForAllDP(access_control_id_DP_list=self.DP_table, client=self.client,entryList=self.recorded_entrieslst, boolShouldPlay=True,env=self.env,PlayerVersion=self.PlayerVersion,sniffer_fitler=self.sniffer_fitler_After_Mp4flavorsUpload,Protocol="http",RefreshPlayer_Timeout=True,ServerURL=self.ServerURL)
                if not rc:
                    self.logi.appendMsg("FAIL -  CheckPlaybackDP")
                    testStatus = False
                    return
                self.logi.appendMsg("PASS - Play RECORDED ENTRY from " + self.sniffer_fitler_After_Mp4flavorsUpload + " after MP4 flavors uploaded " + str(entryLiveStream.recordedEntryId))

                ########### DURATION Compare for recording entry

                # Cal recording duration after mp4 flavors are uploaded
                self.logi.appendMsg("INFO - AFTER END LIVE:Going to verify DURATION of recorded entry.FirstRecording_EntryID = " + str(FirstRecording_EntryID))
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
           self.practitest.post(self.Practi_TestSet_ID, '961','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '961','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
        
        
            
    #===========================================================================
    #pytest.main(['test_961_LiveNG_CheckPlaybackForAllDP_TransDVRPreviewRecSESSION.py', '-s'])
    #===========================================================================
        
        
        