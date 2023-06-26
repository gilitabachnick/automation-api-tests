'''
@author: Moran.Cohen
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
@test_name: test_1887_MR_End2End
 
 @desc : This test check mediaRepurposing E2E test - Deletion of entry, testing.qa - real deletion , Production - dry run  
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
'''


import datetime
import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)

import uploadFuncs
import reporter2

import autoitWebDriver
import MediaRepurposingFuncs

import DOM
import ClienSession
import Config
import Practitest
import Entry
import tearDownclass
import MySelenium
import KmcBasicFuncs

### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()

if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

#Success to create new MR profile
CreateMRStatus = False


class TestClass:
    
    #===========================================================================
    # SETUP
    #===========================================================================
    def setup_class(self):
        try:       
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
                self.Partner_ID = inifile.RetIniVal(section, 'partnerElla')
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretMR')
                self.MediaRepurposingTemplateType = "Delete"
               
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                self.Partner_ID = inifile.RetIniVal(section, 'partnerId4770') 
                self.AdminSecret     = inifile.RetIniVal(section, 'AdminSecretMR')
                self.MediaRepurposingTemplateType = "Delete with Notification"

            # Admin Console
            self.user = inifile.RetIniVal(section, 'AdminConsoleUser')
            self.pwd = inifile.RetIniVal(section, 'AdminConsolePwd')
            self.transProfileID = inifile.RetIniVal(section, 'MRTransProfile')
            self.url    = inifile.RetIniVal(section,'admin_url') 
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.remote_host = inifile.RetIniVal('admin_console_access', 'host')
            self.remote_user = inifile.RetIniVal('admin_console_access', 'user')
            self.remote_pass = inifile.RetIniVal('admin_console_access', 'pass')
            self.admin_user = inifile.RetIniVal('admin_console_access', 'session_user')
            self.env = inifile.RetIniVal('admin_console_access', 'environment')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()       
            self.practitest = Practitest.practitest()
            self.logi = reporter2.Reporter2('test_1887_MR_End2End')
            self.practitest = Practitest.practitest('4586')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.MediaRepurposingFuncs = MediaRepurposingFuncs.MediaRepurposingFuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.MediaRepurposingProfileName = str(self.Partner_ID) + "_create_from_template" +  str(datetime.datetime.now())
            # File for entry
            pth                 = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
            self.filepth    = r'\QRcodeVideo.mp4'
            self.FileName       = "QRcodeVideo.mp4"        
            self.FileName = os.path.join(pth, self.FileName).replace("\\", "/")
            self.entryName  = 'QRcodeVideo'
            self.testTeardownclass = tearDownclass.teardownclass()
                  
            #Session
            self.ServerURL      = inifile.RetIniVal(section,'ServerURL')         
            
            if self.Wdobj.RUN_REMOTE:
                self.autoitwebdriver = autoitWebDriver.autoitWebDrive() 
                self.AWD =  self.autoitwebdriver.retautoWebDriver()
            else:
                self.filepth = self.filepth[1:]         
        except Exception as Exp:
            print(Exp) 
            pass   
        
    def test_1887_MR_End2End(self):
        
        global testStatus
        global CreateMRStatus
        self.logi.initMsg('test_1887_MR_End2End')

        try:
            #############################################################UPLOAD ENTRY - API ##########################################
            self.logi.appendMsg('INFO - Start create session for partenr: ' + self.Partner_ID)
            mySess = ClienSession.clientSession(self.Partner_ID,self.ServerURL,self.AdminSecret)
            self.client = mySess.OpenSession()
            time.sleep(2)
            # Upload entry with the above transcoding profile
            self.logi.appendMsg('INFO - Going to upload new entry with the transcoding profile id: ' +  str(self.transProfileID))
            myentry = Entry.Entry(self.client,"Entry MR" + str(datetime.datetime.now()) , "MR Automation test", "MR tag", "MRAdmintag", "MR category", 1, open(self.FileName,'rb'), self.transProfileID)
            entry = myentry.AddNewEntryWithFile()
            if isinstance(entry,bool):
                self.logi.appendMsg('FAIL - Entry was not uploaded after 5 minutes')
                testStatus = False
                return
            elif isinstance(entry, str):
                self.logi.appendMsg('FAIL - Entry got error when trying to upload it')
                testStatus = False
                return
            else:
                self.logi.appendMsg('INFO - Finished upload file to new entry id :' + str(entry.id))

            self.testTeardownclass.addTearCommand(myentry,'DeleteEntry(\'' + str(entry.id) + '\')')


            try:
                self.logi.appendMsg("INFO - Going to login to Admin Console. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                if "nv" not in self.url:  # Bypass NVD console user/pass login
                    ks = self.BasicFuncs.generateAdminConsoleKs(self.remote_host, self.remote_user, self.remote_pass,
                                                                self.admin_user, self.env)
                else:
                    ks = False
                rc = self.BasicFuncs.invokeConsoleLogin(self.Wd,self.Wdobj,self.logi,self.url,self.user,self.pwd,ks)
                if(rc):
                    self.logi.appendMsg("PASS - Admin Console login.")
                else:
                    self.logi.appendMsg("FAIL - Admin Console login. Login details: userName - " + self.user + " , PWD - " + self.pwd)
                    testStatus = False
                    return
            except:
                pass


            self.Wd.maximize_window()

            self.logi.appendMsg("INFO - Going to Navigate to MediaRepurposing screen. Partner_ID: " + self.Partner_ID)
            rc= self.MediaRepurposingFuncs.AdminConsole_Navigate_MediaRepurposing(self.Partner_ID)
            if not rc:
                self.logi.appendMsg("FAIL - Navigate to MR profile screen, Partner_ID: " + self.Partner_ID)
                testStatus = False
                return

            self.logi.appendMsg("INFO - Going to create MR profile, MR name: " + self.MediaRepurposingProfileName)

            rc = self.MediaRepurposingFuncs.MediaRepurposingProfileCreate(self.MediaRepurposingProfileName,self.MediaRepurposingTemplateType,str(entry.id))
            if not rc:
                self.logi.appendMsg("FAIL - Create MR profile, MR name: " + self.MediaRepurposingProfileName)
                testStatus = False
                return
            else:
                CreateMRStatus = True
                self.logi.appendMsg("PASS - Create MR profile, MR name: " + self.MediaRepurposingProfileName)

            time.sleep(2)
            self.logi.appendMsg("INFO - Going to press on the search button")
            self.Wd.find_element_by_xpath(DOM.MR_SEARCH_BTN).click()
            time.sleep(2)
            self.logi.appendMsg("INFO - Going to Enable MR profile, MR name: " + self.MediaRepurposingProfileName)
            rc = self.MediaRepurposingFuncs.MediaRepurposingProfileAction(self.MediaRepurposingProfileName,"enable")
            if not rc:
                self.logi.appendMsg("FAIL - Delete MR profile, MR name: " + self.MediaRepurposingProfileName)
                testStatus = False
                return

            # Waiting the MR profile to delete entry
            if isProd == False:############## Testing.qa - Run real MR
                self.logi.appendMsg('***********INFO - Going to verify that entry is deleted by MR profile. entryId :' + str(entry.id))
                try:
                    finit = self.MediaRepurposingFuncs.WaitForEntryDelete(self.client,entry.id)
                    if isinstance(finit, bool):
                        if finit:
                            self.logi.appendMsg('PASS - Entry is deleted by MR profile. entryId :' + str(entry.id))
                        else:
                            self.logi.appendMsg('FAIL - Entry is NOT deleted by MR profile - Entry timeout. entryId :' + str(entry.id))
                    else:
                        self.logi.appendMsg('FAIL - Entry is NOT deleted by MR profile - Entry error. entryId :' + str(entry.id))
                except Exception as Exp:
                    print(Exp)
                    self.logi.appendMsg('FAIL - Entry is NOT deleted by MR profile - Entry error. entryId :' + str(entry.id))
            else:############### PROUCTION - only Run Dry (real MR is taken few hours)
                self.logi.appendMsg('********* INFO - Going to verify that entry will be deleted by MR profile Dry Run. entryId :' + str(entry.id))
                self.logi.appendMsg('INFO - Going to get Media Repurposing profile ID .MediaRepurposingProfileName:' + self.MediaRepurposingProfileName)
                rc,MediaRepurposingID = self.MediaRepurposingFuncs.GetMediaRepurposingProfileId(self.MediaRepurposingProfileName)
                if not rc:
                    self.logi.appendMsg("FAIL - Could NOT get Media Repurposing ID. MediaRepurposingProfileName= " + self.MediaRepurposingProfileName)
                    testStatus = False
                    return
                 # Select MediaRepurposing profile id
                self.logi.appendMsg("INFO - Going to perform DRY RUN by:Media Repurposing ID = " + MediaRepurposingID)
                rc = self.MediaRepurposingFuncs.MediaRepurposing_DryRun(MediaRepurposingID)
                if not rc:
                    self.logi.appendMsg("FAIL - Could NOT perform dry run by - Media Repurposing ID= " + MediaRepurposingID)
                    testStatus = False
                    return
                time.sleep(3)

                ExpectedMediaRepurposingAlertResult = "Dry run for MR profile id [" + MediaRepurposingID + "] has been Assign. This could take couple of minutes. Results will be save to file."
                # Verify MediaRepurposing alert and return job id
                self.logi.appendMsg("INFO - Going to verify Alert result of dry run:Media Repurposing ID = " + MediaRepurposingID)
                rc,ActualbatchJobId = self.MediaRepurposingFuncs.MediaRepurposing_VerfiyAlertDryRun(MediaRepurposingID,ExpectedMediaRepurposingAlertResult)
                if not rc:
                    self.logi.appendMsg("FAIL - Verify dry run of - Media Repurposing ID= " + MediaRepurposingID )
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - Dry run of - Media Repurposing ID= " + MediaRepurposingID + " ,ActualbatchJobId = " + ActualbatchJobId )
                time.sleep(3)
                # Perform MediaRepurposing Dry Run Identification
                self.logi.appendMsg("INFO - Going to Perform MediaRepurposing Dry Run Identification: ActualbatchJobId = " + ActualbatchJobId)
                rc = self.MediaRepurposingFuncs.MediaRepurposing_DryRunIdentificationResultUntil1000(ActualbatchJobId,1,str(entry.id),str(entry.name))
                if not rc:
                    self.logi.appendMsg("FAIL - MediaRepurposing Dry Run Identification - ActualbatchJobId = " + ActualbatchJobId )
                    testStatus = False
                    return
                else:
                    self.logi.appendMsg("PASS - MediaRepurposing Dry Run Identification - Media Repurposing ID= " + MediaRepurposingID + " ,ActualbatchJobId = " + ActualbatchJobId )

        except Exception as Exp:
            print(Exp)
            testStatus = False
            self.logi.appendMsg("FAIL - on the test procedure")
        
        
    def teardown_class(self):
         
        global testStatus
        global CreateMRStatus
        
        try:
            if CreateMRStatus == True:
                self.logi.appendMsg("INFO - Going to delete MR profile, MR name: " + self.MediaRepurposingProfileName)
                #time.sleep(3)   
                rc = self.MediaRepurposingFuncs.MediaRepurposingProfileAction(self.MediaRepurposingProfileName,"remove")
                if not rc:
                    self.logi.appendMsg("FAIL - Delete MR profile, MR name: " + self.MediaRepurposingProfileName)
                    testStatus = False
                    return 
        except Exception as Exp:
            print(Exp) 
            pass

        try:
            self.Wd.quit()
        except:
            pass

        try:
            self.testTeardownclass.exeTear()
        except:
            pass
         
        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '1887','1')
            self.logi.reportTest('fail',self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '1887','0')
            self.logi.reportTest('pass',self.sendto)
            assert True
    
    #===========================================================================
    # pytest.main(args=['test_1887_MR_End2End.py','-s'])
    # pytest.main('test_1887_MR_End2End.py -s')
    #===========================================================================
