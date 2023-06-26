import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..', 'APITests','lib'))
sys.path.insert(1,pth)


import DOM
import MySelenium
import KmcBasicFuncs
import uploadFuncs
import reporter2

import Config
import Practitest
import Entrypage

# ======================================================================================
# Run_locally ONLY for writing and debugging *** ASSIGN False to use in automation!!!
# ======================================================================================
Run_locally = False
if Run_locally:
    import pytest
    isProd = True
    Practi_TestSet_ID = '1418'
else:
    ### Jenkins params ###
    cnfgCls = Config.ConfigFile("stam")
    Practi_TestSet_ID,isProd = cnfgCls.retJenkinsParams()
    if str(isProd) == 'true':
        isProd = True
    else:
        isProd = False

testStatus = True


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
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile  = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
                
            self.url    = inifile.RetIniVal(section, 'Url')
            self.user   = inifile.RetIniVal(section, 'userName5')
            self.pwd    = inifile.RetIniVal(section, 'passUpload')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.logi = reporter2.Reporter2('TEST955')
            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")
            self.entryPage = Entrypage.entrypagefuncs(self.Wd, self.logi)
            self.uploadfuncs = uploadFuncs.uploadfuncs(self.Wd, self.logi, self.Wdobj)
            self.practitest = Practitest.practitest('4586')
            self.entriesName = "Kaltura Site Audio New Cat,Kaltura Site Video New Cat,Kaltura Site Video few,Kaltura Site Audio few,Kaltura Site Video,Kaltura Site Audio"
        except Exception as e:
            print(e)
        
    def test_955(self):
        
        global testStatus
        self.logi.initMsg('test 955')
        
        try:
            #Login KMC
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.user, self.pwd)
            self.Wd.maximize_window()

            # Delete any entries or categories that might not have been deleted
            try:
                self.BasicFuncs.deleteEntries(self.Wd, self.entriesName, ",")
                self.BasicFuncs.deleteCategories(self.Wd, "New Category Audio;New Category Video;Sample Videos;Sample Audio")
            except Exception as e:
                print(e)
                    
            '''
            @EXISTING_CATEGORIES
            '''
            self.logi.appendMsg("")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("INFO - going to upload entries file for existing categories")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("")
            fname = "xml_file_uploadToExistingCategory_entries.xml"
            entries = '"Kaltura Site Video","Kaltura Site Audio"'
            expstatus = "Finished successfully"
            self.logi.appendMsg("INFO - going to test bulk upload to existing categories, upload file: " + fname)
                       
            entryList = entries.split(",")
            rc = self.uploadfuncs.bulkUploadAndEntriesVerify(fname, expstatus, entryList)
            if not rc:
                self.logi.appendMsg("Fail - failed bulk load 1")
                testStatus = False
                return
               
            self.logi.appendMsg("INFO - going to verify the entries inserted with the correct categories") 
            cnt =0 
            for i in entryList:
                entryCategories = self.entryPage.retEntryCategories(entryList[cnt])
                print(str(entryCategories))
                if cnt==0:
                    closeFilter = "Kaltura Site Video"
                    if entryCategories == "Sample Videos":
                           
                        self.logi.appendMsg("PASS - the entry category should have been: Sample Videos and it is as expected")
                    else:
                        self.logi.appendMsg("FAIL - the entry category should have been: Sample Videos")
                        testStatus = False
                        return
                else:
                    closeFilter = "Kaltura Site Audio"
                    if entryCategories == "Sample Audio":
                        self.logi.appendMsg("PASS - the entry category should have been: Sample Audio and it is as expected")
                    else:
                        self.logi.appendMsg("FAIL - the entry category should have been: Sample Audio")
                        testStatus = False
                        return
                           
                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                self.BasicFuncs.closeFilterTag(self.Wd,closeFilter)
                   
                # verify the entry appears when searching by its category
                self.logi.appendMsg("INFO - goning to search by the entry category filter and verify it appears")
                self.BasicFuncs.selectCategoryFilter(self.Wd, entryCategories)
                numOfEntriesFound = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if numOfEntriesFound == 1:
                    self.logi.appendMsg("PASS - the entry returned for the search in category: " + entryCategories)
                else:
                    self.logi.appendMsg("FAIL - looked for 1 returned entry for searching in category: " + entryCategories + " and actually retreived: " + str(numOfEntriesFound))
                    testStatus = False
                    return
                self.BasicFuncs.closeFilterTag(self.Wd, entryCategories)
                   
                cnt +=1                   
                  
            '''
            @NEW_CATEGORIES
            '''
            self.logi.appendMsg("")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("INFO - going to upload entries file for New categories")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("")
            fname = "xml_file_uploadToNewCategory_entries.xml"
            entries = '"Kaltura Site Audio New Cat","Kaltura Site Video New Cat"'
            expstatus = "Finished successfully"
            self.logi.appendMsg("INFO - going to test bulk upload to existing categories, upload file: " + fname)
                      
            entryList = entries.split(",")
            rc = self.uploadfuncs.bulkUploadAndEntriesVerify(fname, expstatus, entryList)
            if not rc:
                testStatus = False
                self.logi.appendMsg("Fail - failed bulk load 2")
                return
            self.logi.appendMsg("INFO - going to verify the entries inserted with the correct categories") 
            cnt =0 
            for i in entryList:
                entryCategories = self.entryPage.retEntryCategories(entryList[cnt])
                print(str(entryCategories))
                if cnt==0:
                    closeFilter = "Kaltura Site Audio New Cat"
                    if entryCategories == "New Category Audio":
                          
                        self.logi.appendMsg("PASS - the entry category should have been: New Category Audio and it is as expected")
                    else:
                        self.logi.appendMsg("FAIL - the entry category should have been: New Category Audio")
                        testStatus = False
                        return
                else:
                    closeFilter = "Kaltura Site Video New Cat"
                    if entryCategories == "New Category Video":
                        self.logi.appendMsg("PASS - the entry category should have been: New Category Video and it is as expected")
                    else:
                        self.logi.appendMsg("FAIL - the entry category should have been: New Category")
                        testStatus = False
                        return

                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                self.BasicFuncs.closeFilterTag(self.Wd,closeFilter)
                  
                # verify the entry appears when searching by its category
                self.logi.appendMsg("INFO - goning to search by the entry category filter and verify it appears")
                self.BasicFuncs.selectCategoryFilter(self.Wd, entryCategories)
                numOfEntriesFound = self.BasicFuncs.retNumOfRowsInEntryTbl(self.Wd)
                if numOfEntriesFound == 1:
                    self.logi.appendMsg("PASS - the entry returned for the search in category: " + entryCategories)
                else:
                    self.logi.appendMsg("FAIL - looked for 1 returned entry for searching in category: " + entryCategories + " and actually retreived: " + str(numOfEntriesFound))
                    testStatus = False
                    return
                self.BasicFuncs.closeFilterTag(self.Wd,entryCategories)
                  
                cnt +=1

            '''
            @FEW_CATEGORIES
            '''
            self.logi.appendMsg("")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("INFO - going to upload entries file related to Few categories")
            self.logi.appendMsg("================================================================")
            self.logi.appendMsg("")
            fname = "xml_file_uploadToMoreThanOneCategory_entries.xml"
            entries = '"Kaltura Site Video few","Kaltura Site Audio few"'
            expstatus = "Finished successfully"
            self.logi.appendMsg("INFO - going to test bulk upload to existing categories, upload file: " + fname)
                     
            entryList = entries.split(",")
            rc = self.uploadfuncs.bulkUploadAndEntriesVerify(fname, expstatus, entryList)
            if not rc:
                testStatus = False
                self.logi.appendMsg("Fail - failed bulk Upload 3")
                return

            self.logi.appendMsg("INFO - going to verify the entries inserted with the correct categories") 
            cnt =0 
            for i in entryList:
                entryCategories = self.entryPage.retEntryCategories(entryList[cnt])
                 
                if cnt==0:
                    closeFilter = "Kaltura Site Video few"
                    if entryCategories == "Sample Audio;Sample Videos;test;test1":
                         
                        self.logi.appendMsg("PASS - the entry category should have been: Sample Videos;Sample Audio;test;test1 and it is as expected")
                    else:
                        self.logi.appendMsg("FAIL - the entry category should have been: Sample Videos;Sample Audio")
                        testStatus = False
                        return
                else:
                    closeFilter = "Kaltura Site Audio few"
                    if entryCategories == "Sample Audio;Sample Videos;test;test1":
                        self.logi.appendMsg("PASS - the entry category should have been: Sample Audio;Sample Videos;test;test1 and it is as expected")
                    else:
     
                        self.logi.appendMsg("FAIL - the entry category should have been: Sample Audio;Sample Videos;test;test1")
                        testStatus = False

                self.Wd.find_element_by_xpath(DOM.ENTRIES_TAB).click()
                time.sleep(3)
                self.BasicFuncs.closeFilterTag(self.Wd,closeFilter)

                cnt +=1  
                  
            time.sleep(5)
        except Exception as e:
            print(e)
            testStatus = False

    def teardown_class(self):
        self.logi.appendMsg("")
        self.logi.appendMsg("====================== Tear Down =========================")
        self.logi.appendMsg("")
        global testStatus
        try:
            self.BasicFuncs.deleteEntries(self.Wd,self.entriesName,",")
            time.sleep(1)
            self.BasicFuncs.deleteCategories(self.Wd, "New Category Audio;New Category Video")
            time.sleep(1)
        except Exception as e:
            print(e)
        try:
            self.Wd.quit()
        except Exception as e:
            print(e)

        try:
            if testStatus == False:
                self.logi.reportTest('fail',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '955','1')
                assert False
            else:
                self.logi.reportTest('pass',self.sendto)
                self.practitest.post(Practi_TestSet_ID, '955','0')
                assert True
        except Exception as e:
            print(e)

    # ===========================================================================
    # pytest.main('test_955.py -s')
    if Run_locally:
        pytest.main(args=['test_955', '-s'])
    # ===========================================================================
          