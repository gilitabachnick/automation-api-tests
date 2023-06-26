import os
import sys
import time

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
sys.path.insert(1, pth)
pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import MySelenium
import KmcBasicFuncs
import reporter2
import Config
import Practitest

from onesecmail import OneSecMail
from onesecmail.validators import SubjectValidator
from urlextract import URLExtract


### Jenkins params ###
cnfgCls = Config.ConfigFile("stam")
Practi_TestSet_ID, isProd = cnfgCls.retJenkinsParams()
if str(isProd) == 'true':
    isProd = True
else:
    isProd = False

testStatus = True

class TestClass:
    # ===========================================================================
    # SETUP
    # ===========================================================================
    def setup_class(self):

        try:
            pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ini'))
            if isProd:
                section = "Production"
                self.env = 'prod'
                print('PRODUCTION ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini'))
            else:
                section = "Testing"
                self.env = 'testing'
                print('TESTING ENVIRONMENT')
                inifile = Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))

            self.url = inifile.RetIniVal(section, 'Url')
            self.sendto = inifile.RetIniVal(section, 'sendto')
            self.BasicFuncs = KmcBasicFuncs.basicFuncs()
            self.practitest = Practitest.practitest('4586')
            self.emailReset = inifile.RetIniVal(section, 'emailReset')

            self.logi = reporter2.Reporter2('TEST2397_reset_password')

            self.Wdobj = MySelenium.seleniumWebDrive()
            self.Wd = self.Wdobj.RetWebDriverLocalOrRemote("chrome")

        except:
            pass

    def test_2397_reset_password(self):

        global testStatus
        MAXTIME = 300
        self.timestmp = str(time.strftime("%c"))
        self.logi.initMsg('test 2397_reset_password')

        try:
            self.logi.initMsg('Reseting password...')
            rc = self.BasicFuncs.resetPassword(self.Wd, self.Wdobj, self.logi, self.url, self.emailReset)
            if rc:
                self.logi.appendMsg('Password reset success!')
                self.logi.appendMsg('Going to check that a new Reset Password email arrived...')
                endoftime = False
                mailArrived = False
                timepassed = 0
                # wait for email to arrive
                time.sleep(10)
                while not endoftime and not mailArrived:
                    mailbox = OneSecMail.from_address(self.emailReset)
                    subject_validator = SubjectValidator("Your Kaltura user password has been reset")
                    messages = mailbox.get_messages(validators=[subject_validator])    # get only password reset messages
                    my_message = messages[0].body    # get first message from Kaltura
                    if not isinstance(my_message, bool):   # case messages found in the inbox
                        extractor = URLExtract()
                        urls = extractor.find_urls(my_message)    # look for key string in mail
                        if not isinstance(urls, bool):  # URL found
                            self.resetURL = urls[0]
                            self.logi.appendMsg('Reset password mail found, the reset link is: ' + self.resetURL)
                            time.sleep(5)
                            mailArrived = True
                        else:
                            time.sleep(10)
                            timepassed = timepassed + 10
                            if timepassed > MAXTIME:
                                endoftime = True
                    else:
                        time.sleep(10)
                        timepassed = timepassed + 10
                        if timepassed > MAXTIME:
                            endoftime = True

                if not mailArrived:
                    assert False
                else:
                    assert True

            #Follow reset password link, set new password
            self.randPass = self.BasicFuncs.generateRandomPassword(7)    # generate new password
            if isinstance(self.randPass, str):
                self.logi.appendMsg('Generated random secure password ' + self.randPass)
            else:
                self.logi.appendMsg("Couldn't generate new secure password, failed!")
                testStatus = False
                pass
            #Using reset URL, reset password
            rc = self.BasicFuncs.setNewPassword(self.Wd,self.Wdobj, self.logi, self.resetURL,self.randPass)
            if rc:
                self.logi.appendMsg('Set new password successfully, going to login using it...')
            else:
                self.logi.appendMsg("Couldn't set new password, failed!")
                testStatus = False
                pass
            # Try to log in with new credentials
            rc = self.BasicFuncs.invokeLogin(self.Wd, self.Wdobj, self.url, self.emailReset, self.randPass)
            if rc:
                self.logi.appendMsg('Login with new password success, test passed!')
            else:
                self.logi.appendMsg("Couldn't log in with new password, failed!")
                testStatus = False
                pass
        except Exception as EXP:
            print(EXP)
            testStatus = False
            pass

    # ===========================================================================
    # TEARDOWN
    # ===========================================================================
    def teardown_class(self):

        global testStatus
        self.Wd.quit()

        if testStatus == False:
            self.practitest.post(Practi_TestSet_ID, '2397', '1')
            self.logi.reportTest('fail', self.sendto)
            assert False
        else:
            self.practitest.post(Practi_TestSet_ID, '2397', '0')
            self.logi.reportTest('pass', self.sendto)
            assert True
    #===========================================================================
    #pytest.main(args=['test_2397_reset_password.py', '-s'])
    #===========================================================================
