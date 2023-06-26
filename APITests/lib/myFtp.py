'''
Created on Aug 30, 2017

@author: Adi.Miller
'''
import ftplib
import os
import socket

import paramiko

#===============================================================================
# import paramiko
# from paramiko.py3compat import input
#===============================================================================

# Paramiko client configuration
UseGSSAPI = True  # enable GSS-API / SSPI authentication
DoGSSAPIKeyExchange = True
Port = 22

 
class myFtp():
    '''
    classdocs
    '''


    def __init__(self, server, user, pwd):
        '''
        Constructor
        '''
        self.server = server
        self.user = user
        self.pwd= pwd
        
        
        
    def uploadFile(self, fPath, tPath, fnewName):
        try:
            self.session = ftplib.FTP(self.server, self.user, self.pwd)
            self.session.cwd(tPath)
            f = open(fPath,'rb')                  
            self.session.storbinary('STOR ' + fnewName, f)    
            f.close()                                   
            self.session.quit()
            return True
        except Exception as Exp:
            print(Exp)
            print(('Could not start session for UPLOAD with the FTP server- ' + self.server))
            return False
        
        
    def DelFilefromserver(self, fPath):
        
        try:
            self.session = ftplib.FTP(self.server, self.user, self.pwd) 
            self.session.delete(fPath)
            try:
                self.session.delete(fPath)
                print(('deleted file ' + fPath + ' From the ftp server'))
            except:
                print('file not exist on the ftp server')
        except:
            print(('Could not start session for DELETE with the FTP server- ' + self.server))
            assert False
            
    
    
    def sftpconnect(self):
        
        # get host key, if we know one
        hostkeytype = None
        hostkey = None
        try:
            host_keys = paramiko.util.load_host_keys(
                os.path.expanduser("~/.ssh/known_hosts")
            )
        except IOError:
            try:
                # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                host_keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/ssh/known_hosts")
                )
            except IOError:
                print("*** Unable to open host keys file")
                host_keys = {}
        
        if self.server in host_keys:
            hostkeytype = list(host_keys[self.server].keys())[0]
            hostkey = host_keys[self.server][hostkeytype]
            print(("Using host key of type %s" % hostkeytype))
        
        
        # now, connect and use paramiko Transport to negotiate SSH2 across the connection
        try:
            t = paramiko.Transport((self.server, Port))
            t.connect(hostkey,self.user,self.pwd,gss_host=socket.getfqdn(self.server),gss_auth=UseGSSAPI,gss_kex=DoGSSAPIKeyExchange)
            sftp = paramiko.SFTPClient.from_transport(t)
            
        except Exception as Ex:
            print(Ex)
            
            