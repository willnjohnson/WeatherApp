'''
offlinedata.py
TMWRK

Edited By:
    Robert Schaffer

Class for writing and reading last known weather data in case
there is no internet connection for API calls
'''

from datetime import datetime
import pickle

class offlineData:
    def __init__(self):
        self.numLocations = 0
        self.locationData = []
        self.datetime
    
    def addLocationData(self, data):
        self.locationData.append(data)
        self.numLocations += 1

    def writeOfflineData(self):
        self.datetime = datetime.now()
        with open('offline_data.pkl', 'wb') as outp:
            pickle.dump(self.datetime, outp, pickle.HIGHEST_PROTOCOL)
            pickle.dump(self.numLocations, outp, pickle.HIGHEST_PROTOCOL)
            for data in self.locationData:
                pickle.dump(data, outp, pickle.HIGHEST_PROTOCOL)

    def readOfflineData(self):
        with open('offline_data.pkl', 'rb') as inp:
            self.datetime = pickle.load(inp)
            self.numLocations = pickle.load(inp)
            for num in range (0, self.numLocations):
                self.addLocationData(pickle.load(inp))
