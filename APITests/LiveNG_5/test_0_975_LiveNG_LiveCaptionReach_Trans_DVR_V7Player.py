'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_0_975_LiveNG_LiveCaptionReach_Trans_DVR_V7Player.py
 @desc : this test check E2E test of new LiveNG entries Transcoding with DVR + Live caption reach - including scroll to start point - REWIND ,Scroll to middle point - REWIND, BACK TO LIVE button
host access run ffmpeg cmd 
verification of create new entries ,API,start/check ps/stop streaming, Playback and liveDashboard Analyzer - alerts tab and channels

Test case:
Create live entry
Create schedulingEvent
Create Kaltura EntryVendorTask
Start streaming - until https://kaltura.atlassian.net/wiki/spaces/LiveTeam/pages/3778773251/Feature+Manager+-+technical+design  until manager feature is ready ->YOU MUST TO Start streaming after arriving to scheduleEvent.startTime AND  EntryVendorTaskId.status=3 processing
Verify Playback VTT + DVR different location
End streaming


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
import clsPlayerV2
import ast
import StaticMethods
### Jenkins params ###
#===============================================================================
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
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'LIVENG_UserSecret')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'LIVENG_PublisherID')  # QA 6611/ PROD 2930571
            self.UserSecret = self.inifile.RetIniVal(self.section, 'LIVENG_UserSecret')

        # LIVE CAPTION config profile
        self.reachProfileId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'reachProfileId')#QA 310 #PROD 206622
        self.catalogItemId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID,'catalogItemId')#QA 374 #PROD 14652

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
        self.PlayerVersion = 3 # player version 2 or 3

        # Live caption parameters
        self.SchedulerEvent_AddMinToStartTime = 5  # Time to add for startTime - minutes
        self.SchedulerEvent_sessionEndTimeOffset = 30  # Time to add for EndTime from startTime  - minutes
        self.sniffer_fitler = '.vtt'

        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project LIVENG
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_0_975_LiveNG_LiveCaptionReach_Trans_DVR_V7Player')
        self.logi.initMsg('test_0_975_LiveNG_LiveCaptionReach_Trans_DVR_V7Player')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)



    def test_0_975_LiveNG_LiveCaptionReach_Trans_DVR_V7Player(self):
        global testStatus
        try:
           # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

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
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-LiveEntry_LiveCaptionReach_DVR_PASSTHROUGH_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "adi category", 1,None,self.CloudtranscodeId)
                #Add stream entry    # recordStatus - send 0 for disable, 1 for append, 2 for per_session # dvrStatus - send 0 for disable, 1 for enable
                self.entry = Entryobj.AddEntryLiveStream(None, None, recordStatus=0, dvrStatus=1)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)


            time.sleep(5)
            # Create live caption
            self.logi.appendMsg('INFO - Going to create live caption')
            startTime = time.time() + (self.SchedulerEvent_AddMinToStartTime) * 60
            print("startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            endTime = startTime + self.SchedulerEvent_sessionEndTimeOffset * 60
            print("endTime = " + str(datetime.datetime.fromtimestamp(int(endTime)).strftime('%Y-%m-%d %H:%M:%S')))
            self.logi.appendMsg("INFO - Going to add KalturaLiveStreamScheduleEvent.Details: entryid=" + str(self.entry.id) + " , startTime INT= " + str(startTime) + " , endTime INT= " + str(endTime) + " , current time= " + str(datetime.datetime.now()))
            self.logi.appendMsg("INFO - startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')) + " , endTime = " + str(datetime.datetime.fromtimestamp(int(endTime)).strftime('%Y-%m-%d %H:%M:%S')))
            rc,EntryVendorTaskId=self.liveObj.LiveCaption_Create(client=self.client, startTime=startTime, endTime=endTime, entryId=self.entry.id,catalogItemId=self.catalogItemId, reachProfileId=self.reachProfileId)
            if rc !=True:
                self.logi.appendMsg('FAIL - LiveCaption_Create')
                testStatus = False
                return

            # Wait to scheduling event startTime
            self.logi.appendMsg("INFO - Wait for arriving to startTime = " + str(datetime.datetime.fromtimestamp(int(startTime)).strftime('%Y-%m-%d %H:%M:%S')))
            while startTime > time.time():  # Wait until SchedulerEvent.startTime
                time.sleep(5)
            # Verify VendorTask Status - 3 processing after arriving to startTime --> will update for sure just after arriving to startTime and start stream for 10sec
            rc = self.liveObj.Create_KalturaEntryVendorTask_VerifyStatus(client=self.client, id=EntryVendorTaskId,Expected_STATUS=3)  # entryVendorTask.status - first 1 scheduled , 3 processing
            if rc == False:
                self.logi.appendMsg("FAIL - After arriving to startTime:Create_KalturaEntryVendorTask_VerifyStatus.Details: entryid=" + self.entry.id + " , EntryVendorTaskId= " + str(EntryVendorTaskId) + " , catalogItemId= " + str(self.catalogItemId) + " , Expected_STATUS= 3 processing")
                testStatus = False
                return
            self.logi.appendMsg("PASS - Create_KalturaEntryVendorTask_VerifyStatus.Details: entryid=" + self.entry.id + " , EntryVendorTaskId= " + str(EntryVendorTaskId) + " , catalogItemId= " + str(self.catalogItemId) + " , Expected_STATUS= 3 processing")
            time.sleep(2)

            # Get entryId and primaryBroadcastingUrl from live entries
            for i in range(0, self.NumOfEntries):
                time.sleep(2)
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
                    self.logi.appendMsg("FAIL - Start_StreamEntryByffmpegCmd.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
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

                # ****** Livedashboard - Channels tab
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None, logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi, self.LiveDashboardURL, self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env, Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False
            # Verify DVR
            rc= self.liveObj.DVR_Verification(liveObj=self.liveObj, entryList=self.entrieslst, entryId=self.entryId, MinToPlay=self.MinToPlay,boolShouldPlay=True,PlayerVersion=self.PlayerVersion,ClosedCaption=True,sniffer_fitler=self.sniffer_fitler,Protocol="http",MatchValue=True,QRCODE=False,ServerURL=self.ServerURL)
            if rc == True:
                self.logi.appendMsg("PASS  - DVR_Verification. entryId = " + str(self.entryId))
            else:
                self.logi.appendMsg("FAIL  - DVR_Verification. entryId = " + str(self.entryId))
                testStatus = False

            #Stop streaming - kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                testStatus = False
                return


        except Exception as e:
            print(e)
            testStatus = False
            pass


    #===========================================================================
    # TEARDOWN
    #===========================================================================

    def teardown_class(self):

        global testStatus

        print ('#############')
        print (' Tear down - Wd.quit')

        try:
            self.PlayBrowserDriver.quit()
        except Exception as Exp:
            print (Exp)
            pass

        try:
            self.Wd.quit()
        except Exception as Exp:
            print (Exp)
            pass
        try:
            print ('Tear down - testTeardownclass')
            time.sleep(20)
            self.testTeardownclass.exeTear()  # Delete entries
            print ('#############')
        except Exception as Exp:
            print (Exp)
            pass

        if testStatus == False:
            print ("fail")
            self.practitest.post(self.Practi_TestSet_ID, '975', '1', self.logi.msg)
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            print ("pass")
            self.practitest.post(self.Practi_TestSet_ID, '975', '0', self.logi.msg)
            self.logi.reportTest('pass', self.sendto)
            assert True



    #===========================================================================
    #pytest.main(['test_0_975_LiveNG_LiveCaptionReach_Trans_DVR_V7Player.py','-s'])
    #===========================================================================
        
        
        