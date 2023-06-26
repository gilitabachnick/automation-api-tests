'''
Created on Jan 11, 2017

@author: Adi.Miller
'''

import datetime
import time

from KalturaClient.Plugins import AdCuePoint
from KalturaClient.Plugins import CuePoint


class AddStitching:
    


    def __init__(self, client, entryId):
        self.entryId = entryId
        self.client = client
    
    '''
    this function insert add queue point 
    Paramters:
        @triggerAt - send the number of seconds from now to insert the queue point
        @durTime - is the time of the played add
    '''
    def getnowEpochTime(self):
        dt1 = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        pattern = '%d.%m.%Y %H:%M:%S'
        epoch = int(time.mktime(time.strptime(dt1, pattern)))
        return epoch
    
    
    def addCuePoint(self, triggerAt,epoch, durTime=60000):
        cuePoint = AdCuePoint.KalturaAdCuePoint()
        cuePoint.entryId = self.entryId
               
        cuePoint.triggeredAt = epoch+triggerAt
        cuePoint.sourceUrl = 'http://projects.kaltura.com/aviya/ProductionRegularADV-Auto.xml'
        cuePoint.adType = AdCuePoint.KalturaAdType.OVERLAY
        cuePoint.duration = durTime
        
        try:
            self.client.cuePoint.cuePoint.add(cuePoint)
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch+triggerAt))
        except Exception as exp:
            print(exp)
            return False
            
    
    def retCuePointsforEntry(self):   
         
        cuefilter = CuePoint.KalturaCuePointFilter()
        cuefilter.entryIdEqual = self.entryId
        pager = None
        try:
            return self.client.cuePoint.cuePoint.list(cuefilter, pager)
        except Exception as Exp:
            print(Exp)
            return False 
        
    def deletecuepointsFromEntry(self,cueList):
        
        try:
            for i in range(0,cueList.totalCount):
                self.client.cuePoint.cuePoint.delete(cueList.objects[i].id)
        except:
            return False
                 
            
        
        
        