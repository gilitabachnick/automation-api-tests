'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_537_ExistLiveNG_SSHRTMPPassthrough_LiveDashboard.py
 
 @desc : this test check exist LiveNG entry Passthrough with RTMP streaming by SSH shellscript
 verification of Playback and liveDashboard Analyzer  

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
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import ClienSession
import reporter2
import Config
import Practitest
import tearDownclass
import MySelenium

import live
import LiveDashboard
import ast
import uiconf
import StaticMethods

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
            self.UserSecret = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'LIVENG_UserSecret')
            self.entryId = self.inifile.RetIniVal('LiveNG_Partner_' + self.PublisherID, 'ExistEntry')
        else:
            self.PublisherID = self.inifile.RetIniVal(self.section, 'LIVENG_PublisherID')  # QA 6611/ PROD 2930571
            self.UserSecret = self.inifile.RetIniVal(self.section, 'LIVENG_UserSecret')
            self.entryId = self.inifile.RetIniVal(self.section, 'ExistEntry')
        # ***** Cluster config
        self.Live_Cluster_Primary = None
        self.Live_Cluster_Backup = None
        self.Live_Change_Cluster = ast.literal_eval(self.inifile.RetIniVal(self.section, 'Live_Change_Cluster'))  # import ast # Change string(False/True) to BOOL
        if self.Live_Change_Cluster == True:
            self.Live_Cluster_Primary = self.inifile.RetIniVal(self.section, 'Live_Cluster_Primary')
            self.Live_Cluster_Backup = self.inifile.RetIniVal(self.section, 'Live_Cluster_Backup')

        self.cmdLine_parametners ="" #No parametners script    
        self.LiveDashboardURL = self.inifile.RetIniVal(self.section, 'LiveDashboardURL')
        self.sendto = "moran.cohen@kaltura.com;"        
        #***** SSH streaming server - liveng-core3-automation.kaltura.com
        self.remote_host = self.inifile.RetIniVal('NewLive', 'remote_host_LIVENGNew')
        self.remote_user = self.inifile.RetIniVal('NewLive', 'remote_user_LiveNGNew')
        self.remote_pass = ""
        self.filePath = "/home/kaltura/entries/LongCloDvRec.mp4"
        self.PlayerVersion = 3 # Player version 2 or 3
        self.NumOfEntries = 1
        self.MinToPlay = 10  # Minutes to play all entries
        self.seenAll_justOnce_flag = True  # if you want to play each entry just one time set True
        # SSH streaming computer - Ilia

      
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.logi = reporter2.Reporter2('test_537_ExistLiveNG_SSHRTMPPassthrough_LiveDashboard')
        self.logi.initMsg('test_537_ExistLiveNG_SSHRTMPPassthrough_LiveDashboard')
        
        # Live objects
        self.Wd = None
        self.LiveDashboard = None
        #self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, isProd, self.PublisherID, self.playerId)


    def test_537_ExistLiveNG_SSHRTMPPassthrough_LiveDashboard(self):
        global testStatus
        try:
            # create client session
            self.logi.appendMsg('INFO - start create session for BE_ServerURL=' + self.ServerURL + ' ,Partner: ' + self.PublisherID )
            mySess = ClienSession.clientSession(self.PublisherID, self.ServerURL, self.UserSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
            ###############
            # Create player of latest version -  Create 3 Player
            self.logi.appendMsg('INFO - Going to create latest V3')
            myplayer3 = uiconf.uiconf(self.client, 'livePlayer')
            self.player = myplayer3.addPlayer(None, self.env, False, False, "v3")  # Create latest player v3
            if isinstance(self.player, bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            # Create live object with current player
            self.logi.appendMsg('INFO - Created latest player V3 ' + str(self.player))
            self.testTeardownclass.addTearCommand(myplayer3, 'deletePlayer(' + str(self.player.id) + ')')
            # Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID,self.playerId)

            ###############
            # #****** ssh streaming entry
            self.logi.appendMsg("INFO - Going to stream EXIST entry by file ssh streamEntryByShellScript." + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                #Entryobj = Entry.Entry(self.client, 'AUTOMATION-Transcoding_SWITCHFLAVORS' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag","Admintag", "Moran category", 1, None, self.CloudtranscodeId)
                Entryobj =self.client.liveStream.get(self.entryId)
                #self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(Entryobj)
                self.testTeardownclass.addTearCommand(Entryobj, 'DeleteEntry(\'' + str(self.entryId) + '\')')
                streamUrl = self.client.liveStream.get(self.entryId)
                self.streamUrl.append(streamUrl)

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
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))

                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                # start ffmpeg by FoundByProcessId
                rc, ffmpegOutputString = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True)
                if rc == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
            #******* CHECK CPU usage of streaming machine
            #cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}'"
            self.logi.appendMsg("INFO - Going to VerifyCPU_UsageMachine.Details: ENTRY#entryId = " +self.entryId + ", host details=" + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , datetime = " + str(datetime.datetime.now()))
            cmdLine= "grep 'cpu' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage \"%\"}';date"
            rc,CPUOutput = self.liveObj.VerifyCPU_UsageMachine(self.remote_host, self.remote_user, self.remote_pass, cmdLine)

            if rc == True:
                self.logi.appendMsg("INFO - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , CPUOutput = " + str(CPUOutput))
            else:
                self.logi.appendMsg("FAIL - VerifyCPU_UsageMachine.Details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + str(cmdLine))
                testStatus = False
                return

            # Playback verification of all entries
            self.logi.appendMsg("INFO - Going to play " + str(self.entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=self.PlayerVersion,ServerURL=self.ServerURL)
                time.sleep(5)
                if not rc:
                    testStatus = False
                    return
                if self.seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(self.PlayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
            time.sleep(2)
            # kill ffmpeg ps
            self.logi.appendMsg("INFO - Going to end streams by killall cmd.Datetime = " + str(datetime.datetime.now()))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass,self.entryId, self.PublisherID,FoundByProcessId=ffmpegOutputString)
            if rc != False:
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
                testStatus = False
                return

            # **** Login LiveDashboard
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
            time.sleep(5)
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.LiveDashboard.invokeLiveDashboardLoginByKS(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL, self.PublisherID, self.ServerURL,self.UserSecret, self.env)
            if (rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
            time.sleep(5)
            # ****** Channels tab
            navigateTo = "Channels"
            rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
            if (rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                testStatus = False
                return
            self.logi.appendMsg("INFO - Waiting to status Stopped - 30 sec")
            time.sleep(10)  # wait for status to Stopped
            # Return row data from Channels
            rc, RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd, self.entryId, navigateTo,True)
            rowsNum = len(RowData)
            i = 1
            if (rc):
                self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd, self.entryId, self.PublisherID,RowData, navigateTo, "Stopped",env=self.env,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if (rc):
                    self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
            else:
                if self.isProd:
                    self.logi.appendMsg("WARNING -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                return
            # LiveDashboard - Alerts tab
            navigateTo = "Alerts"
            self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo= " + navigateTo)
            rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo)
            if (rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                testStatus = False
                return

            # Return row data from Alerts
            rc, RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd, self.entryId, navigateTo)
            rowsNum = len(RowData)
            if (rc):
                self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd, self.entryId, self.PublisherID,RowData, navigateTo, env=self.env)
                if (rc):
                    self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - Error on alerts tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
            else:
                self.logi.appendMsg("INFO -ReturnRowDataLiveDashboardByEntryId - NO Alert of the entry. entryId: " + self.entryId + ", ************ENTRY" + str(i))

            try:
                self.logi.appendMsg("INFO - Going to close browser")
                self.Wd.quit()
            except Exception as Exp:
                print (Exp)
                pass

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
        print('Tear down')
        try:
            print('Tear down - Wd.quit')
            self.Wd.quit()
        except Exception as Exp:
            print(Exp)
            pass
        print('#############')

        if testStatus == False:
            print("fail")
            self.practitest.post(self.Practi_TestSet_ID, '537', '1', self.logi.msg)
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            print("pass")
            self.practitest.post(self.Practi_TestSet_ID, '537', '0', self.logi.msg)
            self.logi.reportTest('pass', self.sendto)
            assert True


    #===========================================================================
    #pytest.main('test_537_ExistLiveNG_SSHRTMPPassthrough_LiveDashboard.py -s')
    #===========================================================================
        
        
        