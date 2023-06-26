import logging
import os
import Email

class Reporter:
    
    def __init__(self,TestsetName='CustomMetadataSet',loglevel=logging.INFO):
        try:
            os.remove(TestsetName+'.log')
            print('removed old log file')
        except:
            print('log file was not exist, no need to remove it')
        print('DEBUG: isProd = ' + str(os.getenv('isProd')))
        print('DEBUG: IsSRT = ' + str(os.getenv('IsSRT')))
        self.TestsetName = TestsetName
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='['+'%m/%d/%Y %I:%M:%S %p'+']',filename=TestsetName+'.log',level=loglevel)
            
        logging.info('################## START RUNNING '+TestsetName+' TEST SET ##################')
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Tests'))
        self.logfile = open(os.path.join(pth,TestsetName+'.log'),"w+")
        self.msg = '\t'
            
    def initMsg(self,testname):
        self.testname = testname
        logging.info('----------------------- ' + self.testname + '----------------------- ')
        print(('----------------------- ' + testname + '----------------------- '))
                        
    def appendMsg(self,newMsgLine):
        self.msg = self.msg +'\n' + '\t' + newMsgLine
        print(newMsgLine)
                
        
    def reportTest(self,TestStatus,iniSecSendTo='Environment'):
        if TestStatus=='pass':
            logging.info('**********  ' + self.testname+'    : PASS **********')
            print(('**********  ' + self.testname+'    : PASS **********'))
            print('-----------------------------------------------------------------')
        else:
            logging.info('**********  ' + self.testname + '    : FAIL **********' + '\n'+ str(self.msg))
            print(('**********  ' + self.testname+'    : FAIL **********'))
            print('-----------------------------------------------------------------')
            self.logfile.write(self.msg)
            self.logfile.close()
            logmail = Email.email(self.logfile,iniSecSendTo,self.msg)
            logmail.sendEmailFailtest(self.TestsetName)
        
        logger = logging.getLogger()
        logger.handlers[0].close()
        logger.removeHandler(logger.handlers[0])
         
    
        
    #===========================================================================
    # def log(self,msg):
    #     print msg
    #     self.msg = self.msg +'\n' + '\t' + msg
    #     
    #===========================================================================
        
        
        