'''

Moran.Cohen
this class lib includes reusable functions for AWS kubernetes for live NG
Use K8s connect:
https://github.com/kubernetes-client/python/blob/master/examples/remote_cluster.py
https://stackoverflow.com/questions/64221992/simple-way-to-delete-existing-pods-from-python

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


import datetime
import os
import sys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)
pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)

from io import open
import time
import threading

threadLock = threading.Lock()
threads = []

####################

import boto3
import base64
import json
from eks_token import get_token
from kubernetes import client, config
from kubernetes.stream import stream


namespace = "default"
arnRole = "arn:aws:iam::383697330906:role/nva1-win-slave-be-iam-role"

srt_selector = "component=srt"
packager_selector = "component=packager"
transcoder_selector = "component=transcoding-agent"
controller_selector= "component=controller"
monitor_selector= "component=monitor"


def getClient_name(cluster_name):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(RoleArn=arnRole, RoleSessionName="automationMachine")
    credentials = assumed_role_object['Credentials']
    eks_client = boto3.client('eks', region_name="us-east-1", aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],aws_session_token=credentials['SessionToken'])

    token = get_token(cluster_name=cluster_name, role_arn=arnRole)["status"]["token"]
    desc = eks_client.describe_cluster(name=cluster_name)
    conf = client.Configuration()
    conf.host = desc["cluster"]["endpoint"]
    conf.verify_ssl = True
    crt_content = base64.b64decode(desc["cluster"]["certificateAuthority"]["data"]).decode('utf-8')
    crt_path = 'C:\\' + cluster_name + '.crt'
    open(crt_path, 'w').write(crt_content)
    conf.ssl_ca_cert = crt_path
    conf.api_key['authorization'] = token
    conf.api_key_prefix['authorization'] = 'Bearer'
    return client.CoreV1Api(client.ApiClient(conf))


def getClient(cluster_id):
        if cluster_id == '1-a':
            return getClient_name('nvq1-eks-live-cluster-1-a')
        elif cluster_id == '1-b':
            return getClient_name('nvq1-eks-live-cluster-1-b')
        return getClient_name('nvq1-eks-live-manager-1')


class Kubernetes_Live():

    def __init__(self, client, logi,isProd, publisherId):
        self.client = client
        self.logi = logi
        self.isProd = isProd
        self.publisherId = publisherId

    #This function get Packager For EntryID
    # session_type=0 primary, 1 backup
    # cluster_id='1-a'/'1-b'
    def getPackagerForEntry(self,entry_id, session_type,cluster_id):
        try:
            print("cluster_id= " + str(cluster_id))
            exec_command = ['/bin/sh', '-c','python3 redis-cli.py --get CHANNEL_ASSOCIATION:' + entry_id + '_' + session_type]
            resp = stream(getClient(cluster_id).connect_get_namespaced_pod_exec, 'analyzers-0', namespace, command=exec_command,stderr=True, stdin=False, stdout=True, tty=False)
            res = json.loads(resp.replace("\'", "\""))
            self.logi.appendMsg("PASS - getPackagerForEntry = " + str(res['packagerId']))
            return res['packagerId']
        except Exception as err:
            print("Error in getting packagerId process.")
            self.logi.appendMsg("FAIL - getPackagerForEntry")
            print(str(err))
            return False

    #This function delete pod
    def deletePod(self,cluster_id, pod_name):

        client = getClient(cluster_id)
        try:
            res = client.delete_namespaced_pod(pod_name, namespace)
            if res and res.metadata.name == pod_name:
                print("Delete correct pod")
                self.logi.appendMsg("PASS - deletePod - Run RESTART Component got OK." + str(res.metadata.name))
                return pod_name
            else:
                print("Wrong deletion - deleted" + res.metadata.name)
                self.logi.appendMsg("FAIL - deletePod- Run RESTART Component failed." + str(res.metadata.name))
                return False
        except Exception as err:
            print("Error in deletion process")
            print(str(err))
            return False

    #This function list pods of the cluster_id
    def listPod(self,cluster_id, selector=None):
        try:

            print("Your listPod - selector is:" + str(selector))
            client = getClient(cluster_id)
            ret = client.list_namespaced_pod(namespace, label_selector=selector)
            # for i in ret.items:
            #    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            return [i.metadata.name for i in ret.items]

        except Exception as err:
            print("Error in listPod process")
            self.logi.appendMsg("FAIL - listPod")
            print(str(err))
            return False

    def getClusterId(cluster_id):
        return 'cluster-' + cluster_id + '.live.nvq1'

    # This function run the backup script
    #Send res = execRestoreRecording('1-a', '0_ywak2rut', '0_bvggy8dx', '0') - when streaming from primary
    #Send res = execRestoreRecording('1-b', '0_ywak2rut', '0_bvggy8dx', '1') - when streaming from backup
    # cluster_id='1-a'/'1-b'
    def execRestoreRecording(self,cluster_id, entry_id, recorded_entry_id, session_type):
        try:
            print("cluster_id= " + str(cluster_id))
            exec_command = ['curl', '-i', '-d','{\"channelId\" : \"' + entry_id + '\", \"recordedEntryId\" : \"' + recorded_entry_id + '\", \"sessionType\" : ' + session_type + ', \"clusterId\" : \"' + Kubernetes_Live.getClusterId(cluster_id) + '\", \"ignoreMissingTS\" : true}', '-H', 'Content-Type: application/json','-X', 'POST', 'http://localhost:8084/restorerecord']
            print("execRestoreRecording: Run exec_command = " + str(exec_command))
            Current_Controller = str(Kubernetes_Live.listPod(self, cluster_id=cluster_id, selector=controller_selector)[0])
            print("Run on Controller = " + str(Current_Controller))
            resp = stream(getClient(cluster_id).connect_get_namespaced_pod_exec, Current_Controller, namespace,command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)
            print("Run backup script:execRestoreRecording - OK")
            return resp
        except Exception as err:
            print("Error in execRestoreRecording process")
            print(str(err))
            return False


    # This function play the live entry
    def Kubernetes_verifyAllEntriesPlayOrNoBbyQrcode(self,liveObj, entrieslst, boolShouldPlay, MinToPlayEntry,PlayerVersion,QrCodecheckProgress=4,ServerURL=None):
        try:
            print ("QrCodecheckProgress = " + str(QrCodecheckProgress))
            # running as thread
            seenAll_justOnce_flag = True
            # LIVE ENTRY - Playback verification of all entries during packager RESTART
            self.logi.appendMsg("INFO - Going to play LIVE ENTRY " + str(entrieslst) + "  live entries on preview&embed page during - MinToPlay=" + str(MinToPlayEntry) + " , Start time = " + str(datetime.datetime.now()))
            limitTimeout = datetime.datetime.now() + datetime.timedelta(0, MinToPlayEntry * 60)
            seenAll = False
            while datetime.datetime.now() <= limitTimeout and seenAll == False:
                rc = liveObj.verifyAllEntriesPlayOrNoBbyQrcode(entrieslst, boolShouldPlay, MinToPlayEntry,PlayerVersion,QrCodecheckProgress=QrCodecheckProgress,ServerURL=ServerURL)
                time.sleep(5)
                if not rc:
                    #testStatus = False
                    return False
                if seenAll_justOnce_flag == True:
                    seenAll = True

            self.logi.appendMsg("PASS - LIVE ENTRY Playback of " + str(entrieslst) + " live entries on preview&embed page during - MinToPlay=" + str(MinToPlayEntry) + " , End time = " + str(datetime.datetime.now()))
            return True

        except Exception as err:
            print(str(err))
            return False

    # This function get Transcoder for EntryId
    #res = getTranscoderForEntry('0_76i6kgsq', '0')
    # session_type= 0 primary, 1 backup
    # cluster_id='1-a'/'1-b'
    def getTranscoderForEntry(self, entry_id, session_type,cluster_id):
        try:
            print("cluster_id= " + str(cluster_id))

            st = 'p' if session_type == '0' else 'b'
            exec_command = ['/bin/sh', '-c','python3 redis-cli.py --keys transcoder:*' + entry_id + '*' + '@' + st + ':*']
            res = stream(getClient(cluster_id).connect_get_namespaced_pod_exec, 'analyzers-0', namespace, command=exec_command,stderr=True, stdin=False, stdout=True, tty=False)
            transcoders = map(lambda x: x.split(':')[1], res.splitlines())
            return list(set(transcoders))

        except Exception as err:
            print("Error in getting Transcoder: " + str(err))
            return False