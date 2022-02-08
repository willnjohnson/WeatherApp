from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QFont
from pyowm import *
from PyQt5.QtCore import QObject, QRunnable, Qt, pyqtSignal
from datetime import datetime
import pytz

APIKEY = '397761367f10ea851226a8c81cd1215b'

class Api: 
    location = ""
    country = ""
    need_to_search_again = 0
    def __init__(self, location):
        words = location.split(", ")
        self.location = words[0]
        self.country = words[1]
        
        # initialize and owm object
        self.owm = OWM(APIKEY)

        # initialize a weather manager object
        self.mgr = self.owm.weather_manager()

        # initialize a onecall object request
        #
        # there is an ambiguity in the locations_for() code in this library that is currently being
        # patched per github. this has to do with the country field being used for states in the US
        # and also for other countries, some of which match. like California and Canada.
        # if not patched before end of iteration, this can be swapped out for another geocode api
        self.reg = self.owm.city_id_registry()
        
        # error check country abbreviation (length has to be 2)
        if (len(self.country) != 2):
            self.need_to_search_again = 1
            self.new_search()

        self.list_of_locations = self.reg.locations_for(self.location, country=self.country)

        # error check city name
        if (len(self.list_of_locations) == 0):
            self.need_to_search_again = 1
            self.new_search()
        
        self.regLocation = self.list_of_locations[0]
        self.lat = self.regLocation.lat
        self.lon = self.regLocation.lon

        try:
            self.onecall = self.mgr.one_call(lat=self.lat, lon=self.lon)
        except Exception as e:
            self.display_error_message(e)

    def new_search(self):
        self.need_to_search_again = 0
        return 1

    # function to display QDialog error message
    def display_error_message(self, error):
        error_message = QDialog()
        error_message.setWindowTitle("Error")
        error_message.setWindowFlags(Qt.WindowStaysOnTopHint)
        error_message.setFixedSize(400, 100)
        error_message.setStyleSheet("background-color: rgb(255, 0, 0);")
        error_message.setFont(QFont("Arial", 12))
        error_message.setStyleSheet("color: rgb(255, 255, 255);")
        error_message.show()
        
        # AttributeError: 'QDialog' object has no attribute 'setText'
        #error_message.setText(error.args[0])

        error_message.exec_()

class apiSignals(QObject):
    '''
    signals available from running an apiWorker thread
    '''
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(Api, Api)

class apiWorker(QRunnable):
    '''
    worker thread for api updates
    '''
    signals = apiSignals()
    is_interrupted = False

    def __init__(self, location, cc_location):
        super(apiWorker, self).__init__()
        self.location = location
        self.cc_location = cc_location

    def run(self):
        try:
            # searched city api object
            self.api = Api(self.location)
            # users current city via IP api object
            self.ccapi = Api(self.cc_location)
            # returns both apis as signal object
            self.signals.result.emit(self.api, self.ccapi)
        except Exception as e:
            self.signals.error.emit(str(e))

        self.signals.finished.emit()

# class to hold both local(user) and location date and time information
class Time:
    localDateTime = None
    locationDateTime = None
    timezone = None
    local12Str = ""
    local24Str = ""
    location12Str = ""
    location24Str = ""

    # Time constructor, takes a timezone string from api.onecall.timezone
    def __init__(self, timezone: str):
        self.timezone = timezone

        self.localDateTime = datetime.now()
        self.locationDateTime = datetime.now(pytz.timezone(timezone))

        self.local12Str = self.localDateTime.strftime("%B %d, %Y - %I:%M %p")
        self.local24Str = self.localDateTime.strftime("%B %d, %Y - %H:%M")

        self.location12Str = self.locationDateTime.strftime("%B %d, %Y - %I:%M %p")
        self.location24Str = self.locationDateTime.strftime("%B %d, %Y - %H:%M")

    # updates the Time object, take a timezone string from api.onecall.timezone
    def updateTime(self, timezone: str):
        self.timezone = timezone

        self.locationDateTime = datetime.now()
        self.locationDateTime = datetime.now(pytz.timezone(timezone))

        self.local12Str = self.localDateTime.strftime("%B %d, %Y - %I:%M %p")
        self.local24Str = self.localDateTime.strftime("%B %d, %Y - %H:%M")

        self.location12Str = self.localDateTime.strftime("%B %d, %Y - %I:%M %p")
        self.location24Str = self.localDateTime.strftime("%B %d, %Y - %H:%M")