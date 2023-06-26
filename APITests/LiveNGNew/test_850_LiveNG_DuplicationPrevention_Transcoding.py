'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@author: moran.cohen

@test_name: test_850_LiveNG_DuplicationPrevention_Transcoding.py

 @desc : This test check E2E test of new LiveNG entries cloud transcording by creating New Player v2 + v3
 Player v7 check by sniffer_filter_per_flavor_list - each flavor is played with sniffer verification.
 Start RTMP streaming by new logic function - host access run ffmpeg cmd. 
 verification of create new entries ,API,start/check ps/stop streaming, Playback with the created player v2+v3 and liveDashboard Analyzer - alerts tab and channels
 Basic case - Stream the same stream name twice.
 Verify that just on ProcessId can be streamed  - Added ProcessIds platform.
 Search for DuplicateInputAlert on liveDashboard.
 Verify that live entry is playback ok with one ProcessId.

 FULL TEST CASES:
 https://kaltura.atlassian.net/browse/LIV-808
    Progression tests:
    1.the basic - stream the same stream name twice. also test the format of stream name without channel id, like once stream to "/0_i9fybfi3_1" and then to "/1" (try the possible combinations).
    2.stream the same stream name but to different clusters - validate that one of them will be rejected. (LIV-570)
    Regression tests:
    1.stream -> stop -> immediately stream again -> validate that the fast re-stream won't be rejected (maybe can be easier with OBS as it only click on buttons to stop and stream again).
    2.stream primary and backup and validate none of them will be rejected.
    3.stream to different stream names and validate none of them will be rejected (like multiflavor / multiaudio).
    *Rejected = the ffmpeg / obs should be disconnect after 30s-1m.
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
import DOM

