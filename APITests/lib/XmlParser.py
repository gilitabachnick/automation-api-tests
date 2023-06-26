#from pip._vendor.requests.packages.urllib3.util.connection import select
import os

try:
    import xml.etree.cElementTree as ETree
except ImportError:
    import xml.etree.ElementTree as ETree


# xml parser class new instance can start with xml file or string
class XmlParser():
    
    def __init__(self,xmlAsfile,xmlAsstring=None):
        pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'XML'))
        if xmlAsfile != None:
            self.xmltree = ETree.ElementTree(file=os.path.join(pth, xmlAsfile))
        else:
            self.xmltree = ETree.ElementTree(element=xmlAsstring)
            #self.xmltree = ETree.fromstring(xmlAsstring)
            
    
    # return certain parameter value from xml, bfindall=true when want to return all appearances of val, false would return the first appearance
    # xpath send with "." between nodes
    def retXMLvals(self,xpth,bfindall):
                
        if bfindall:
            retval = ""
            for elem in self.xmltree.iterfind('TextFieldName'):
                retval = retval + elem.tag,elem.text 
        else:
            try:
                elem = self.xmltree.find(xpth)
                retval = elem.tag,elem.text
            except:
                retval=None
            
        return retval
    
    def retCustomDataFieldVal(self,fieldName='Auto1'):
        if str(self.xmltree._root).find(fieldName)!=-1:
            splitedStr = str(self.xmltree._root).split('<'+fieldName+'>')
            retval = splitedStr[1].split('<')
            return retval[0]
        else:
            return None
    
    

        
        