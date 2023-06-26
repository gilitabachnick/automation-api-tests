###################################################
#                                                 #
# this class uses user -2 permissions             #
# for now allowed only on testing                 #
# environment.                                    #
# uses only for admin side settings prerun        #
#                                                 #
###################################################
import os

import ClienSession
import Config
# ===============================================================================
# from KalturaClient.Plugins import SystemPartner
# ===============================================================================
from KalturaClient.Plugins import EmailNotification, SystemPartner
from KalturaClient.Plugins import EventNotification
from KalturaClient.Plugins.Drm import *


class AdminSettings():
    # creates client session for user -2
    def __init__(self,env='testing',userId=None, impersonateID=None):
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'ini'))
        self.env = env
        if env=='testing':
            inifile =  Config.ConfigFile(os.path.join(pth, 'TestingParams.ini'))
        else:
            inifile = Config.ConfigFile(os.path.join(pth, 'ProdParams.ini')) 
        
        self.PublisherID = -2
        self.ServerURL = inifile.RetIniVal('Environment', 'ServerURL')
        self.UserSecret = inifile.RetIniVal('Environment','AdminSecret')
        self.PartnerId = inifile.RetIniVal('Environment','PublisherID')
        mySess = ClienSession.clientSession(self.PublisherID,self.ServerURL,self.UserSecret,userId, impersonateID=impersonateID )
        try:
            self.client = mySess.OpenSession()
        except Exception as Exp:
            print(Exp)
        self.client.partner_id = self.PartnerId
    
    # this method searches for a drm profile by it name and return the drm profile ID if exist, 0 if not.
    def drmprofileExsistByname(self,profileName):
        filter = KalturaDrmProfileFilter()
        filter.nameLike = profileName
        pager = None
        rc = self.client.drm.drmProfile.list(filter, pager)
        if rc.totalCount>0:
            return rc.objects[0].id
        else:
            return 0
        
    # intdrmProfileType 0-2 send the number for the type of profile needed the default is PLAY_READY    
    def createDrmProfile(self,partnerId,profileName,intdrmProfileType=0):
        # if profile exist delete it and recreate it
        rc = self.drmprofileExsistByname(profileName)
        if rc != 0:
            self.deleteDrmProfile(rc)
        # create the DRM profile    
        drmProfile = KalturaDrmProfile()
        drmProfile.partnerId = partnerId 
        drmProfile.name = profileName
        drmProfile.description = 'DRM profile for automation tests'
        providertype = {0:KalturaDrmProviderType.PLAY_READY,
                        1:KalturaDrmProviderType.WIDEVINE,
                        2:KalturaDrmProviderType.CENC}   #3:KalturaDrmProviderType.FAIRPLAY
                        
        drmProfile.provider = providertype[intdrmProfileType]
        drmProfile.status = KalturaDrmProfileStatus.ACTIVE
        if self.env=='testing':
            if intdrmProfileType==0:
                drmProfile.licenseServerUrl = 'http://192.168.193.48/playready/rightsmanager.asmx'
            else:
                drmProfile.licenseServerUrl = 'http://qa-udrm.dev.kaltura.com'
          
        else:
            if intdrmProfileType==0:
                drmProfile.licenseServerUrl = 'https://playreadylicense.kaltura.com/rightsmanager.asmx'
            else:
                drmProfile.licenseServerUrl = 'https://udrm.kaltura.com'
        
        self.client.requestConfiguration['partnerId']=partnerId
        
        try:
            return self.client.drm.drmProfile.add(drmProfile)
        except:
            return False
        
    
    def drmPolicy(self,partnerID,provider=0):
        drmPolicy = KalturaDrmPolicy()
        drmPolicy.partnerId = partnerID
        drmPolicy.name = "debug_msl150_vmguid_" + str(partnerID)
        drmPolicy.systemName = "debug_msl150_vmguid_" + str(partnerID)
        drmPolicy.provider = KalturaDrmProviderType.CENC
        drmPolicy.status = KalturaDrmPolicyStatus.ACTIVE
        drmPolicy.scenario = KalturaDrmLicenseScenario.PROTECTION
        drmPolicy.licenseType = KalturaDrmLicenseType.PERSISTENT
        drmPolicy.licenseExpirationPolicy = KalturaDrmLicenseExpirationPolicy.FIXED_DURATION
        try:
            result = self.client.drm.drmPolicy.add(drmPolicy)
        except Exception as exep:
            if exep.code == 'DRM_POLICY_DUPLICATE_SYSTEM_NAME':
                result = self.getDRMpolicy(partnerID, provider)
            else:
                return exep.code
        return result  
    
    def getDRMpolicy(self,partnerID, provider=0):
        drmProvider = {0:KalturaDrmProviderType.PLAY_READY,
                       1:KalturaDrmProviderType.CENC}
        filter = KalturaDrmPolicyFilter()
        filter.partnerIdIn = partnerID
        filter.providerEqual = drmProvider[provider]
        pager = None
        result = self.client.drm.drmPolicy.list(filter, pager)
        return result

    def retUdrmPolicy(self,drmpolicyId):
        drmPolicyId = drmpolicyId
        try:
            return(self.client.drm.drmPolicy.get(drmPolicyId))
        except:
            return False
        
    def updateDeliveryProfile(self,partnerId, deliveryProfiles=r'{"sl":[891],"mpegdash":[831]}'):
        configuration = SystemPartner.KalturaSystemPartnerConfiguration()
        try:
            configuration.deliveryProfileIds = deliveryProfiles  
            return self.client.systemPartner.systemPartner.updateConfiguration(partnerId, configuration)
        except:
            return 'exist'
                
    def deleteDrmProfile(self,profileId):
        try:
            result = self.client.drm.drmProfile.delete(profileId)
        except Exception as exep:
            if exep.code == 'INVALID_OBJECT_ID':
                return 'not exist'
            else:
                return exep.code
            
    def deleteDrmPolicy(self,drmPolicyId):
        try:
            return self.client.drm.drmPolicy.delete(drmPolicyId)
        except:
            return False    
        
    
    def CreateEmailTemplate(self, name, sysname, desc, timestmp=None):
       
        NotificationTemplate = EmailNotification.KalturaEmailNotificationTemplate(
            name = name,
            systemName = sysname,
            description = desc,
            type = EventNotification.KalturaEventNotificationTemplateType.EMAIL,
            automaticDispatchEnabled = 1,
            manualDispatchEnabled = 0,
            
            eventType = EventNotification.KalturaEventNotificationEventType.OBJECT_CHANGED,
            eventObjectType = EventNotification.KalturaEventNotificationEventObjectType.ENTRY,
            eventConditions = [
                EventNotification.KalturaEventFieldCondition(not_=0, field=KalturaEvalBooleanField(code='$scope->getEvent()->getObject() instanceof entry && in_array(entryPeer::STATUS, $scope->getEvent()->getModifiedColumns()) && $scope->getEvent()->getObject()->getStatus() == entryStatus::READY'))
            ],
            contentParameters = [EmailNotification.KalturaEmailNotificationParameter(key='from_email',description="Sender email",value = KalturaEvalStringField(code ='kConf::get("partner_notification_email")')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='from_name',description="Sender name",value = KalturaEvalStringField(code ='kConf::get("partner_notification_name")')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='entry_id',description="Entry ID",value = KalturaEvalStringField(code ='(($scope->getObject() instanceof entry) && ($scope->getObject()->getIsTemporary()) && ($scope->getObject()->getReplacedEntryId()))? $scope->getObject()->getReplacedEntryId():$scope->getObject()->getId()')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='entry_name',description="Entry Name",value = KalturaEvalStringField(code ='(($scope->getObject() instanceof entry) && ($scope->getObject()->getIsTemporary()) && ($scope->getObject()->getReplacedEntryId()))? entryPeer::retrieveByPK($scope->getObject()->getReplacedEntryId())->getName():$scope->getObject()->getName()')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='creator_name',description="Entry creator name",value = KalturaEvalStringField(code ='$scope->getEvent()->getObject()->getkuser()->getFirstName() . '' '' . $scope->getEvent()->getObject()->getkuser()->getLastName()')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='creator_id',description="Entry creator ID",value = KalturaEvalStringField(code ='$scope->getEvent()->getObject()->getKuserId()')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='creator_email',description="Entry creator email",value = KalturaEvalStringField(code ='$scope->getEvent()->getObject()->getkuser()->getEmail()')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='owner_name',description="Account owner name",value = KalturaEvalStringField(code ='!is_null(entryPeer::retrieveByPk($scope->getEvent()->getObject()->getEntryId())) ? entryPeer::retrieveByPk($scope->getEvent()->getObject()->getEntryId())->getPartner()->getPartnerName() : \'''\'')),
                                 EmailNotification.KalturaEmailNotificationParameter(key='owner_email',description="Account owner email",value = KalturaEvalStringField(code ='!is_null(entryPeer::retrieveByPk($scope->getEvent()->getObject()->getEntryId())) ? entryPeer::retrieveByPk($scope->getEvent()->getObject()->getEntryId())->getPartner()->getAdminEmail() : \'''\'')),
            ],
           
            format = EmailNotification.KalturaEmailNotificationFormat.HTML,
            subject = 'Entry is Ready for Publishing: {entry_name}/ ID: {entry_id}',
            body = 'Entry Readt ID: {entry_id} , Date: ' + timestmp,
            fromEmail = '{from_email}',
            fromName = '{from_name}',
            to = EmailNotification.KalturaEmailNotificationStaticRecipientProvider([EmailNotification.KalturaEmailNotificationRecipient(KalturaStringValue(value='autokalt@gmail.com'), KalturaStringValue(value='autokalt'))])
          
        )
        
        try:
            result = self.client.eventNotification.eventNotificationTemplate.add(NotificationTemplate)
        except Exception as exp:
           result = exp 
           return result
        
        # update to automatic dispatch   
        #=======================================================================
        # try:
        #     result = self.client.eventNotification.eventNotificationTemplate.update(result.id, NotificationTemplate)
        # except Exception as exp:
        #    result = exp
        #=======================================================================
           
        return result
    
    def searchEventTemplateBysysName(self, eventSysName):
        filter = EventNotification.KalturaEventNotificationTemplateFilter()
        filter.systemNameEqual = eventSysName
        pager = None
        result = self.client.eventNotification.eventNotificationTemplate.list(filter, pager)
        if result.totalCount!=0:
            return result.objects[0].id
        else:
            return False
        
        
    
    def DeleteTemplateNotification(self, eventId):
        try :
            result = self.client.eventNotification.eventNotificationTemplate.delete(eventId)
        except Exception as exp:
            result = exp
           
        return result
    
    
    
    
    
    
    
    
   
        
        
        
        
        
        