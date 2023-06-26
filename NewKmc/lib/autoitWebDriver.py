'''
Created on Jun 10, 2018

@author: adi.miller
'''
import os
import sys

from selenium import webdriver

pth = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib'))
sys.path.insert(1,pth)


class autoitWebDrive:
    
    def retautoWebDriver(self):
        return webdriver.Remote( command_executor='http://192.168.163.35:4723/wd/hub', desired_capabilities={'browserName':'AutoIt'})