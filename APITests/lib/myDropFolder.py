#===============================================================================
# from _tkinter import create
#===============================================================================
from KalturaClient.Plugins import DropFolder


class myDropFolder():
    
    def __init__(self,client, partnerId, folderName='autotest drop folder', folderDesc='autotest drop folder desc',):
        self.client     = client
        self.partnerId  = partnerId
        self.folderName = folderName
        self.folderDesc = folderDesc
        
        
    #===========================================================================
    # add drop folder for a publisher- adds a drop folder instance to admin site 
    # of the publisher.
    # parameters:
    #     foldertype - send number 0-6 (list at dictFolderType) for the folder type need to create    
    #===========================================================================
    def addDropFolder(self, folderType, folderDirectory=0, folderPth='/incoming/adi', filePolicy=0):
        
        drpFolder = DropFolder.KalturaDropFolder()
        drpFolder.partnerId = self.partnerId
        drpFolder.name = self.folderName
        drpFolder.description = self.folderDesc
        dictFolderType = {0:DropFolder.KalturaDropFolderType.LOCAL,
                          1:DropFolder.KalturaDropFolderType.FTP,
                          2:DropFolder.KalturaDropFolderType.SCP,
                          3:DropFolder.KalturaDropFolderType.SFTP,
                          4:DropFolder.KalturaDropFolderType.S3,
                          5:DropFolder.KalturaDropFolderType.FEED}
        
        drpFolder.type = dictFolderType[folderType]
        drpFolder.status = DropFolder.KalturaDropFolderStatus.ENABLED
        drpFolder.dc = folderDirectory
        drpFolder.path = folderPth
        drpFolder.fileSizeCheckInterval = 30
        drpFolder.fileDeletePolicy = DropFolder.KalturaDropFolderFileDeletePolicy.AUTO_DELETE_WHEN_ENTRY_IS_READY
        drpFolder.autoFileDeleteDays = 0
        drpFolder.fileHandlerType = DropFolder.KalturaDropFolderFileHandlerType.CONTENT
        drpFolder.fileHandlerConfig = DropFolder.KalturaDropFolderContentFileHandlerConfig()
        dictFolderPolicy = {0:DropFolder.KalturaDropFolderContentFileHandlerMatchPolicy.ADD_AS_NEW,
                            1:DropFolder.KalturaDropFolderContentFileHandlerMatchPolicy.MATCH_EXISTING_OR_ADD_AS_NEW,
                            2:DropFolder.KalturaDropFolderContentFileHandlerMatchPolicy.MATCH_EXISTING_OR_KEEP_IN_FOLDER}
         
        drpFolder.fileHandlerConfig.contentMatchPolicy = dictFolderPolicy[filePolicy]
        
        try:        
            return self.client.dropFolder.dropFolder.add(drpFolder)
        except:
            return False
        
    
    def deleteDropFolder(self, dropFolderId):
        try:
            return self.client.dropFolder.dropFolder.delete(dropFolderId)
        except Exception as exep:
            print((str(exep)))
            return False
            
        
        
        
        
        
        