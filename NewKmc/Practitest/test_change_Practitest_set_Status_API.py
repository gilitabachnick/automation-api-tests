import os
import sys
import pytest

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)
import Practitest
import Config




### Jenkins params ###
theFile = '/home/ubuntu/jenkins/workspace/Host.txt'
cnfgCls = Config.ConfigFile(theFile)
Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()

if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:

    def test_1308(self):

        print("-------1---------")
        self.practitest = Practitest.practitest('4586','APITests')

        sessionId, boolRunOnlyFailed = self.practitest.getPractiTestAutomationSession()
        print("-------2---------")

        try:
            self.practitest.setTestSetAutomationStatusAsProcessed(Practi_TestSet_ID)
        except Exception as Exp:
            print(Exp)
        try:
            tstList = self.practitest.getPractiTestSessionInstances(sessionId, boolRunOnlyFailed)
        except Exception as Exp:
            print(Exp)

        rc = self.practitest.copyTestsForExecution(tstList)

        if rc:
            print(" Starting test execution")
        else:
            print("!!!! Could NOT start the test run, something went Wrong with the copying tests process !!!!")

    pytest.main(['test_change_Practitest_set_Status_API.py','s'] )