import live
import LiveDashboard
import Transcoding
import QrcodeReader
import ast
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
        self.flavorList = "Auto;480p;360p"  # option on player v7 of source selector
        #self.sniffer_filter_per_flavor_list = '-s35.ts;-s35.ts;-s33.ts'  # ts search for each flavor on flavorList
        self.sniffer_filter_per_flavor_list = '-s35;-s35;-s33'  #ts search for each flavor on flavorList - Delivery profile 1033:Live packager hls -redirect

        self.NumOfEntries = 1
        self.MinToPlay = 10 # Minutes to play all entries
        self.seenAll_justOnce_flag=True  # if you want to play each entry just one time set True    
        #self.PlayerVersion = 2 # Player version 2 or 3
        #self.AllPlayers = True # If True running the two version in a loop/ If False running just self.PlayerVersion
          
        #=======================================================================
        self.testTeardownclass = tearDownclass.teardownclass()
        #=======================================================================
        self.practitest = Practitest.practitest('18742')#set project BE API
        self.Wdobj = MySelenium.seleniumWebDrive()
        self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
        self.logi = reporter2.Reporter2('test_850_LiveNG_DuplicationPrevention_Transcoding')
        self.logi.initMsg('test_850_LiveNG_DuplicationPrevention_Transcoding')
        self.LiveDashboard = LiveDashboard.LiveDashboard(self.Wd, self.logi)
        self.QrCode = QrcodeReader.QrCodeReader(wbDriver=self.Wd, logobj=self.logi)

    def test_850_LiveNG_DuplicationPrevention_Transcoding(self):
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
            self.logi.appendMsg('INFO - Going to create latest V2')
            myplayer = uiconf.uiconf(self.client, 'livePlayer')
            self.player = myplayer.addPlayer(None,self.env,False, False) # Create latest player v2
            if isinstance(self.player,bool):
                testStatus = False
                return
            else:
                self.playerId = self.player.id
            self.logi.appendMsg('INFO - Created latest player V2 ' + str(self.playerId))       
            self.testTeardownclass.addTearCommand(myplayer,'deletePlayer(' + str(self.player.id) + ')')    
            #Create live object with current player
            self.liveObj = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId)
                     
            self.logi.appendMsg('INFO - Going to create latest V3')
            myplayer3 = uiconf.uiconf(self.client, 'livePlayer')
            self.player_v3 = myplayer3.addPlayer(None,self.env,False, False,"v3") # Create latest player v3
            if isinstance(self.player_v3,bool):
                testStatus = False
                return
            else:
                self.playerId_v3 = self.player_v3.id
            #Create live object with current player_v3
            self.logi.appendMsg('INFO - Created latest player V3 ' + str(self.player_v3))       
            self.testTeardownclass.addTearCommand(myplayer3,'deletePlayer(' + str(self.player_v3.id) + ')')
            #Create live object with current player
            self.liveObj_v3 = live.Livecls(None, self.logi, self.testTeardownclass, self.isProd, self.PublisherID, self.playerId_v3)
            
            self.entrieslst = []
            self.streamUrl = []
            # Create self.NumOfEntries live entries
            for i in range(0, self.NumOfEntries):
                Entryobj = Entry.Entry(self.client, 'AUTOMATION-DuplicationPrevention_Transcoding' + str(i) + '_' + str(datetime.datetime.now()), "Live Automation test " + str(self.NumOfEntries) + " Entries", "Live tag", "Admintag", "Moran category", 1,None,self.CloudtranscodeId)
                self.entry = Entryobj.AddEntryLiveStream(None, None, 0, 0)
                self.entrieslst.append(self.entry)
                self.testTeardownclass.addTearCommand(Entryobj,'DeleteEntry(\'' + str(self.entry.id) + '\')')
                streamUrl = self.client.liveStream.get(self.entry.id)
                self.streamUrl.append(streamUrl)

            #**** Login LiveDashboard
            self.logi.appendMsg("INFO - Going to perform invokeLiveDashboardLogin.")
            rc = self.LiveDashboard.invokeLiveDashboardLoginByKS(self.Wd, self.Wdobj, self.logi, self.LiveDashboardURL,self.PublisherID, self.ServerURL, self.UserSecret,self.env)
            if(rc):
                self.logi.appendMsg("PASS - LiveDashboard login.")
            else:       
                self.logi.appendMsg("FAIL - LiveDashboard login. LiveDashboardURL: " + self.LiveDashboardURL)
                testStatus = False
                return
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
                self.logi.appendMsg("INFO - ************** Going to ssh Start_StreamEntryByffmpegCmd - Only primaryBroadcastingUrl.********** ENTRY#" + str(i) + " , Datetime = " + str(datetime.datetime.now()) + " , "  + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId) + " , primaryBroadcastingUrl = " + str(Current_primaryBroadcastingUrl))
                if self.IsSRT == True:
                    ffmpegCmdLine,Current_primaryBroadcastingUrl = self.liveObj.ffmpegCmdString_SRT(self.filePath, str(Current_primaryBroadcastingUrl),primarySrtStreamId)
                else:
                    ffmpegCmdLine = self.liveObj.ffmpegCmdString(self.filePath, str(Current_primaryBroadcastingUrl),self.streamUrl[i].streamName)
                #start ffmpeg by FoundByProcessId
                rc1,ffmpegOutputString1 = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, ffmpegCmdLine, self.entryId,self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True,MultiArrProcessIds=True)
                if rc1 == False:
                    self.logi.appendMsg("FAIL - Start_StreamEntryByShellScript. Start_StreamEntryByShellScript details: " + self.remote_host + " , " + self.remote_user + " , " + self.remote_pass + " , " + self.filePath + " ," + self.entryId + " , " + self.PublisherID + " , " + str(self.playerId))
                    testStatus = False
                    return
                time.sleep(5)
                rc2, ffmpegOutputString2 = self.liveObj.Start_StreamEntryByffmpegCmd(self.remote_host, self.remote_user,self.remote_pass, ffmpegCmdLine,self.entryId, self.PublisherID,env=self.env,BroadcastingUrl=Current_primaryBroadcastingUrl,FoundByProcessId=True,timout_SearchPsAux=60,MultiArrProcessIds=True)
                if len(ffmpegOutputString2)>1:
                    self.logi.appendMsg("FAIL - Duplication Prevention.There are multi streams with same stream name. ffmpegCmdLine: " + ffmpegCmdLine)
                    for i in range(0, len(ffmpegOutputString2)):
                        self.logi.appendMsg("FAIL - Duplication Prevention. ProcessId: " + str(ffmpegOutputString2[i]))
                    testStatus = False
                    return
                if rc2 == False:
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
                time.sleep(5)
                if self.env == "prod":
                    time.sleep(10)
                #############Waiting for alerts
                locator = DOM.LIVE_DASHBOARD_ROWS
                timeout = 10
                if self.env == "prod":
                    timeout = 50
                element = self.LiveDashboard.wait_element(self.Wd, locator=locator, timeout=timeout)
                if element == False:
                    self.logi.appendMsg("INFO: Element   was NOT found; Locator by: " + locator)
                    return False
                 ############
                 # Return row data from Alerts
                rc,RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd,self.entryId,navigateTo)
                rowsNum=len(RowData)
                if(rc):
                    self.logi.appendMsg("INFO - Going to verify the Alerts of return RowData:")
                    rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd,self.entryId,self.PublisherID,RowData,navigateTo,env=self.env)
                    if(rc):
                        #self.logi.appendMsg("PASS -VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are NO alerts - Missing DuplicateInputAlert. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                        testStatus = False
                    else:
                        CntError=0
                        flag_DuplicateInputAlert=False
                        for j in range(0, len(RowData)):
                            if RowData[j].find("DuplicateInputAlert") > 0:
                                flag_DuplicateInputAlert=True
                            if RowData[j].find("Error") > 0:
                                CntError=+1
                        if CntError > 1 or flag_DuplicateInputAlert != True:#Many Errors - Not just DuplicateInputAlert
                           self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are Error alerts, but Missing DuplicateInputAlert. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                           testStatus = False
                        elif CntError < 1:#No alerts
                            self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are NO alerts - Missing DuplicateInputAlert. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                            testStatus = False
                        elif CntError >= 1 or flag_DuplicateInputAlert == True:
                            if CntError == 1:
                                self.logi.appendMsg("PASS -ReturnRowDataLiveDashboardByEntryId - DuplicateInputAlert appears. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                            else:
                                self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - There are too many error alerts on type DuplicateInputAlert. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                                testStatus = False
                        else:
                            self.logi.appendMsg("FAIL -VerifyReturnRowDataLiveDashboard - DuplicateInputAlert verification. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                            testStatus = False

                else:       
                    self.logi.appendMsg("FAIL -ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    testStatus = False
                    return
           # ****** Livedashboard - Channels tab
            navigateTo = "Channels"
            self.logi.appendMsg("INFO - Going to perform navigateToLiveDashboardTabs.navigateTo = " + navigateTo)
            rc = self.LiveDashboard.navigateToLiveDashboardTabs(self.Wd, navigateTo, env=self.env)
            if (rc):
                self.logi.appendMsg("PASS - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
            else:
                self.logi.appendMsg("FAIL - navigateToLiveDashboardTabs. navigateTo: " + navigateTo)
                testStatus = False
                return
            '''time.sleep(5)
            if self.env == "prod":
                time.sleep(15)'''
            #############Waiting for channels
            locator = DOM.LIVE_DASHBOARD_ROWS
            timeout = 10
            if self.env == "prod":
                timeout = 50
            element = self.LiveDashboard.wait_element(self.Wd, locator=locator, timeout=timeout)
            if element == False:
                self.logi.appendMsg("INFO: Element  was NOT found; Locator by: " + locator)
                return False
            ##########
            # Return row data from Channels
            rc, RowData = self.LiveDashboard.ReturnRowDataLiveDashboardByEntryId(self.Wd, self.entryId, navigateTo)
            rowsNum = len(RowData)
            if (rc):
                self.logi.appendMsg("INFO - Going to verify the Channels of return RowData:")
                rc = self.LiveDashboard.VerifyReturnRowDataLiveDashboard(self.Wd, self.entryId, self.PublisherID, RowData,navigateTo, env=self.env,Live_Cluster_Primary=self.Live_Cluster_Primary)
                if (rc):
                    self.logi.appendMsg("PASS -Channels VerifyReturnRowDataLiveDashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                else:
                    self.logi.appendMsg("FAIL -Channels VerifyReturnRowDataLiveDashboard - Error on Channels tab livedashboard. entryId: " + self.entryId + ", ************ENTRY" + str(i))
                    if self.env == 'testing':
                        testStatus = False
            else:
                self.logi.appendMsg("FAIL -Channels ReturnRowDataLiveDashboardByEntryId. entryId: " + self.entryId + ", ************ENTRY" + str(i))
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
        
         
            time.sleep(2)
            if self.env == 'prod':
                time.sleep(15)
            for CurrentplayerVersion in range(2,4):
                #Playback verification of all entries with all player version = 2 and 3
                self.logi.appendMsg("INFO - ************** Going to play live entries on PlayerVersion= "+ str(CurrentplayerVersion) +"  on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , Start time = " + str(datetime.datetime.now()))
                limitTimeout = datetime.datetime.now() + datetime.timedelta(0, self.MinToPlay*60)
                seenAll = False
                while datetime.datetime.now() <= limitTimeout and seenAll==False:   
                        if CurrentplayerVersion == 3:
                            # Player v7 check by sniffer_filter_per_flavor_list
                            rc = self.liveObj_v3.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion,SourceSelector=True,flavorList=self.flavorList,sniffer_filter_per_flavor_list=self.sniffer_filter_per_flavor_list,ServerURL=self.ServerURL)
                        else:
                            rc = self.liveObj.verifyAllEntriesPlayOrNoBbyQrcode(self.entrieslst, True,PlayerVersion=CurrentplayerVersion,ServerURL=self.ServerURL)
                        time.sleep(5)
                        if not rc:
                            testStatus = False
                            return
                        if self.seenAll_justOnce_flag ==True:
                            seenAll = True
    
                self.logi.appendMsg("PASS - Playback of PlayerVersion= " + str(CurrentplayerVersion) + " live entries on preview&embed page during - MinToPlay=" + str(self.MinToPlay) + " , End time = " + str(datetime.datetime.now()))
                      
            # kill ffmpeg ps by FoundByProcessId
            self.logi.appendMsg("INFO - Going to end streams by FoundByProcessId cmd.Datetime = " + str(datetime.datetime.now()) + " , FoundByProcessId = " + str(ffmpegOutputString1[0]))
            rc = self.liveObj.End_StreamEntryByffmpegCmd(self.remote_host, self.remote_user, self.remote_pass, self.entryId,self.PublisherID,FoundByProcessId=ffmpegOutputString1[0])
            if rc != False:            
                self.logi.appendMsg("PASS - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript.  streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " , entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId= " + str(self.playerId))
            else:
                self.logi.appendMsg("FAIL - streamEntryByShellScript and VerifyResultFromStreamEntryByShellScript. streamEntryByShellScript: remote_host= " + self.remote_host + " , remote_user= " + self.remote_user + " , remote_pass= " + self.remote_pass + " , filePath= " + self.filePath + " ,entryId= " + self.entryId + " , entryId= " + self.PublisherID + " , playerId = " + str(self.playerId))
                testStatus = False
                return    
                        
            
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
            print('#############')
        except Exception as Exp:
           print(Exp)
           pass
        
        if testStatus == False:
           print("fail")
           self.practitest.post(self.Practi_TestSet_ID, '850','1', self.logi.msg)
           self.logi.reportTest('fail',self.sendto)        
           assert False
        else:
           print("pass")
           self.practitest.post(self.Practi_TestSet_ID, '850','0', self.logi.msg)
           self.logi.reportTest('pass',self.sendto)
           assert True        
    
            
    #===========================================================================
    #pytest.main('test_850_LiveNG_DuplicationPrevention_Transcoding.py -s')
    #===========================================================================
        
        
        