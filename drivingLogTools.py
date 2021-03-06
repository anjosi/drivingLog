#!/usr/bin/env python
#-*- coding: utf-8 -*-
import pandas as pd

class logDataFrame:
    def __init__(self):
        self.df = pd.DataFrame(columns=['StartDate', 'StartTime', 'EndDate', 'EndTime', 'StartKm', 'EndKm', 'Distance','StartAddress', 'EndAddress', 'Description', 'Driver', 'Type'])
        pd.__version__

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df


import csv

class logParser:

    def __init__(self, p_filePath, p_source='Kunnallissairaalantie 61, 20810 Turku', p_year='2019', p_initKm = '50000', p_defaultDriver='Antti Siirilä'):

        self._keywords = {
                "koti": "Kunnallissairaalantie 61, 20810 Turku",
                "konttori": "Kärsamäentie 8-10, 20300 Turku",
                "t": "Työmatka",
                "tm": "Työn ja kodin välinen matka",
                "o": "Henkilökohtainen matka",
                "noora": "Noora Kotaja",
                "fta": "Fure-kohteen tarjouskatselmointi",
                "fti": "Fure-kohteen tilauskatselmointi",
                "mta": "Modernisaatio-kohteen tarjouskatselmointi",
                "mti": "Modrnisaatio-kohteen tilauskatselmointi",
                "at": "Asiakastapaaminen",
                "tmk": "Vierailu asennustyömaalla",
                "apf": "APF-kohteen katselmointi",
                "ah": "Vierailu alihankkijalla",
                "eti": "Ebuli-kohteen tilauskatselmointi",
                "eta": "Ebuli-kohteen tarjouskatselmointi"
                }
        self._lineNum = 0
        self._path = p_filePath
        self._baseAddress = p_source
        self._source = p_source
        self._year = p_year
        self._destination = ''
        self._startDate = ''
        self._startTime = ''
        self._endDate = ''
        self._endTime = ''
        self._baseKm = p_initKm
        self._initKm = p_initKm
        self._destinationKm = ''
        self._driver = ''
        self._desc = ''
        self._type = ''
        self._driveTable = None
        self._defaultDriver = p_defaultDriver


    def readFileToDF(self):
        self.driveTable = logDataFrame()
        with open(self.path, mode='r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";", skipinitialspace=True)
            self._lineNum=0
            ## read a new row
            
            
            for row in reader:
                #row with a length of 1 is a date row
                if(len(row[None]) == 1):
                    self._newDate(row[None][0])
                    continue
                #The row is an aller retour row, if the first field starts with &
                if("&" in row[None][0]):
                    ##print("handling the allerRetour.")
                    self._handleAllerRetour(row[None])
                    self._setType(row[None][1])
                    self._setDriver(row[None])
                else:
                    print("handling the aller.")
                    self._handleAller(row[None])
                    self._setType(row[None][1])
                    self._setDriver(row[None])
                if(len(row[None]) < 3):
                    print("wierd row: " + row[None][0] + ", @: " + str(self._lineNum) + ', len: ' + str(len(row[None])))
                    continue
                self._handleTimeAndKm(row[None][2])
                self._appendDataFrame()
                self._lineNum += 1
        return self.driveTable.df
        

    ## handle a return trip -> make the first field to become the description. Destination will be the same as the source.
    def _handleAllerRetour(self, p_row):
        l_FirstField = p_row[0]
        self._destination = self._source.capitalize()
        self._desc = l_FirstField[l_FirstField.find('&')+1:].strip().capitalize()
        ### append the extra description if available
        if(len(p_row) == 5):
            self._desc = self._desc + ' (' + self._lookASide(p_row[4].lower()) + ')'
        if(len(p_row) > 5):
            print("something weird in the neighborhood of aller return", p_row)
    ##print(self._desc)
    ## Handel a new date row
    def _newDate(self, p_input):
        self._startDate = p_input.replace('-','').strip()
        try:
            if(self._startDate[-1] == '.'):
                self._startDate += self._year
            else:
                self._startDate += '.'+self._year
        except IndexError:
            print("Parsing the date field ["+p_input+"] failed in row "+str(self._lineNum) )
        self._endDate = self._startDate
    ## print(self._startDate, self._endDate)
    ## handle oneway trip
    def _handleAller(self, p_input):
        self._destination = p_input[0].replace('-','').strip()
        self._destination = self._lookASide(self._destination.lower()).capitalize()
        self._desc = self._getDescription(p_input)

    ## Replace keywords with the corresponding addresses
    def _lookASide(self, p_input):
        try:
            return self._keywords[p_input.strip()]
        except KeyError:
            return p_input
    ## Parse the description field
    def _getDescription(self, p_input):
        if(len(p_input) == 5):
            l_lowered = p_input[4].strip().lower()
            l_translated = self._lookASide(l_lowered)
            if(l_translated == l_lowered):
                return p_input[4].strip()
            else:
                return l_translated
        return '--'
    ## Parse the driver
    def _setDriver(self, p_input):
        if(len(p_input) > 3 and p_input[3] != ''):
            self._driver = self._lookASide(p_input[3].lower())
        else:
            self._driver = self._defaultDriver
    ## Parse the trip type
    def _setType(self, p_input):
        ##print("Type input: " + p_input)
        ##print("Look a side: " + self._lookASide(p_input.strip().lower()))
        self._type = self._lookASide(p_input.strip().lower())
        ## Parse the start and end times and end kilometers
    def _handleTimeAndKm(self, p_input):
        l_subFields = p_input.strip().split(" ")
        if(len(l_subFields) < 3):
            print("Line: " + str(self._lineNum) + " too few subfields (time and km): " )
            print(l_subFields)
            return
        if(len(l_subFields) > 3):
            print("Line: " + str(self._lineNum) + " too many subfields (time and km): ")
            try:
                l_subFields.remove('')
            except ValueError:
                print("Empty element expected but not found")
            print(l_subFields)
        self._startTime = self._decodeTimeField(l_subFields[0])
        self._endTime = self._decodeTimeField(l_subFields[1])
        self._destinationKm = l_subFields[2]
    ## Append the parsed row to the pandas data frame
    def _appendDataFrame(self):
        temp = str(int(self._destinationKm)-int(self._initKm))
        ##print("Driver: " + self._driver + " Type: " + self._type)
        self.driveTable.df = self.driveTable.df.append({"StartDate": self._startDate, "StartTime": self._startTime, "EndDate": self._endDate, "EndTime": self._endTime, "StartKm":self._initKm, "EndKm": self._destinationKm, "Distance": temp, "StartAddress": self._source, "EndAddress": self._destination, "Description": self._desc, "Driver": self._driver, "Type": self._type}, ignore_index=True)
        self._source = self._destination
        self._initKm = self._destinationKm
    ## reformat the time field: (x)xxx -> (x)x.xx
    def _decodeTimeField(self, p_input):
        return p_input[:-2] + "." + p_input[-2:]

    @property
    def driveTable(self):
        return self._driveTable
    
    @driveTable.setter
    def driveTable(self, value):
        self._driveTable = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def init(self):
        self._initKm = self._baseKm
        self._source = self._baseAddress
