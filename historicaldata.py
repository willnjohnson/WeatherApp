import requests
import json

from historygraph import HistoryGraph

class HistoricalData:
    def __init__(self):
        self.token = "xwPDPxAMOcpejWpbvJbGJddMEQUBPHlO"
        self.url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'
        self.header = dict(token=self.token)
        self.dataType = ''
        self.location = ''
        self.locationType = ''
        self.units = 'standard'
        self.startDate = ''
        self.endDate = ''
        self.limit = '1000'
        self.locCats = []
        self.dataSets = []
        self.dataCats = []
        self.dataList = []
        self.isValid = True

    def setLimit(self, limit):
        if int(limit) < 1000 or limit > 0:
            self.limit = limit
        else:
            limit = '1000'

    def setLocationType(self, locType):
        self.locationType = locType

    def setLocation(self, loc):
        self.location = loc

    def  setStartDate(self, year, month, day):
        if year and month and day != '':
            if int(year) < 1970:
                y = '1970'
            else:
                y = year
            if int(month) < 1 or int(month) > 12:
                m = '1'
            else:
                m = month
            if int(day) < 0 or int(day) > 31:
                d = '1'
            else:
                d = day

            self.startDate = y + '-' + m + '-' + d
    
    def  setEndDate(self, year, month, day):
        if year and month and day != '':
            if int(year) < 1970:
                y = '1970'
            else:
                y = year
            if int(month) < 1 or int(month) > 12:
                m = '1'
            else:
                m = month
            if int(day) < 0 or int(day) > 31:
                d = '1'
            else:
                d = day

            self.endDate = y + '-' + m + '-' + d

    def getDataSets(self):
        dSetUrl = self.url+'datasets?limit='+self.limit+'&locationid='+self.locationType+':'+self.location
        r = requests.get(dSetUrl, headers=self.header)
        if r.status_code == 200:
            d = r.json()
            if 'results' in d:
                self.isValid = True
                for item in d['results']:
                    self.dataSets.append(item['name'])
            else:
                self.isValid = False
        else:
            self.isValid = False

    def getDataCategories(self):
        dSetUrl = self.url+'datacategories?limit='+self.limit+'&locationid='+self.locationType+':'+self.location
        r = requests.get(dSetUrl, headers=self.header)
        if r.status_code == 200:
            d = r.json()
            if 'results' in d:
                self.isValid = True
                for item in d['results']:
                    self.dataCats.append([item['name'], item['id']])
            else:
                self.isValid = False
        else:
            self.isValid = False
    
    def getData(self):
        dSetUrl = self.url+'data?datasetid=GHCND&datatypeid='+self.dataType+'&limit='+self.limit+'&locationid='+self.locationType+':'+self.location+'&startdate='+self.startDate+'&enddate='+self.endDate+'&units='+self.units
        r = requests.get(dSetUrl, headers=self.header)
        if r.status_code == 200:
            d = r.json()
            if 'results' in d:
                self.isValid = True
                for item in d['results']:
                    self.dataList.append([item['value'], item['date']])
            else:
                self.isValid = False
        else:
            self.isValid = False

    def getLocationCategories(self):
        fullUrl = self.url+'locationcategories?limit='+self.limit
        r = requests.get(fullUrl, headers=self.header)
        if r.status_code == 200:
            d = r.json()
            if 'results' in d:
                self.isValid = True
                for item in d['results']:
                    self.locCats.append([item['name'], item['id']])
            else:
                self.isValid = False
        else:
            self.isValid = False