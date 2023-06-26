'''

Moran.Cohen
this class lib includes reusable functions for AWS kubernetes for live NG
https://kaltura.atlassian.net/browse/VCP-8553
AWS machine for kubernetes connection:
login to 10.204.1.227(private ip) OR 18.234.42.64(public)
pwd = ykF19nsFl9#iCHu8eR%T@6C2E0db$Uu
user= root
Clusters Types:
"aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
"aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
Cmd lines:
"kubectl get pods|grep controllers"
# Run backup recording entry script
kubectl exec -i controllers-56459684df-tqgvd  -- curl -i -d '{"channelId" : "0_7s6z104t", "recordedEntryId" : "0_iei8xj5m", "sessionType" : 1, "clusterId" : "cluster-1-b.live.nvq1"}' -H "Content-Type: application/json" -X POST  http://localhost:8084/restorerecord
python3 redis-cli.py --keys \*
python3 redis-cli.py --get <somekey>
python3 redis-cli.py --set <somekey> <someval>
python3 redis-cli.py --ttl <somekey>
python3 redis-cli.py --delete <somekey>
python3 redis-cli.py --mget <somekey_1> ... <somekey_n>
python3 redis-cli.py --get-unzipped <somekey>
Get packager :
kubectl exec -it analyzers-0 -- sh -c "python3 redis-cli.py --get CHANNEL_ASSOCIATION:0_b9ecn7lo_0" | awk '{print substr($1,15,12)}' | sed -e 's/^"//' -e 's/"$//'
CHANNEL_ASSOCIATION:0_b9ecn7lo_0 (if it's primary)

https://github.com/kaltura/live/wiki/How-to#non-interactive-mode
'''

import _thread
import datetime
import os
import sys
import time



from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

import Entry
import strclass
import clsPlayerV2
import QrcodeReader
import paramiko
import KmcBasicFuncs


from selenium.webdriver.common.action_chains import ActionChains
from io import open
import json
import pickle

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Caption import *
import paramiko
from KalturaClient import *
from KalturaClient.Plugins.Schedule import *


pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)
import Entrypage
import re
import threading

threadLock = threading.Lock()
threads = []

