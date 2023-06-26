'''
Moran.cohen
this class lib includes reusable functions for simulive tests ,stream types , API

'''

import _thread
import datetime
import os
import sys
import time
from subprocess import Popen, PIPE


from selenium.webdriver.common.keys import Keys

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)

from KalturaClient.Plugins.Schedule import *
from KalturaClient.Plugins.Metadata import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', 'NewKmc', 'lib'))
sys.path.insert(1,pth)


class Simulivecls():

    def __init__(self, client, logi, tearobj, isProd, publisherId, playerId):
        self.client = client
        self.logi = logi
        self.testTeardownclass = tearobj
        self.isProd = isProd
        self.publisherId = publisherId
        self.playerId = playerId


    '''
    Moran.Cohen
    This function add live stream object type simulive
    '''
    def LiveStream_Add(self, client, entry_name, entry_conversionProfileId, entry_adminTags="adminTags",entry_userId="admin", entry_entitledUsersPublish="Admins", entry_entitledUsersView="Admins",entry_entitledUsersEdit="WebcastingAdmin,Admins"):
        try:
            entry = KalturaLiveStreamEntry()
            entry.name = entry_name#"name"
            #k_type = KalturaEntryType.LIVE_STREAM
            entry.mediaType = KalturaMediaType.LIVE_STREAM_FLASH
            entry.recordStatus = KalturaRecordStatus.DISABLED
            entry.sourceType = KalturaSourceType.LIVE_STREAM
            entry.conversionProfileId = entry_conversionProfileId#30162
            entry.adminTags = entry_adminTags#"adminTags"
            entry.explicitLive = KalturaNullableBoolean.FALSE_VALUE
            entry.userId = entry_userId#'admin'
            entry.entitledUsersPublish = entry_entitledUsersPublish#'Admins'
            entry.entitledUsersView = entry_entitledUsersView#'Admins'
            entry.entitledUsersEdit =entry_entitledUsersEdit# 'WebcastingAdmin,Admins'
            entry.recordingOptions = KalturaLiveEntryRecordingOptions()
            entry.recordingOptions.shouldCopyEntitlement = KalturaNullableBoolean.TRUE_VALUE
            entry.recordingOptions.shouldMakeHidden = KalturaNullableBoolean.TRUE_VALUE
            live_stream_entry = entry
            source_type = KalturaSourceType.LIVE_STREAM
            object_liveStream = client.liveStream.add(live_stream_entry, source_type)
            return object_liveStream
        except Exception as err:
            print(err)
            return False

    '''
    Moran.Cohen
    This function updates metadata_profile_id to entry - service metadata.add
    '''
    def Metadata_Add(self, client, metadata_profile_id,entry_id,xml_data=None):
        try:
            #metadata_profile_id = 18242
            object_type = KalturaMetadataObjectType.ENTRY
            #object_id = object_liveStream.id
            if xml_data==None:
                xml_data = '<metadata>\
                    <SlidesDocEntryId></SlidesDocEntryId>\
                    <IsKwebcastEntry>1</IsKwebcastEntry>\
                </metadata>'

            object_metadata = client.metadata.metadata.add(metadata_profile_id, object_type, entry_id, xml_data)
            return object_metadata

        except Exception as err:
            print(err)
            return False



    '''
    Moran.Cohen
    This function set KS with  privileges and user_id
    '''
    def session_setKs(self, client, UserSecret,partner_id,privileges,user_id):
        try:
            secret = UserSecret
            #user_id = 'kmsAdminServiceUser'
            k_type = KalturaSessionType.ADMIN
            #partner_id = PublisherID
            expiry = None
            #privileges = 'disableentitlement'

            object_session = client.session.start(secret, user_id, k_type, partner_id, expiry, privileges)
            client.setKs(object_session)
            return client
        except Exception as err:
            print(err)
            return False

    '''
    Moran.Cohen
    This function add ScheduleEvent with the following params
    '''
    def ScheduleEvent_Add(self, client, object_id, schedule_event_sourceEntryId, schedule_event_startDate,
                      schedule_event_endDate,schedule_event_summary,schedule_event_tags="simulive",schedule_event_organizer="adminGroup",preStartEntryId=None,postEndEntryId=None,isContentInterruptible=None):
        try:
            self.logi.appendMsg('INFO - Going to Add ScheduleEvent:')
            schedule_event = KalturaLiveStreamScheduleEvent()
            schedule_event.templateEntryId = object_id
            schedule_event.sourceEntryId = schedule_event_sourceEntryId
            schedule_event.startDate = schedule_event_startDate
            schedule_event.endDate = schedule_event_endDate#schedule_event.startDate + sessionEndOffset * 60  # 1675243980
            schedule_event.recurrenceType = KalturaScheduleEventRecurrenceType.NONE
            schedule_event.summary = schedule_event_summary
            schedule_event.tags = schedule_event_tags#"simulive"
            schedule_event.organizer = schedule_event_organizer#"adminGroup"
            if preStartEntryId!=None:
                schedule_event.preStartEntryId = preStartEntryId
                self.logi.appendMsg('INFO - schedule_event.preStartEntryId = ' + str(schedule_event.preStartEntryId))
            if postEndEntryId!= None:
                schedule_event.postEndEntryId = postEndEntryId
                self.logi.appendMsg('INFO - schedule_event.postEndEntryId = ' + str(schedule_event.postEndEntryId))
            if isContentInterruptible!= None:
                schedule_event.isContentInterruptible = isContentInterruptible
                self.logi.appendMsg('INFO - schedule_event.isContentInterruptible = ' + str(schedule_event.isContentInterruptible))

            object_scheduleEvent = client.schedule.scheduleEvent.add(schedule_event)

            self.logi.appendMsg('INFO - schedule_event.id = ' + str(schedule_event.id))
            self.logi.appendMsg('INFO - schedule_event.sourceEntryId = ' + str(schedule_event.sourceEntryId))
            self.logi.appendMsg('INFO - schedule_event.startDate = ' + str(datetime.datetime.fromtimestamp(schedule_event.startDate).strftime('%Y-%m-%d %H:%M:%S')))
            self.logi.appendMsg('INFO - schedule_event.endDate = ' + str(datetime.datetime.fromtimestamp(schedule_event.endDate).strftime('%Y-%m-%d %H:%M:%S')))

            return object_scheduleEvent
        except Exception as err:
            print(err)
            return False

    '''
   Moran.Cohen
   This function creates simulive entry
   '''
    def Simulive_Add(self, client,UserSecret,partner_id, entry_name, entry_conversionProfileId,metadata_profile_id,schedule_event_sourceEntryId,schedule_event_summary,schedule_event_startDate=None,schedule_event_endDate=None,sessionEndOffset=5,preStartEntryId=None,postEndEntryId=None,isContentInterruptible=None):
        try:
            if schedule_event_startDate == None:
                schedule_event_startDate = time.time()
                schedule_event_endDate = schedule_event_startDate + sessionEndOffset * 60  # 1675243980
            else:
                if schedule_event_endDate ==None:
                    schedule_event_endDate = schedule_event_startDate + sessionEndOffset * 60  # 1675243980

            object_liveStream=self.LiveStream_Add(client=client,entry_name=entry_name,entry_conversionProfileId=entry_conversionProfileId)
            if object_liveStream==False:
                self.logi.appendMsg("FAIL - LiveStream_Add")
            object_metadata=self.Metadata_Add(client=client,metadata_profile_id=metadata_profile_id,entry_id=object_liveStream.id)
            if object_metadata == False:
                self.logi.appendMsg("WARNING - Metadata_Add")
            object_client=self.session_setKs(client=client,UserSecret=UserSecret,partner_id=partner_id,privileges='disableentitlement',user_id='kmsAdminServiceUser')
            if object_client == False:
                self.logi.appendMsg("FAIL - session_setKs")
            object_scheduleEvent=self.ScheduleEvent_Add(client=object_client, object_id=object_liveStream.id, schedule_event_sourceEntryId=schedule_event_sourceEntryId, schedule_event_startDate=schedule_event_startDate,schedule_event_endDate=schedule_event_endDate,schedule_event_summary=schedule_event_summary,schedule_event_tags="simulive",schedule_event_organizer="adminGroup",preStartEntryId=preStartEntryId,postEndEntryId=postEndEntryId,isContentInterruptible=isContentInterruptible)
            if object_scheduleEvent == False:
                self.logi.appendMsg("FAIL - ScheduleEvent_Add")
            self.logi.appendMsg("PASS - ScheduleEvent_Add from entry_id = " + str(object_liveStream.id) + " , scheduleEvent_id" +  str(object_scheduleEvent.id))
            return True,object_liveStream.id
        except Exception as err:
            print(err)
            return False