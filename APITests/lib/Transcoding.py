from KalturaClient.Plugins.Core import *


class Transcoding():
    
    def __init__(self,client,transcodingProfileName,transcodingProfileID=None):
        self.client = client
        self.transcodingProfileName = transcodingProfileName
        self.transcodingProfileID = transcodingProfileID
        


    def getTranscodingProfileIDByName(self,transcodingProfileName):
        transfilter = KalturaConversionProfileFilter()
        transfilter.advancedSearch = None
        transfilter.nameEqual = transcodingProfileName
        pager = None
        result = self.client.conversionProfile.list(transfilter, pager)
               
        if result.totalCount!=0:
            return result.objects[0].id 
        else:
            return None 
    
    # flavorsIds - send as string with comma seperate between ID's
    # typeint = send 0 for Media, 1 for live stream
    def addTranscodingProfile(self,typeint,flavorsIds,defaultEntryId=None,isNegative=False):
        if self.transcodingProfileID == None:
            conversionProfile = KalturaConversionProfile()
            conversionProfile.status = KalturaConversionProfileStatus.ENABLED
            transcodingType = {0:KalturaConversionProfileType.MEDIA,
                               1:KalturaConversionProfileType.LIVE_STREAM }
            conversionProfile.type = transcodingType[typeint]
            conversionProfile.name = self.transcodingProfileName
            conversionProfile.systemName = self.transcodingProfileName
            conversionProfile.description = self.transcodingProfileName
            conversionProfile.flavorParamsIds = flavorsIds
            if defaultEntryId != None:
                conversionProfile.defaultEntryId = defaultEntryId
            
            try:
                return self.client.conversionProfile.add(conversionProfile)
            except Exception as exp:
                if isNegative:
                    return exp
                else:
                    return False         
        else:
            return self.transcodingProfileID
    
    def deleteTranscodingProfile(self,profileId):
        try:
            result = self.client.conversionProfile.delete(profileId)
            
        except:
            print('problem with deleting conversion profile')
   
    # change intermediate flavor handling 
    # to Delete send in act='del' for readybehavior send act='ready'     
    def EditConversionProfileFlavors(self,flavorsIds,profileId,act='del'):
        conversionProfileAssetParams = KalturaConversionProfileAssetParams()
        arrFlavors = flavorsIds.split(',')
        for item in arrFlavors:
            if act=='del':
                conversionProfileAssetParams.deletePolicy = KalturaAssetParamsDeletePolicy.DELETE
            elif act=='ready':
                conversionProfileAssetParams.readyBehavior = KalturaFlavorReadyBehaviorType.REQUIRED
                
            self.client.conversionProfileAssetParams.update(profileId, item, conversionProfileAssetParams)

    #Moran.Cohen
    # Create new ConversionProfile if there is no exist with same name
    def CreateConversionProfileFlavors(self,client,CF_Name,flavorsIds):
        try:
            Transobj = Transcoding(client, CF_Name)
            CloudtranscodeId = Transobj.getTranscodingProfileIDByName(CF_Name)
            if CloudtranscodeId == None:
                CloudtranscodeId = Transobj.addTranscodingProfile(1, flavorsIds)
                if isinstance(CloudtranscodeId, bool):
                    print('Error with creating conversion profile')
                    return False
                print('Creating new conversion profile = ' + str(CloudtranscodeId.id))
                CloudtranscodeId = CloudtranscodeId.id
            return CloudtranscodeId
        except Exception as err:
            print(err)
            print('Error with creating conversion profile')
            return False
        
        
        