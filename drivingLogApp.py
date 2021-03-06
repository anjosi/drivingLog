#!/usr/bin/env python
# -*- coding: utf-8 -*-
from drivingLogTools import *
import pandas as pd

class logApplication:

    def __init__(self, p_path="ajot_1.txt"):
        self._dTable = logDataFrame()
        self.parser = logParser(p_path, p_source='Kunnallissairaalantie 61, 20810 Turku', p_year='2020', p_initKm='72582')

    def addLogFile(self, p_path=''):
        if(p_path != ''):
            self.parser.path=p_path
        print (self.parser.path)
        self.dTable.df = self.dTable.df.append(self.parser.readFileToDF(), ignore_index=True)

## compose an excel file from the data frame
    def _makeExcel(self, p_fileName = 'ajopaivakirja'):
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #print(self.driveTable.df)
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(p_fileName + '.xlsx', engine='openpyxl')
        # Convert the dataframe to an XlsxWriter Excel object.
        self.dTable.df.to_excel(writer, sheet_name='data')
        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    @property
    def dTable(self):
        return self._dTable
    
    @dTable.setter
    def dTable(self, value):
        self._dTable = value

    def driveTableInit(self):
        self.dTable.df = self.dTable.df.iloc[0:0]
        self.parser.init()


