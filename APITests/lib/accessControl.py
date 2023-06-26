import datetime
import pprint

from KalturaClient.Plugins.Drm import *


class accessControl():
    
    def __init__(self,client):
        self.client = client
        
    def getaccessControlIdBySysName(self,accessControlSysName):
        filter = KalturaAccessControlFilter()
        filter.systemNameIn = accessControlSysName
        pager = None
        try:
            result = self.client.accessControl.list(filter, pager)
            return result.objects[0].id
        except Exception as exp:
            return exp 
        
    
    
    def CreatAccessUDRMprofile(self,accName, accSysName, accDesc, drmPolicyID, dictPlayreadyPolicyIds, deliveryProfileIds, accIsDefault=0):
        accessControl = KalturaAccessControlProfile()  
        accessControl.name = accName
        accessControl.systemName = accSysName
        accessControl.description = accDesc
        accessControl.isDefault = accIsDefault  
        
        rulesArr = []
        
        # rule 1
        context1 = KalturaContextTypeHolder()
        context1.type = KalturaContextType.SERVE
        cond1 = KalturaDeliveryProfileCondition()
        deliveryProfileIntegerValues = []
        for deliveryProfileId in deliveryProfileIds.split(','):
            currentIntValue = KalturaIntegerValue()
            currentIntValue.value= deliveryProfileId
            deliveryProfileIntegerValues.append(currentIntValue)
            
        cond1.deliveryProfileIds = deliveryProfileIntegerValues
        cond1.not_ = True
        action1 = KalturaAccessControlLimitFlavorsAction()
        action1.flavorParamsIds = '251,561,241,261,331,341,351,361' 
        rule1 = KalturaRule()
        rule1.contexts = [context1]
        rule1.conditions = [cond1]
        rule1.actions = [action1]
        
        # rule 2
        cond2 = KalturaAuthenticatedCondition()
        privelage2 = KalturaStringValue()
        privelage2.value = "scenario_default"
        cond2.privileges = [privelage2]
        action2 = KalturaAccessControlDrmPolicyAction()
        action2.policyId = dictPlayreadyPolicyIds['default']           
        rule2 = KalturaRule()
        rule2.conditions = [cond2]
        rule2.actions = [action2]
        
        # rule 3
        cond3 = KalturaAuthenticatedCondition()
        privelage3 = KalturaStringValue()
        privelage3.value = "scenario_rental"
        cond3.privileges = [privelage3]
        action3 = KalturaAccessControlDrmPolicyAction()
        action3.policyId = dictPlayreadyPolicyIds['rental']            
        rule3 = KalturaRule()
        rule3.conditions = [cond3]
        rule3.actions = [action3]
        
        # rule 4
        cond4 = KalturaAuthenticatedCondition()
        privelage4 = KalturaStringValue()
        privelage4.value = "scenario_purchase"
        cond4.privileges = [privelage4]
        action4 = KalturaAccessControlDrmPolicyAction()
        action4.policyId = dictPlayreadyPolicyIds['purchase']           
        rule4 = KalturaRule()
        rule4.conditions = [cond4]
        rule4.actions = [action4]
        
        # rule 5
        cond5 = KalturaAuthenticatedCondition()
        privelage5 = KalturaStringValue()
        privelage5.value = "scenario_subscription"
        cond5.privileges = [privelage5]
        action5 = KalturaAccessControlDrmPolicyAction()
        action5.policyId = dictPlayreadyPolicyIds['subscription']            
        rule5 = KalturaRule()
        rule5.conditions = [cond5]
        rule5.actions = [action5]
        
        # rule 6
        context6 = KalturaContextTypeHolder()
        context6.type = KalturaContextType.PLAY
        action6 = KalturaAccessControlDrmPolicyAction()
        action6.policyId = drmPolicyID                      
        rule6 = KalturaRule()
        rule6.contexts = [context6]
        rule6.actions = [action6]    
        
        for i in range(1,7):
            rulesArr.append(eval('rule'+str(i)))
            
        accessControl.rules = rulesArr
        
        try:
            result = self.client.accessControlProfile.add(accessControl)
        except Exception as exep:
            if  exep.code == 'SYSTEM_NAME_ALREADY_EXISTS':
                result = 'exist'
            elif exep.code != 'SYSTEM_NAME_ALREADY_EXISTS':
                return exep
            else:
                pprint.pformat(exep)
                result = False
                #result = False
                 
        return result
    
    #Moran.Cohen
    # This function adds accessControl with Session Restriction(only ks admin can be played)
    def CreateAcessControlSessionRestriction(self,accName="AC_KalturaSessionRestriction_"):
        access_control = KalturaAccessControl()
        access_control.name = accName + str(datetime.datetime.now())
        access_control.restrictions = []
        access_control.restrictions.append(KalturaSessionRestriction()) 
        try:
            result = self.client.accessControl.add(access_control)
        except Exception as exep:
            if  exep.code == 'SYSTEM_NAME_ALREADY_EXISTS':
                result = 'exist'
            elif exep.code != 'SYSTEM_NAME_ALREADY_EXISTS':
                return exep
            else:
                pprint.pformat(exep)
                result = False
                #result = False
                 
        return result
    
    def deleteAccessControlProfile(self, accId):
        try:
            return self.client.accessControlProfile.delete(accId)
        except Exception as exp:
            print(exp)
            return False
    #Moran.Cohen
    #This function deletes access control    
    def deleteAccessControl(self, accId):
        try:
            return self.client.accessControl.delete(accId)
        except Exception as exp:
            print(exp)
            return False
        