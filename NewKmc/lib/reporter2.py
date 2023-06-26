'''
Created on Jun 7, 2017

@author: Adi.Miller
'''
import logging
import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'APITests', 'lib'))
sys.path.insert(1, pth)

import Email


class Reporter2:
    
    def __init__(self,testname='CustomMetadataSet',loglevel=logging.INFO):
        try:
            os.remove(testname+'.log')
            print('removed old log file')
        except:
            print('log file was not exist, no need to remove it')
        print('DEBUG: isProd = ' + str(os.getenv('isProd')))
        print('DEBUG: IsSRT = ' + str(os.getenv('IsSRT')))
        self.testname = testname
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='['+'%m/%d/%Y %I:%M:%S %p'+']',filename=testname+'.log',level=loglevel)
        logging.info('################## START RUNNING '+testname+' TEST SET ##################')
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Tests'))
        self.logfile = open(os.path.join(pth,testname+'.log'),"w+")
        self.msg = '\t'
            
    def initMsg(self,testname):
        self.testname = testname
        logging.info('----------------------- ' + self.testname + '----------------------- ')
        print('----------------------- ' + testname + '----------------------- ')
                        
    def appendMsg(self,newMsgLine):
        self.msg = self.msg +'\n' + '\t' + newMsgLine
        print(newMsgLine)
                
        
    def reportTest(self,TestStatus,sendTo=None):
        if TestStatus=='pass':
            logging.info('**********  ' + self.testname+'    : PASS **********')
            print('**********  ' + self.testname+'    : PASS **********')
            print('-----------------------------------------------------------------')
        else:
            logging.info('**********  ' + self.testname + '    : FAIL **********' + '\n'+ str(self.msg))
            print('**********  ' + self.testname+'    : FAIL **********')
            print('-----------------------------------------------------------------')

            self.logfile.write(self.msg)
            self.logfile.close()
            logmail = Email.email(self.logfile, sendTo, self.msg)

            try:
                logmail.sendEmailFailtest(self.testname)
            except:
                print("could not send fail test email")
                pass
    
           
    
        
    #===========================================================================
    # def log(self,msg):
    #     print msg
    #     self.msg = self.msg +'\n' + '\t' + msg
    #     
    #===========================================================================
        
        
        