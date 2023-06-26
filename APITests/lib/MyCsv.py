'''
Created on Aug 21, 2017

@author: Adi.Miller
'''

import csv
import codecs


class MyCsv(object):

    def __init__(self, csvPath):
        self.csvPath = csvPath

    def retNumOfRowsinCsv(self):
        with open(self.csvPath, 'rb') as f:
            rows = list(csv.reader(codecs.iterdecode(f, 'utf-8')))

        return len(rows)

    def readValFromCsv(self, iRow, iCol):
        with open(self.csvPath, 'rb') as f:
            rows = list(csv.reader(codecs.iterdecode(f, 'utf-8')))

        return rows[iRow][iCol]
