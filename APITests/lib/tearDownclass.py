class teardownclass():
    
    def __init__(self):
        self.cmdlist=[]
        self.objlist=[]
        self.lstcnt = 0
        
    def addTearCommand(self,obj,cmdAsstring):
        self.cmdlist.insert(self.lstcnt,cmdAsstring) 
        self.objlist.insert(self.lstcnt,obj)
        self.lstcnt = self.lstcnt + 1
        
    def exeTear(self):
        for index in reversed(self.cmdlist):
            print(('tear down: ' + index))
            try:
                eval('self.objlist[self.cmdlist.index(index)].' + index)
            except Exception as Exp:
                print(('Could not execute ' + index))
                print('this is the Exception: ' + str(Exp))

            