class Kubernetes_Live():

    def __init__(self, client, logi,isProd, publisherId):
        self.client = client
        self.logi = logi
        self.isProd = isProd
        self.publisherId = publisherId


    #This function connect to kubernetes linux machines and perform cmd lines:
    # KubernetesCmdLine_clusterType - First Set cluster type "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1" OR "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    # KubernetesCmdLines - Run Kubernetes cmd line
    # The function return the result of KubernetesCmdLines
    def Start_KubernetesByCmd(self, host, user, passwd, KubernetesCmdLine_clusterType, entryId, partnerId,env='testing', BroadcastingUrl=None, KubernetesCmdLines=None):

        try:
            statusStreaming = False
            self.logi.appendMsg("INFO - Going to connect to ssh.host = " + host + " , user = " + user + " , passwd = " + passwd + ", entryId = " + entryId + " , partnerId= " + partnerId)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd, timeout=60)#was timeout=5
            remote_conn = ssh.invoke_shell()
            #print("Interactive SSH - Going to run.ffmpegCmdLine = " + ffmpegCmdLine)
            self.logi.appendMsg("INFO - Interactive SSH - Going to run KubernetesCmdLine_clusterType = " + KubernetesCmdLine_clusterType)
            self.logi.appendMsg("INFO - Interactive SSH - KubernetesCmdLine_clusterType datetime " + str(datetime.datetime.now()))
            output = remote_conn.recv(1000)
            remote_conn.send("\n")
            time.sleep(1)
            remote_conn.send(KubernetesCmdLine_clusterType + "\n")
            #print(ffmpegCmdLine)
            time.sleep(15)
            output = str(remote_conn.recv(10000))
            output = output.replace('\\r\\n',os.linesep).replace('\\r',os.linesep)
            self.logi.appendMsg("INFO - KubernetesCmdLine_clusterType output = " + str(output))
            if output.find("Updated context arn:aws:eks:") >= 0:
                self.logi.appendMsg("PASS - Updated context arn:aws:eks is performed - KubernetesCmdLine_clusterType output = " + str(output))
            else:
                self.logi.appendMsg("FAIL - Updated context arn:aws:eks is NOT performed - KubernetesCmdLine_clusterType output = " + str(output))
                return False, "NoConnectionToCluster_" + str(output)
            #self.Search_KubernetesStrResult(output,clusterSelection)
            if KubernetesCmdLines!=None:
                self.logi.appendMsg("INFO - Interactive SSH - Going to run KubernetesCmdLines = " + KubernetesCmdLines)
                self.logi.appendMsg("INFO - Interactive SSH - KubernetesCmdLine_clusterType datetime " + str(datetime.datetime.now()))
                remote_conn = ssh.invoke_shell()
                output = remote_conn.recv(1000)
                remote_conn.send("\n")
                time.sleep(1)
                remote_conn.send(KubernetesCmdLines + "\n")
                # print(ffmpegCmdLine)
                time.sleep(15)
                output = str(remote_conn.recv(10000))
                output = output.replace('\\r\\n', os.linesep).replace('\\r', os.linesep)
                self.logi.appendMsg("INFO - KubernetesCmdLines output = " + str(output))
                if output == "" or output=='b\'\'' or str(output.split("\n")[2]) == '[root@ip-10-204-1-227 ~]# \'':#Check If return empty result
                    self.logi.appendMsg("FAIL - KubernetesCmdLines return EMPTY output = " + str(output))
                    return False, "NoKubernetesCmdLines_" + str(output)

            return True,str(output)

        except Exception as err:
            print(err)
            return False,err

    # This function get Packager By EntryId
    # host, user, passwd- Detail of the Kubernetes access machine.
    # KubernetesCmdLine_clusterType =  "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
    # Or "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    # entryId - get Packager By EntryId
    def Kubernetes_getPackagerByEntryId(self, host, user, passwd, KubernetesCmdLine_clusterType, entryId, partnerId,env='testing', BroadcastingUrl=None):
        try:
            #KubernetesCmdLines = "kubectl exec -it analyzers-0 -- python3 redis-cli.py <<< \"get CHANNEL_ASSOCIATION:" + str(entryId) + "_0\" | grep packager-"
            KubernetesCmdLines = f"""kubectl exec -it analyzers-0 -- sh -c \"python3 redis-cli.py --get CHANNEL_ASSOCIATION:""" + str(entryId) + f"""_0\" | awk '{{print substr($1,15,12)}}' | sed -e 's/^"//' -e 's/"$//'"""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes - GET packager by entryId: entryId=" + entryId)
            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType,entryId,partnerId,env,BroadcastingUrl,KubernetesCmdLines)
            no_spaces_output = re.sub(r'\s', '', Kubernetes_output)
            #no_spaces_output = no_spaces_output.replace("\\x1b[m\\x1b[K", "")
            packagers = re.findall('(packager-[0-9])', no_spaces_output)
            if rc_Kubernetes == True:
                self.logi.appendMsg("PASS - Kubernetes_getPackagerByEntryId .Kubernetes_output" + str(Kubernetes_output))
            else:
                self.logi.appendMsg("FAIL - Kubernetes_getPackagerByEntryId .Kubernetes_output" + str(Kubernetes_output))
                testStatus = False
                return False
            currentPackager = str(packagers[0])  # set current packager
            return currentPackager
        except Exception as err:
            print(err)
            return False

    # This function play the live entry
    def Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(self,liveObj, entrieslst, boolShouldPlay, MinToPlayEntry,PlayerVersion,QrCodecheckProgress=4):
        try:
            print ("QrCodecheckProgress = " + str(QrCodecheckProgress))
            # running as thread
            seenAll_justOnce_flag = True
            # LIVE ENTRY - Playback verification of all entries during packager RESTART
            self.logi.appendMsg("INFO - Going to play LIVE ENTRY " + str(entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(MinToPlayEntry) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entrieslst, boolShouldPlay, MinToPlayEntry,PlayerVersion,QrCodecheckProgress=QrCodecheckProgress)
                time.sleep(5)
                if not rc:
                    #testStatus = False
                    return False
                if seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - LIVE ENTRY Playback of " + str(entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(MinToPlayEntry) + " , End time = " + str(datetime.datetime.now()))
            return True

        except Exception as err:
            print(err)
            return False

    # This function Restart component- Packager/transcoder
    def Kubernetes_RestartComponent(self,host,user,passwd,entryId,partnerId,env,BroadcastingUrl,currentComponent,KubernetesCmdLine_clusterType = "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1",SearchResult=None):
        try:
            #self.logi.appendMsg("INFO - Going to perform Kubernetes RestartPackager to currentPackager = " + currentComponent + " ,  datetime=" +  str(datetime.datetime.now()))
            KubernetesCmdLines = f"""kubectl delete pod {currentComponent}"""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes cmd2 - RESTART Component): KubernetesCmdLines=" + KubernetesCmdLines)
            #KubernetesCmdLine_clusterType = "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
            if SearchResult == None:
                SearchResult = f"""pod "{currentComponent}" deleted"""

            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType,entryId,partnerId,env,BroadcastingUrl,KubernetesCmdLines)
            if rc_Kubernetes == True:
                if Kubernetes_output.find(SearchResult) >= 0:
                    self.logi.appendMsg("PASS - Start_KubernetesByCmd - Run RESTART Component got OK.")
                else:
                    self.logi.appendMsg("FAIL - Start_KubernetesByCmd- Run RESTART Component failed.")
                    return False
            else:
                self.logi.appendMsg("FAIL - Start_KubernetesByCmd .Kubernetes_output" + str(Kubernetes_output))
                return False

            return True
        except Exception as err:
            print(err)
            return False

    # This function get Packager By EntryId
    # host, user, passwd- Detail of the Kubernetes access machine.
    # KubernetesCmdLine_clusterType =  "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
    # Or "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    # entryId - get Transcoder By EntryId
    def Kubernetes_getTranscoderByEntryId(self, host, user, passwd, KubernetesCmdLine_clusterType, entryId, partnerId,env='testing', BroadcastingUrl=None):
        try:
            KubernetesCmdLines = f"""kubectl exec -it analyzers-0 -- sh -c \"python3 redis-cli.py --keys transcoder:\\*""" + str(entryId) + f"""\\*\""""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes - GET Transcoder by entryId: entryId=" + entryId)
            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType,entryId,partnerId,env,BroadcastingUrl,KubernetesCmdLines)
            #no_spaces_output = re.sub(r'\s', '', Kubernetes_output)
            #Transcoders = re.findall('(transcoding-agent-[0-9])', no_spaces_output)
            Transcoders = re.findall('(transcoding-agent-([A-Za-z0-9\\-\\_]+))', Kubernetes_output)
            if rc_Kubernetes == True:
                self.logi.appendMsg("PASS - Kubernetes_getTranscoderByEntryId .Kubernetes_output" + str(Kubernetes_output))
            else:
                self.logi.appendMsg("FAIL - Kubernetes_getTranscoderByEntryId .Kubernetes_output" + str(Kubernetes_output))
                testStatus = False
                return False
            currentTranscoder = str(Transcoders[0][0])  # set current Transcoder
            return currentTranscoder
        except Exception as err:
            print(err)
            return False

    # This function get All Transcoders on QA env
    # host, user, passwd- Detail of the Kubernetes access machine.
    # KubernetesCmdLine_clusterType =  "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
    # Or "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    def Kubernetes_getAllTranscoders(self, host, user, passwd, KubernetesCmdLine_clusterType, entryId, partnerId,env='testing', BroadcastingUrl=None):
        try:
            #KubernetesCmdLines = f"""kubectl get pods | grep transcoding-agent-"""
            KubernetesCmdLines = f"""kubectl get pod -l component=transcoding-agent"""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes - GET All Transcoders")
            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType,entryId,partnerId,env,BroadcastingUrl,KubernetesCmdLines)
            #no_spaces_output = re.sub(r'\s', '', Kubernetes_output)
            #no_spaces_output = no_spaces_output.replace("\\x1b[m\\x1b[K", "")
            #Transcoders = re.findall('(transcoding-agent-[0-9])', no_spaces_output)

            Transcoders = re.findall('(transcoding-agent-([A-Za-z0-9\\-\\_]+))', Kubernetes_output)
            if rc_Kubernetes == True:
                self.logi.appendMsg("PASS - Kubernetes_getTranscoderByEntryId .Kubernetes_output" + str(Kubernetes_output))
            else:
                self.logi.appendMsg("FAIL - Kubernetes_getTranscoderByEntryId .Kubernetes_output" + str(Kubernetes_output))
                testStatus = False
                return False

            return Transcoders
        except Exception as err:
            print(err)
            return False


    # This function config kubectl use-context according to  CONTEXT_NAME
    # kubectl config use-context CONTEXT_NAME
    # Example:kubectl config use-context arn:aws:eks:us-east-1:383697330906:cluster/nvq1-eks-live-cluster-1-a
    ''' Precondition: Upgrade the cluster, please try both command:
        kubectx -d arn:aws:eks:us-east-1:383697330906:cluster/nvq1-eks
        OR
        aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-b --region us-east-1
        kubectl config get-contexts
        kubectl context CONTEXT_NAME'''
    def Kubernetes_ConfigUseContext(self, host, user, passwd, entryId, partnerId, env, BroadcastingUrl,KubernetesCmdLine_clusterType="aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1",CONTEXT_NAME="arn:aws:eks:us-east-1:383697330906:cluster/nvq1-eks-live-cluster-1-a",SearchResult=None):

        try:
            KubernetesCmdLines = f"""kubectl config use-context {CONTEXT_NAME}"""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes cmd - kubectl config use-context CONTEXT_NAME): KubernetesCmdLines=" + KubernetesCmdLines)
            if SearchResult == None:
                SearchResult = f"""Switched to context "{CONTEXT_NAME}"""""

            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host, user, passwd,KubernetesCmdLine_clusterType, entryId,partnerId, env, BroadcastingUrl,KubernetesCmdLines)
            if rc_Kubernetes == True:
                if Kubernetes_output.find(SearchResult) >= 0:
                    self.logi.appendMsg("PASS - Start_KubernetesByCmd - RUN kubectl config use-context CONTEXT_NAME got OK.")
                else:
                    self.logi.appendMsg("FAIL - Start_KubernetesByCmd- RUN kubectl config use-context CONTEXT_NAME FAILED.")
                    return False
            else:
                self.logi.appendMsg("FAIL - Start_KubernetesByCmd .Kubernetes_output" + str(Kubernetes_output))
                return False

            return True
        except Exception as err:
            print(err)
            return False

    # This function get controllers
    # host, user, passwd- Detail of the Kubernetes access machine.
    # KubernetesCmdLine_clusterType =  "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
    # Or "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    def Kubernetes_getcontrollers(self, host, user, passwd, KubernetesCmdLine_clusterType, entryId, partnerId,env='testing', BroadcastingUrl=None):
        try:

            KubernetesCmdLines = "kubectl get pods|grep controllers | grep -o \"controllers-\S*\""
            self.logi.appendMsg("INFO - ************** Going to perform kubernetes getcontrollers: KubernetesCmdLines=" + KubernetesCmdLines)
            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType=KubernetesCmdLine_clusterType,entryId=entryId,partnerId=partnerId,env=env,BroadcastingUrl=BroadcastingUrl,KubernetesCmdLines=KubernetesCmdLines)
            no_spaces_output = re.sub(r'\s', '', Kubernetes_output)
            controllers = re.findall('(controllers-\S[^\\\[]+)', no_spaces_output)  # return controllers list
            if rc_Kubernetes == True:
                self.logi.appendMsg("PASS - Start_KubernetesByCmd - getcontrollers .Kubernetes_output" + Kubernetes_output)
            else:
                self.logi.appendMsg("FAIL - Start_KubernetesByCmd - getcontrollers .Kubernetes_output" + Kubernetes_output)
                return False
            currentontroller = str(controllers[0])  # set current controller
            return currentontroller

        except Exception as err:
            print(err)
            return False

    # This function RunBackupContentScript
    # host, user, passwd- Detail of the Kubernetes access machine.
    # KubernetesCmdLine_clusterType =  "aws eks update-kubeconfig --name nvq1-eks-live-cluster-1-a --region us-east-1"
    # Or "aws eks update-kubeconfig --name nvq1-eks-live-manager-1 --region us-east-1"
    # Precondition - currentontroller ,entryId=live entry,recordedEntryId,clusterId
    def Kubernetes_RunBackupContentScript(self, host, user, passwd, KubernetesCmdLine_clusterType,currentontroller ,entryId,recordedEntryId,clusterId, partnerId,env='testing',BroadcastingUrl=None):
        try:

            KubernetesCmdLines = f"""kubectl exec -i "{currentontroller}"  -- curl -i -d '{{"channelId" : "{entryId}", "recordedEntryId" : "{recordedEntryId}", "sessionType" : 1, "clusterId": "{clusterId}"}}' -H "Content-Type: application/json" -X POST  http://localhost:8084/restorerecord"""

            self.logi.appendMsg("INFO - ************** Going to perform kubernetes -RunBackupContentScript: KubernetesCmdLines=" + KubernetesCmdLines)
            rc_Kubernetes, Kubernetes_output = self.Start_KubernetesByCmd(host,user,passwd,KubernetesCmdLine_clusterType=KubernetesCmdLine_clusterType,entryId=entryId,partnerId=partnerId,env=env,BroadcastingUrl=BroadcastingUrl,KubernetesCmdLines=KubernetesCmdLines)
            if rc_Kubernetes == True:
                if Kubernetes_output.find("OK") >= 0 and Kubernetes_output.find('Content-Length: 4\r\n'):
                    self.logi.appendMsg("PASS - Start_KubernetesByCmd - Run backup script got OK .Kubernetes_output = " + str(Kubernetes_output))
                else:
                    self.logi.appendMsg("FAIL - Start_KubernetesByCmd- Run backup script failed. Kubernetes_output = " + str(Kubernetes_output))
                    return False
            else:
                self.logi.appendMsg("FAIL - Start_KubernetesByCmd .Kubernetes_output" + Kubernetes_output)
                return False

        except Exception as err:
            print(err)
            return False