from KalturaClient.Plugins.Core import *

#===============================================================================
# class name: userRole
# Desc: this class treat user Roles methods
#===============================================================================

class userRole:
    
    def __init__(self,client):
        self.client = client
    
    #===========================================================================
    # parameters:
    # roleStatus - send int 0-2 as in statusLst
    # rolePermissions - send the permissions string separate with "," for example - "KMC_ACCESS,KMC_READ_ONLY,BASE_USER_SESSION_PERMISSION"
    #===========================================================================
        
    def AddUserRole(self, roleName, roleSysName, roleDesc, roleStatus, rolePermissions, isNegative=False):
        uRole = KalturaUserRole()
        uRole.name = roleName
        uRole.systemName = roleSysName
        uRole.description = roleDesc
        statusLst = {0:KalturaUserRoleStatus.ACTIVE,
                     1:KalturaUserRoleStatus.BLOCKED,
                     2:KalturaUserRoleStatus.DELETED}
        uRole.status = statusLst[roleStatus]
        uRole.permissionNames = rolePermissions
        uRole.tags = "kmc"
        try:
            result = self.client.userRole.add(uRole)
        except Exception as exp:
            print((str(exp)))
            if isNegative== True:
                result = exp
            else: 
                result = False
            
        return result
        
    def retUserRoleIdByName(self, RoleName): 
        
        filter = KalturaUserRoleFilter(nameEqual=RoleName)
        pager = None
        result = self.client.userRole.list(filter, pager)
        
        if isinstance(result,KalturaUserRole):
            return result.id
        else:
            return False
        
           
    
    def DeleteUserRole(self,userRoleId):
        try:
            result = self.client.userRole.delete(userRoleId)
        except:
            result = False
            
        return result
    
        
        