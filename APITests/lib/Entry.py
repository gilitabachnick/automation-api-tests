#from pip._vendor.requests.packages.urllib3.util.connection import select
# from pip._vendor.requests.packages.urllib3.util.connection import select
import os
import time

from KalturaClient.Plugins import Document
from KalturaClient.Plugins.Metadata import *

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
# import imp
# imp.load_source('accessControl', os.path.join(pth ,'accessControl.py'))

from importlib.machinery import SourceFileLoader
SourceFileLoader('accessControl', os.path.join(pth ,'accessControl.py'))

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


class Entry:
    # intentryType - choose the number as mantioned in AddEntry method (entryTypeOptions)
    def __init__(self,client, entryName, entryDesc, entryTags, entryAdminTag, entryCategory, intentryType, objfile=None, conversionProfileId=None, accessControlId=None):
        self.client           = client
        self.entryName        = entryName
        self.entryDesc        = entryDesc
        self.entryTags        = entryTags
        self.entryAdminTag    = entryAdminTag
        self.entryCategory    = entryCategory
        self.intentryType    = intentryType
        self.conversionProfileId = conversionProfileId
        self.accessControlId = accessControlId
        
        if objfile!=None:
            self.objfile     = objfile
            
        if conversionProfileId!=None:
            self.conversionProfileId = conversionProfileId
    
    #Add entry
    def AddEntry(self, creatorId=None, ownerId=None):
        entryTypeOptions = {0 : KalturaEntryType.MEDIA_CLIP,
                            1 : KalturaEntryType.AUTOMATIC,
                            2 : KalturaEntryType.DATA,
                            3 : KalturaEntryType.DOCUMENT,
                            4 : KalturaEntryType.EXTERNAL_MEDIA,
                            5 : KalturaEntryType.LIVE_CHANNEL,
                            6 : KalturaEntryType.LIVE_STREAM,
                            7 : KalturaEntryType.MIX,
                            8 : KalturaEntryType.PLAYLIST}
        
        entry = KalturaMediaEntry()
        entry.name = self.entryName
        entry.description = self.entryDesc
        if self.entryTags!=None:
            entry.tags = self.entryTags
            
        if self.entryAdminTag!=None:
            entry.adminTags = self.entryAdminTag
        
        if self.entryCategory!=None:    
            entry.categories = self.entryCategory
            
        if self.intentryType not in (0,8):
            intentryType = None    
        else:
            intentryType = entryTypeOptions[self.intentryType]
        entry.mediaType=KalturaMediaType.VIDEO
        
        if self.conversionProfileId!=None:
            entry.conversionProfileId = self.conversionProfileId
            
        if self.accessControlId!= None:
            entry.accessControlId = self.accessControlId
            
        if creatorId != None:
            entry.creatorId = creatorId
        if ownerId != None:
            entry.userId = ownerId
        
        return self.client.baseEntry.add(entry, intentryType)
   
    #Add stream entry
    # recordStatus - send 0 for disable, 1 for append, 2 for per_session
    # dvrStatus - send 0 for disable, 1 for enable
    # explicitLive - send 0 for disable, 1 for enable
    def AddEntryLiveStream(self, creatorId=None, ownerId=None, recordStatus=0, dvrStatus=0, dvrWindow=120,explicitLive=0):
        entryTypeOptions = {0 : KalturaEntryType.LIVE_CHANNEL,
                            1 : KalturaEntryType.LIVE_STREAM}
        
        recordStatusOptions = {0 : KalturaRecordStatus.DISABLED,
                               1 : KalturaRecordStatus.APPENDED,
                               2 : KalturaRecordStatus.PER_SESSION}
        
        dvrStatusOptions = {0 : KalturaDVRStatus.DISABLED,
                            1 : KalturaDVRStatus.ENABLED}
                           
        
        entry = KalturaLiveStreamEntry()
        
        entry.name = self.entryName
        entry.description = self.entryDesc
        if self.entryTags!=None:
            entry.tags = self.entryTags
            
        if self.entryAdminTag!=None:
            entry.adminTags = self.entryAdminTag
        
        if self.entryCategory!=None:    
            entry.categories = self.entryCategory
            
        if self.intentryType not in (0,1):
            intentryType = None    
        else:
            intentryType = entryTypeOptions[self.intentryType]
        entry.mediaType=KalturaMediaType.LIVE_STREAM_FLASH
        
        if self.conversionProfileId!=None:
            entry.conversionProfileId = self.conversionProfileId
            
        if self.accessControlId!= None:
            entry.accessControlId = self.accessControlId
            
        if creatorId != None:
            entry.creatorId = creatorId
        if ownerId != None:
            entry.userId = ownerId
            
        entry.sourceType = KalturaSourceType.LIVE_STREAM
        if dvrStatus!=None:
            entry.dvrStatus = dvrStatusOptions[dvrStatus]
        if  recordStatus!=None:
            entry.recordStatus = recordStatusOptions[recordStatus]

        if dvrStatus==1:
            if dvrWindow!=None:
                entry.dvrWindow = dvrWindow

        if explicitLive == 1:
            entry.explicitLive = explicitLive
        
        try:
            return self.client.liveStream.add(entry, entry.sourceType)
        except Exception as exp:
            print(exp)
            return False
    
    # add documnet entry
    def AddDocumentEntry(self, uploadTokenId, creatorId=None, ownerId=None):
        #print dir(Document)
        documentEntry = Document.KalturaDocumentEntry()
        documentEntry.name = self.entryName
        documentEntry.description = self.entryDesc
        documentEntry.creatorId = creatorId
        #documentEntry.type = Document.KalturaDocumentType.DOCUMENT
        documentEntry.type = KalturaEntryType.DOCUMENT
        documentEntry.documentType = Document.KalturaDocumentType.DOCUMENT
        documentEntry.groupId = None
        documentEntry.conversionProfileId = self.conversionProfileId 
        documentEntry.templateEntryId = None
        #documentEntry.displayInSearch = Document.KalturaEntryDisplayInSearchType.SYSTEM
        try:
            result = self.client.document.documents.addFromUploadedFile(documentEntry, uploadTokenId)
            #result = self.client.document.addFromUploadedFile(documentEntry, uploadTokenId)
        except Exception as exp:
            result = False
            print(exp)
            
        return result
    
    # retrieve document entry
    def getDocEntry(self, entryId, version=None):
        try:
            result = self.client.document.documents.get(entryId, version)
        except Exception as exp:
            print(exp)
            result = False
            
        return result

        
        
    #Upload file
    def UploadFileToNewEntry(self,entryObj,TokenOnly=False):
        # add Token
        uploadTokenObj = KalturaUploadToken()
        uploadToken = self.client.uploadToken.add(uploadTokenObj)
        try:
            result = self.client.uploadToken.upload(uploadToken.id,self.objfile, None,None,None)
        except Exception as EXP:
            print(EXP)
        # add the file
        if not TokenOnly:
            resource = KalturaUploadedFileTokenResource()
            resource.token = uploadToken.id
            result = self.client.media.addContent(entryObj.id, resource)
            
        return result
    
    def AddNewEntryWithFile(self,timeoutSec=300):
        try:
            entry = self.AddEntry()
            Tokken = self.UploadFileToNewEntry(entry)
            finit = self.WaitForEntryReady(entry.id,timeoutSec)
            if isinstance(finit, bool):
                if finit:
                    return entry
                else:
                    return False
            else:
                return 'error'
        except Exception as Exp:
            print(Exp)
            return 'error'
                    
    # verify entry status ready 
    def isEntryReady(self,entryid):
        result = self.client.baseEntry.get(entryid,None)
        if result.status.value==KalturaEntryStatus.READY:
            return True
        else:
            return False
    
    # wait for entry to get the status ready with given timeout     
    def WaitForEntryReady(self,entryid,timeOut):
        startTime = time.perf_counter()
        bEntryReady = False
        print('Waiting for entry status=Ready...')
        while (time.perf_counter()<=startTime+ timeOut and not bEntryReady):
            result = self.client.baseEntry.get(entryid,None)
            time.sleep(1)
            if result.status.value==KalturaEntryStatus.READY:
                bEntryReady = True
            if result.status.value==KalturaEntryStatus.ERROR_CONVERTING or result.status.value==KalturaEntryStatus.ERROR_IMPORTING:
                return 'error'
        if result.status.value==KalturaEntryStatus.PRECONVERT:
            return 'timeout'
        return bEntryReady
    
    # check if entry exist
    def isEntryExsit(self,entryid):
        try :
            result = self.client.baseEntry.get(entryid,None)
            retId = result.id
            if retId == entryid:
                return True
        except : 
            return False 
        
    def getEntry(self, entryId, version = None):
        
        try:
            result = self.client.baseEntry.get(entryId, version)
        except Exception as exp:
            print(exp)
            result = False
            
        return result
    
    # retrieve list of entries with the same name
    def getEntryListByName(self, entryName, statusFilter=None, createdAtGreaterThanOrEqualFilter=None):
        Kalfilter = KalturaBaseEntryFilter()
        if entryName!=None:
            Kalfilter.nameLike = entryName
        if statusFilter!=None:
            Kalfilter.statusEqual = KalturaEntryStatus.NO_CONTENT
        if createdAtGreaterThanOrEqualFilter!=None:
            Kalfilter.createdAtGreaterThanOrEqual = createdAtGreaterThanOrEqualFilter
        pager = None
        try:
            return self.client.baseEntry.list(Kalfilter, pager)
        except:
            return False 
        
    
    def DeleteEntry(self,entryid):
        if self.isEntryExsit(entryid):
            self.client.baseEntry.delete(entryid)
            result = self.isEntryExsit(entryid)
            if not result:
                return True
            else:
                return False
        else:
            print(('entry',entryid, 'does not exist for this partner'))
            return True
        
     
    # this def retrieve a the list of flavors of an entry     
    def flavorList(self,entryId):
        Kalfilter = KalturaAssetFilter()
        Kalfilter.entryIdEqual = entryId
        pager = None
        try:
            return self.client.flavorAsset.list(Kalfilter, pager)
        except Exception as exp:
            print(exp)
            return False


    # self.entryCategory - should be send as string (the name of the categories to set) seperated by comma
    def updateEntryCategoryandAccessControl(self,entryId):

        baseEntry = KalturaBaseEntry()
        baseEntry.categories = self.entryCategory
        baseEntry.accessControlId = self.accessControlId
        return self.client.baseentry.update(entryId, baseEntry)




    def prettyPrint(self):
        print(("Entry params",self.client,self.entryName,self.entryDesc,self.entryTags,self.entryAdminTag,self.entryCategory,self.intentryType))

    # Moran.cohen
    # This function creates playlist manual with list of entries in playlistContent
    # playlistName = The name of the playlist
    # playlistContent =  set list of entries on manual playlist for example playlistContent="0_es9j90do,0_svkof2p6"
    def CreatePlaylistManual(self, playlistContent):
        try:
            # Create playlist manual
            playlist = KalturaPlaylist()
            playlist.name = self.entryName
            playlist.playlistType = KalturaPlaylistType.STATIC_LIST
            update_stats = False
            Playlist_result = self.client.playlist.add(playlist, update_stats)
            # Update playlist
            id = Playlist_result.id
            playlist = KalturaPlaylist()
            playlist.playlistContent = playlistContent
            playlist.playlistType = KalturaPlaylistType.STATIC_LIST
            update_stats = False
            result = self.client.playlist.update(id, playlist, update_stats)
            return True,Playlist_result.id

        except Exception as err:
            print(err)
            return False,str(err)