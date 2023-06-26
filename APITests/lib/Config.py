#from pip._vendor.requests.packages.urllib3.util.connection import select
import configparser
import datetime
import os
import platform
import socket

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


# ini file parser class
class ConfigFile:
    
    def __init__(self,filepth):
        self.filepth = filepth

    # return ini file parameter value by its section and parameter name
    def RetIniVal(self,section,param):
        cnfg = configparser.RawConfigParser()
        cnfg.read(self.filepth)
        return cnfg.get(section,param)

    def retJenkinsParams(self, iniFilepth=None ):

        print(("@@@@@@@@@@@@@ TEST START TIME: " + str(datetime.datetime.now()) + " @@@@@@@@@@@@@@@"))

        cnfg = configparser.RawConfigParser()
        runOnHost = 'Host.txt'
        if platform.system()=='Windows':
            # compName = str(os.environ['COMPUTERNAME'])
            # print("COMPUTER NAME=" + str(compName))
            # if compName.lower() == 'il-beplayer10-q':
            #     runOnHost = 'Host1.txt'
            # elif compName.lower() == 'lbewin10-1':
            #     runOnHost = 'Host2.txt'
            # elif compName.lower() == 'lbewin10-2':
            #     runOnHost = 'Host3.txt'
            # elif compName.lower() == 'lbewin10-reach':
            #     runOnHost = 'Host4.txt'
            # elif compName.lower() == 'lbewin10-selfse':
            #     runOnHost = 'Host5.txt'
            if iniFilepth == None:
                iniFilepth = r'C:\jenkins\workspace' + '\\' + runOnHost

        else:
            # compName = str(socket.gethostname())
            # if compName.lower() == 'fe-auto.dev.kaltura.com':
            # runOnHost = 'FE_auto.txt'

            if iniFilepth == None:
                iniFilepth = '/home/ubuntu/jenkins/workspace/' + runOnHost
            # print("COMPUTER NAME=" + str(compName))


        cnfg.read(iniFilepth)

        return cnfg.get("env", "Practi_TestSet_ID"), cnfg.get("env", "isProd")