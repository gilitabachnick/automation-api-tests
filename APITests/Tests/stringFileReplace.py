import os

import MyCsv


# Script that replaces text strings in a batch way on an original file
# The new strings to be replaced are provided by a CSV file with two columns: original string,new string 
# The process creates a new file with all the new strings replaced, does not make any changes on original

# Process that make the batch string replacement
# params: originalF: original file, inputF: CSV file with the changes, pathF: files directory (default is ..\UploadData)
# as a result a file with the name converted_+original_name is created on same directory
def convertFile(originalF,inputF,pathF=None):
    
    if pathF == None:
        origFilePath=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'UploadData'))
    else:
        origFilePath=pathF
    originalFile = os.path.join(origFilePath, originalF)
    convertedFile = os.path.join(origFilePath,"converted_"+originalF)
    inputFile = os.path.join(origFilePath,inputF)
    
    f = open(originalFile,'r') 
    newData = f.read()
    f.close()
    
    print("----------------------------------------------")
    print(("Original file: " + originalFile))
    print(("Input CSV file: " + inputFile)) 
    print("----------------------------------------------")
    
    csvObj = MyCsv.MyCsv(inputFile)
    itter = csvObj.retNumOfRowsinCsv()
            
    for i in range(itter):
        oldWord = csvObj.readValFromCsv(i,0)
        newWord = csvObj.readValFromCsv(i,1)
        
        newData = newData.replace(oldWord,newWord)
        
        print(("String: " + oldWord + "  replaced with: " + newWord))

    f = open(convertedFile,'w')
    f.write(newData)
    f.close()
    
    print("----------------------------------------------")
    print(("Output file: " + convertedFile))
    print("----------------------------------------------")

def main():
    convertFile("esearch.csv", "crosskaltura-partnerId-5334-completed.csv")
    convertFile("esearchEntitlement.csv", "crosskaltura-partnerId-5592-completed.csv")
    convertFile("esearchLanguages.csv", "crosskaltura-partnerId-5615-completed.csv")
    convertFile("esearchRelevancy.csv", "crosskaltura-partnerId-5660-completed.csv")
    convertFile("esearchUnified.csv", "crosskaltura-partnerId-5576-completed.csv")
    

if __name__ == '__main__':
    main()