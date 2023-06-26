from KalturaClient import *
from KalturaClient.Plugins.Core import *
from KalturaClient.Plugins.Metadata import *
#from pip._vendor.requests.packages.urllib3.util.connection import select
import os
import time
import sys
import configparser
try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree
    
from xml.etree.ElementTree import QName


class CustomMetaData:
    
    def __init__(self,client):
        self.client = client
    
    # local class function 
    def GetEntityType(self, intEntityType):
        entiTypeOptions = {0 : KalturaMetadataObjectType.ENTRY,
                        1 : KalturaMetadataObjectType.CATEGORY,
                        2 : KalturaMetadataObjectType.USER,
                        3 : KalturaMetadataObjectType.PARTNER,
                        4 : KalturaMetadataObjectType.DYNAMIC_OBJECT,
                        5 : KalturaMetadataObjectType.ANNOTATION,
                        6 : KalturaMetadataObjectType.AD_CUE_POINT,
                        7 : KalturaMetadataObjectType.CODE_CUE_POINT,
                        8 : KalturaMetadataObjectType.THUMB_CUE_POINT,
                        }
        if intEntityType not in (0,8):
            return None
        else:
            return entiTypeOptions[intEntityType]
    
         
    # retrieve meta data for user id    
    def CustomMetaDataList(self):
        filter = KalturaMetadataFilter()
        filter.metadataProfileVersionGreaterThanOrEqual = None
        filter.metadataObjectTypeEqual = KalturaMetadataObjectType.ENTRY
        filter.statusEqual = KalturaMetadataStatus.VALID
        pager = None
        result = self.client.metadata.list(filter, pager)
        
        try:
            result = self.client.metadata.metadata.list(self.entityId)
        except Exception as exep:
            if  exep.code == 'METADATA_NOT_FOUND':
                return 'no mete data found'
            else:
                return 'exception occurred:',exep.code

    
    # retrieve metadata profile list    
    def GetMetaDataProfileListBYname(self, intEntityType, ProfileName):
        filter = KalturaMetadataProfileFilter()
        filter.metadataObjectTypeEqual = self.GetEntityType(intEntityType)
        filter.nameEqual = ProfileName
        pager = None
        return self.client.metadata.metadataProfile.list(filter, pager)
    
    
    # retrieve metadata profile ID by its name
    def retMetaDataProfileIDbyName(self,intEntityType, ProfileName):
        try:
            profileID = self.GetMetaDataProfileListBYname(intEntityType,ProfileName).objects[0].id
            return self.client.metadata.metadataProfile.delete(profileID)
        except:
            return 0
    
    
    # add custom metadata profile scheme
    # returns None if the status of the new profile is not active after 20 sec else return the profile object
    def AddCustomMetaDataProfile(self,xsd, mName='autotest', mSystemName='autotest',mDesc='automation test metadata'):
        
        ACTIVE = 1    
        DEPRECATED = 2    
        TRANSFORMING = 3
        
        metadataProfile = KalturaMetadataProfile()
        metadataProfile.metadataObjectType = KalturaMetadataObjectType.ENTRY
        metadataProfile.name = mName
        metadataProfile.systemName = mSystemName
        metadataProfile.description = mDesc
        metadataProfile.createMode = KalturaMetadataProfileCreateMode.KMC
        if xsd==None:  # default xsd data in project automation.xml
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'XML'))
            xsdData = open(os.path.join(pth, 'XSDfirst.xml')).read()
        else:
            xsdData = xsd
        #viewsData = '<layouts><layout id="KMC"></layout></layouts>'
        viewsData = 'KMC'
        try:
            result = self.client.metadata.metadataProfile.add(metadataProfile, xsdData, viewsData)
            # wait for profile status is ACTIVE
            startTime = time.perf_counter()
            timeOut = 20
            while (time.perf_counter() <= startTime+timeOut and result.getStatus().value != ACTIVE):
                time.sleep(1)
            # status was not changed to ACTIVE    
            if time.perf_counter()> startTime+timeOut:
                result = None
            
        except Exception as exep:
            if  exep.code == 'SYSTEM_NAME_ALREADY_EXISTS':
                result = 'exist'
            else:
                result = False
        
        return result
    
    # update custom metadata profile: 
    # if do not have the metadata profile ID, send None for metadataProfileId parameter and the profile name for metadataProfileName
    # else if profile Id is known send it in metadataProfileId and do not send metadataProfileName
    def UpdateCustomMetadataProfile(self,metadataProfileId,intEntityType=None,metadataProfileName=None,xsdData=None):
        
        ACTIVE = 1    
        DEPRECATED = 2    
        TRANSFORMING = 3
        
        if metadataProfileId==None: 
            metadataProfileId = self.retMetaDataProfileIDbyName(intEntityType, metadataProfileName)
            
        metadataProfile = KalturaMetadataProfile()
        metadataProfile.metadataObjectType = KalturaMetadataObjectType.ENTRY
        metadataProfile.createMode = KalturaMetadataProfileCreateMode.KMC
        if xsdData==None:  # default xsd data in project automation.xml
            pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'XML'))
            xsdData = open(os.path.join(pth, 'XSDsecond.xml')).read()
        else:
            xsdData = xsd
        
        viewsData = "KMC"
        result = self.client.metadata.metadataProfile.update(metadataProfileId, metadataProfile, xsdData, viewsData)
        # wait for profile status is ACTIVE
        startTime = time.perf_counter()
        timeOut = 20
        while (time.perf_counter()<=startTime+timeOut and result.getStatus().value != ACTIVE):
            time.sleep(1)
            # status was not changed to ACTIVE    
            if time.perf_counter()> startTime+timeOut:
                result = None
        return result
    
    # get metadata list by the metadata profile ID
    # return value - xml
    def GetMetadataListByEntryID(self,EntryId):
        filter = KalturaMetadataFilter()
        filter.metadataObjectTypeEqual = KalturaMetadataObjectType.ENTRY
        filter.objectIdEqual = EntryId
        pager = None
        result = self.client.metadata.metadata.list(filter, pager)
        return result
        
        
    
    # add custom meta data to entity type 
    # if do not have the metadata profile ID, send None for metadataProfileId parameter and the profile name for metadataProfileName
    # else if profile Id is known send it in metadataProfileId and do not send metadataProfileName
    def AddCustomMetaData(self,metadataProfileId,intEntityType,objectId,xmlData,metadataProfileName=None):
        # case only matadata profile name sent and no iD 
        if metadataProfileId==None: 
            metadataProfileId = self.retMetaDataProfileIDbyName(intEntityType, metadataProfileName)
        
        intEntityType = self.GetEntityType(intEntityType)
        try:
            result = self.client.metadata.metadata.add(metadataProfileId, intEntityType, objectId, xmlData)
        except Exception as exep:
            if  exep.code == 'METADATA_ALREADY_EXISTS':
                result = 'exist'
            else:
                result = 'exception occurred:',exep.code
        
        return result
    
    
    #def update custom metada 
    
    # delete metadata profile for known profile ID send it in 'profileID' parameter,
    # for unkownn profile id send it 'intEntityType' (0-8) and     'ProfileName'
    def DeleteMetaDataProfile(self,metadataProfileId,intEntityType=None, ProfileName=None):
        if metadataProfileId == None:
            metadataProfileId = self.retMetaDataProfileIDbyName(intEntityType, ProfileName)
        else:
            return self.client.metadata.metadataProfile.delete(metadataProfileId)
            
    
    
    def prettyPrint(self):
        print(('MetaData',self.client))
        