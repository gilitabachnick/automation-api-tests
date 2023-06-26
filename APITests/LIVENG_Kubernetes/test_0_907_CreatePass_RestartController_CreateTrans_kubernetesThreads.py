'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen
https://github.com/kaltura/live/wiki/How-to#non-interactive-mode
@test_name: test_0_907_CreatePass_RestartController_CreateTrans_kubernetesThreads.py
 @desc : this test check E2E test of new LiveNG entries passthrough - host access run ffmpeg cmd
 verification of create new entries ,API,start/check ps/stop streaming, QRCODE Playback and liveDashboard Analyzer - alerts tab and channels
 Running multi threading LIVE entry playback by QRCODE
 Check kubernetes only on QA env:
     kubectl kubectl delete pod --selector=component=controller
     Verify LIVE entry playback by QRCODE during threading
     Verify that live dashboard error should not presented for the passthrough entry
     Verify Create New LIVE entry transcoding + playback by QRCODE

Restart controller --> kubectl delete pod --selector=component=controller
    Verify that the playback of the live entry is ok.
    Verify that it should not influence any of running streams.
    Cause failure to who trying to connect new stream at the moment that the controller is down
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
import Kubernetes
import LiveDashboard
import Transcoding
import QrcodeReader
from KalturaClient.Plugins.Core import *
import re
import threading
import queue
import ast
import Kubernetes_k8sConnect
import StaticMethods



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
        self.Live_Cluster_Primary = '1-a'
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')
        self.sendto = "moran.cohen@kaltura.com;"
        # ***** SSH streaming server - AWS LINUX
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENG_Kubernetes')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LIVENG_Kubernetes')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        self.controller_selector = "component=controller"

        self.NumOfEntries = 1
        self.MinToPlay = 8 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True
        self.PlayerVersion = 3 # player version 2 or 3
        self.MinToPlayEntry = 3 # Minutes to play the live entry
        self.QrCodecheckProgress=4
        #self.sniffer_filter_per_flavor_list = '.ts;.m3u8'
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        #self.Wdobj = MySelenium.seleniumWebDrive()
        #self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_0_907_CreatePass_RestartController_CreateTrans_kubernetesThreads')
        self.logi.initMsg('test_0_907_CreatePass_RestartController_CreateTrans_kubernetesThreads')
        #self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        #self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)
        #self.KubernetesObj = Kubernetes.Kubernetes_Live(None, self.logi,isProd, self.PublisherID)
        self.KubernetesObj = Kubernetes_k8sConnect.Kubernetes_Live(None, self.logi, self.isProd, self.PublisherID)

    def test_0_907_CreatePass_RestartController_CreateTrans_kubernetesThreads(self):
        global testStatus
        try:
            if self.env =='prod':
                self.logi.appendMsg('INFO - This tests is NOT running on PRODUCTION - ONLY QA env')
                return
            #create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)

            ''' RETRIEVE TRANSCODING ID AND CREATE PASSTHROUGH IF NOT EXIST'''
            self.logi.appendMsg('INFO - Going to create(if not exist) conversion profile = Passthrough')
            Transobj = Transcoding.Transcoding(self.client, 'Passthrough')
            self.passtrhroughId = Transobj.CreateConversionProfileFlavors(self.client, 'Passthrough', '32,36,37')
            if isinstance(self.passtrhroughId, bool):
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
            self.logi.appendMsg('INFO - Created latest V' + str(self.PlayerVersion) + ' player.self.playerId = ' + str(self.playerId))
            self.testTeardownclass.addTearCommand(myplayer, 'deletePlayer(' + str(self.player.id) + ')')

            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)

            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-ControllerRestart_Passthrough_' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.passtrhroughId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
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
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd from Primary only.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + Current_primaryBroadcastingUrl)
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                start_streaming = datetime.datetime.now().timestamp()
                rc,ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + str(Current_primaryBroadcastingUrl))
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
                time.sleep(5)  # added
                self.logi.appendMsg("INFO - Going to get All controllers")
                arrControllers = self.KubernetesObj.listPod(self.Live_Cluster_Primary, self.controller_selector)
                if arrControllers == False:
                    self.logi.appendMsg("FAIL - Kubernetes - listPod .Get listPod by controller_selector = " + self.controller_selector)
                    testStatus = False
                    return
                self.logi.appendMsg("INFO - Kubernetes - Return  controllers listPod:")
                for j in range(0, len(arrControllers)):
                    currentController = arrControllers[j]
                    self.logi.appendMsg("INFO - Kubernetes - listPod .currentTranscoder = " + currentController)

                # Running as thread function Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode
                self.logi.appendMsg("INFO - Main : Before creating thread - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                que = queue.Queue()
                x = threading.Thread(target=lambda q, arg1, arg2, arg3, arg4, arg5, arg6, arg7: q.put(self.KubernetesObj.Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(arg1, arg2, arg3, arg4, arg5, arg6, arg7)),args=(que, self.liveObj, self.entrieslst, True, self.MinToPlayEntry, self.PlayerVersion, self.QrCodecheckProgress,self.ServerURL))
                self.logi.appendMsg("INFO - Main : Before running thread - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode -  " + str(datetime.datetime.now()))
                x.start()
                self.logi.appendMsg("INFO - Main : Wait for the thread to start playing the entry - entryId = " + str(self.entryId) + " , CurrentTime = " + str(datetime.datetime.now()))
                #x.join()
                time.sleep(30) #Wait for the thread to start playing the entry
                time.sleep(5)  # added
                self.logi.appendMsg("INFO - ********* Going to RESTART All Controllers:" + ", datetime = " + str(datetime.datetime.now()))
                for j in range(0, len(arrControllers)):
                    currentController = arrControllers[j]  # [0]
                    self.logi.appendMsg("INFO - ####### Going to RESTART Controller-" + str(j) + " :currentController=" + str(currentController) + ", datetime = " + str(datetime.datetime.now()))
                    rc = self.KubernetesObj.deletePod(cluster_id=self.Live_Cluster_Primary, pod_name=currentController)
                    if rc == False:
                        self.logi.appendMsg("FAIL - Start_KubernetesByCmd-  RESTART Controller is failed. currentController = " + str(currentController) + ", datetime = " + str(datetime.datetime.now()))
                        testStatus = False
                        return
                    else:
                        self.logi.appendMsg("PASS - Start_KubernetesByCmd - RESTART Controller is done.currentController = " + str(currentController) + ", datetime = " + str(datetime.datetime.now()))


                self.logi.appendMsg("INFO  - Main: Wait for the thread to finish - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                x.join()
                rc = que.get()
                if rc == True:
                    self.logi.appendMsg("PASS  - Main: thread return result Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                else:
                    self.logi.appendMsg("FAIL -  Main: thread Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode")
                    testStatus = False
                    #return
                self.logi.appendMsg("INFO  - Going to verify live dashboard")
                self.LiveDashboard = LiveDashboard.LiveDashboard(Wd=None,logi=self.logi)
                rc = self.LiveDashboard.Verify_LiveDashboard(self.logi,self.LiveDashboardURL,self.entryId,self.PublisherID,self.ServerURL,self.UserSecret,self.env,Flag_Transcoding=False,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if rc == True:
                    self.logi.appendMsg("PASS  - Verify_LiveDashboard")
                else:
                    self.logi.appendMsg("FAIL -  Verify_LiveDashboard")
                    testStatus = False

                # kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
                if rc != False:
                    self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                else:
                    self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                time.sleep(5)
                ''' RETRIEVE TRANSCODING ID AND CREATE transcoding HD IF NOT EXIST'''
                Transobj = Transcoding.Transcoding(self.client, 'AUTO Transcoding HD')
                self.CloudtranscodeId = Transobj.getTranscodingProfileIDByName('AUTO Transcoding HD')
                if self.CloudtranscodeId == None:
                    # self.CloudtranscodeId = Transobj.addTranscodingProfile(1,'32,42,43')
                    self.CloudtranscodeId = Transobj.addTranscodingProfile(1, '32,33,34,35,42,43')
                    if isinstance(self.CloudtranscodeId, bool):
                        testStatus = False
                        return

                self.entrieslst = []
                self.streamUrl = []
                # Create self.NumOfEntries live entries
                for i in range(0, self.NumOfEntries):
                    Entryobj = Entry.Entry(self.client,'AUTOMATION-ControllerRestart_TranscodingHD_' + str(i) + '_' + str(datetime.datetime.now()),"Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.CloudtranscodeId)
                    self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                    self.entrieslst.append(self.entry)
                    self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entry.id) + '\')')
                    streamUrl = self.client.liveStream.get(self.entry.id)
                    self.streamUrl.append(streamUrl)
                time.sleep(5)
                # Get entryId and primaryBroadcastingUrl from live entries
                for i in range(0, self.NumOfEntries):
                    self.entryId = str(self.entrieslst[i].id)
                    Current_primaryBroadcastingUrl = self.streamUrl[i].primaryBroadcastingUrl
                    if self.Live_Change_Cluster == True and self.env == 'testing':
                        Current_primaryBroadcastingUrl = Current_primaryBroadcastingUrl.replace("1-a",self.Live_Cluster_Primary)
                    self.logi.appendMsg("INFO - ************** Going to RESTART ssh Start_StreamEntryByffmpegCmd after restart all transcoders.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId)+ " , " + Current_primaryBroadcastingUrl)
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath,str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                    start_streaming = datetime.datetime.now().timestamp()
                    rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host,self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                    if rc == False:
                        self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript secondaryBroadcastingUrl. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , " + str(Current_primaryBroadcastingUrl))
                        testStatus = False
                        return
                time.sleep(10)
                self.MinToPlayEntry = 1
                rc=self.KubernetesObj.Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(self.liveObj, self.entrieslst, True, self.MinToPlayEntry, self.PlayerVersion, self.QrCodecheckProgress,self.ServerURL)
                if rc == True:
                    self.logi.appendMsg("PASS  - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode- Playback is OK for New transcording entry after restart all transcoders.entryId " + str(self.entryId ))
                else:
                    self.logi.appendMsg("FAIL  - Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode- Playback is FAILED for New transcording entry after restart all transcoders.entryId " + str(self.entryId ))
                    testStatus = False
                    # return

                # kill ffmpeg ps
                self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()))
                rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
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
           self.practitest.post(self.Practi_TestSet_ID, '907','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '907','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True


    #===========================================================================
    #pytest.main('test_0_907_CreatePass_RestartController_CreateTrans_kubernetesThreads.py -s')
    #===========================================================================
        
        
        