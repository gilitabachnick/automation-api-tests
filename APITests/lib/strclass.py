#from pip._vendor.requests import structures

class strclass():
    
    def __init__(self,str):
        self.str = str
 
    # this method make multiple replace in string
    #  the string to change = self.str
    # strToReplace - the strings to change separate with , example: 'do,while,if'
    # newstr - the new strings to put instead, example: 'where,for,else'
    def multipleReplace(self,strToReplace,newstr):
        
        oldarr = strToReplace.split(',')
        newarr = newstr.split(',')
        for i in range (0,len(oldarr)-1):
            self.str = self.str.replace(oldarr[i], newarr[i])
        return self.str   
            
        