import os
import sys

import pytest

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','..','APITests', 'lib'))
print(str(pth))
sys.path.insert(1,pth)
import Practitest


class Test:
    
    #===================================================================================================================================
    # This script if for test automation night run, which is triggered from Jenkins at night.
    # Sets all testsets under specified filter ('Night Run' under current version), to Pending and disable 'Automation Run Only FAILED'.
    # Sets all tests in each testset to No Run
    #===================================================================================================================================
    #localSettings.LOCAL_SETTINGS_APPLICATION_UNDER_TEST = enums.Application.MEDIA_SPACE
    practiTest          = Practitest.practitest('4586')
    testNum             = "run_all"
    status              = "Pass"   
    filter              = "745646"
    onlyExecuteAtNight  = False 
    
    
    def test_01(self):
        try:
            # Get all Testset under specified Filter ID
            print("INFO","Going to get all testsets instance ids under filter " + self.filter)
            testSetList = self.practiTest.getPractiTestTestSetByFilterId(self.filter, onlyExecuteAtNight=self.onlyExecuteAtNight)
            if testSetList == False:
                print("INFO","FAILED to get all testsets instance ids under filter " + self.filter)
                self.status = "Fail"                    
              
            print("INFO","Going to set No Run status to all testsets under filter " + self.filter)            
            if self.practiTest.setStatusToEntireTestset(testSetList, 'NO RUN') == False:
                print("INFO","FAILED to set No Run status to all testset under filter " + self.filter)
                self.status = "Fail"
                  
            #===================================================================
            # print "INFO","Going to set 'Automation Status' as 'Pending' to all testsets under filter " + self.filter
            # print "INFO","Going to set 'Automation Run Only FAILED ' as 'False' to all testsets under filter " + self.filter
            # customFiledsDict =  OrderedDict({'---f-50308':'Pending'})          
            # if self.practiTest.updateTestsetsCustomFields(testSetList, customFiledsDict) == False:
            #     print "INFO","FAILED to set 'Automation Status' as 'Pending' to all testsets under filter " + self.filter           
            #     self.status = "Fail"                
            #===================================================================

         
        except Exception as inst:
            print("fail start nightly build")
                
    def teardown_method(self,method):
        assert (self.status == "Pass")   
        
    pytest.main('test_' + testNum  + '.py --tb=line')