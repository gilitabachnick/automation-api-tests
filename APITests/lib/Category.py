from KalturaClient.Plugins.Core import *


class category():
    
    def __init__(self, client):
        self.client = client
        
        
    def addCategory(self, parentId=None, categoryName='CategoryTest'):
        
        category = KalturaCategory()
        category.name = categoryName
        if parentId != None:
            category.parentId = parentId
             
        category.appearInList = KalturaAppearInListType.PARTNER_ONLY
        category.privacy = KalturaPrivacyType.ALL
        
        if parentId != None:
            category.privacyContext = 'public'
            category.inheritanceType = KalturaInheritanceType.INHERIT
            
        #category.defaultPermissionLevel =  KalturaCategoryUserPermissionLevel.MANAGER
        category.defaultOrderBy = None
        
        try:
            return self.client.category.add(category)
        except Exception as exp:
            print(exp)
            return False
             
    
    def movecategory(self,categoryId, moveToParentId):  
        try:
            return self.client.category.move(categoryId, moveToParentId)
        except Exception as exp:
            print(exp)
            return False
        
    # retrieve category by id   
    def getCategory(self,catId,notExist=False):
        try:
            return self.client.category.get(catId)
        except Exception as exp:
            if notExist:
                if exp.code == 'CATEGORY_NOT_FOUND':
                    return True
                else:
                    return False
            else:
                print(exp)
                return False
    # retrieve category by name
    def getCategoryByName(self,catName):
        filter = KalturaCategoryFilter()
        filter.fullNameEqual = catName
        pager = None
        try:
            result = self.client.category.list(filter, pager)
            result = result.objects[0].id
        except Exception as exp:
            print(exp)
            result = False
            
        return result
            
    
    
    def updateCategoryNamebyId(self, catId, newName):
        category = KalturaCategory()
        category.name = newName
        try:
            return self.client.category.update(catId, category)
        except Exception as exp:
            print(exp)
            return False
        
    def deleteCategory(self, catId):
        moveEntriesToParentCategory = KalturaNullableBoolean.TRUE_VALUE
        try:
            return self.client.category.delete(catId, moveEntriesToParentCategory)
            
        except Exception as exp:
            print(exp)
            return False
        