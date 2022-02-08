'''
    tabs.py
    TMWRK

    Tabs:
        Organize a horizontal list of cities. When a user searches a city that isn't already in the list,
        add that city to the front (left-most) of the list. Also handle case when user switches cities (toggling).
'''

import jsonhelper as jh
from PyQt5 import QtCore
import geocoder
from stateStr_and_abbrevs import stateStr_to_abbrev
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QButtonGroup, QGroupBox, QHBoxLayout, QMenu, QPushButton, QScrollArea
from weatherdisplay import WeatherDisplay
class Tabs(QScrollArea):
    def __init__(self, location):
        super().__init__()

        self.location = location
        self.weatherDisplay = WeatherDisplay(self.location)

        # settings for the scroll area
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignBottom)
        self.setToolTip('Check the weather for a city in this bookmark list')
        self.setFixedHeight(65)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # inside the scroll area is a groupbox with a horizontal layout
        self.btnGroupBox = QGroupBox()
        self.btnGroupBoxLayout = QHBoxLayout()
        self.btnGroupBoxLayout.addStretch()    # we want no big spacing between cities

        # we need this to control the toggle of our cities (so buttons act more like a radiobutton)
        self.btnGroup = QButtonGroup()

        # set group button layout and box to the scroll area
        self.btnGroupBox.setLayout(self.btnGroupBoxLayout)
        self.setWidget(self.btnGroupBox)

        # make groupbox and buttons look nicer
        self.setStyleSheet('''
            QGroupBox {
                margin-top: 1px;
                padding: 0;
            }
            QPushButton {
                /* more compact */
                padding-left: 3%;
                padding-right: 3%;
            }
        ''')

    # clear buttons
    def clearButtons(self):
        location = None

        for btnObj in self.findChildren(QPushButton):
            if btnObj.isChecked():
                location = btnObj.text()

            btnObj.setParent(None) 
            self.btnGroup.removeButton(btnObj)
            self.btnGroupBoxLayout.removeWidget(btnObj)
        
        return location

    # load buttons of stored cities on program startup
    def loadButtons(self, bookmarks_obj):
        btnGeoLocation = None

        bookmarks_obj.reverse() # reverse for inserting tabs in desired order
        for obj in bookmarks_obj:
            self.btnLocation = QPushButton(obj['location'])
            
            # look for button where it matches name of startup location
            if self.location == self.btnLocation.text():
                btnGeoLocation = self.btnLocation

            self.btnGroup.addButton(self.btnLocation)                           # allows for toggle functionality
            self.setButtonAttributes()
            self.btnGroupBoxLayout.insertWidget(0, self.btnLocation)            # insert to front
        bookmarks_obj.reverse() # reverse back to original

        # set check for the location that was specified by geocoder, 
        # otherwise the button at index 0 is checked by default
        if btnGeoLocation != None:
            btnGeoLocation.setChecked(True)

    # when user modifies an entry (search a city, select a pushbtn, etc.), buttons might change
    def onBtnChange(self, location):
        # check list of pushbtns to see if btn label matches city input
        for btnObj in self.findChildren(QPushButton):
            if btnObj.text() == str(location):
                btnObj.setChecked(True)
                return

        # otherwise, create a new pushbtn, insert it, and add check to it
        self.btnLocation = QPushButton(str(location))
        self.btnGroup.addButton(self.btnLocation)                   # allows for toggle functionality
        self.setButtonAttributes()
        self.btnGroupBoxLayout.insertWidget(0, self.btnLocation)    # insert to front

    # before we update tab buttons, we should update JSON and bookmarks object
    def addLocationToJSON(self, bookmarks_obj, location):
        # return without adding location, if button for location already exists
        # NOTE: this method must occur BEFORE the onBtnChange method since onBtnChange adds in button
        for btnObj in self.findChildren(QPushButton):
            if btnObj.text() == str(location):
                return bookmarks_obj

        # increment ids
        for obj in bookmarks_obj:
            obj['id'] = obj['id']+1
        newObj = {'id': 0, 'location':location}
        
        # prepend new city object to bookmarks object
        bookmarks_obj.reverse()
        bookmarks_obj.append(newObj)
        bookmarks_obj.reverse()

        # get path and update JSON file
        jh.fwrite('/bookmarks.json', bookmarks_obj)

        return bookmarks_obj

    def setButtonAttributes(self):
        self.btnLocation.setCheckable(True)
        self.btnLocation.setChecked(True)
        self.btnLocation.setToolTip('Click to see weather for ' + self.btnLocation.text())
        self.btnLocation.clicked.connect(self.reupdateWeather)
        self.btnLocation.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.btnLocation.customContextMenuRequested.connect(lambda pos, child=self.btnLocation: self.customMenuEvent(pos, child))


    # Reference: https://stackoverflow.com/questions/59798284/pyqt-multiple-objects-share-context-menu#59798635
    def customMenuEvent(self, eventPosition, child):
        contextMenu = QMenu(self)
        contextMenu.setStyleSheet('''
            QMenu {
                margin: 0;
                border: 1px solid rgba(0,0,0,0.5);
            }
        ''')

        # if there's only two items, a single city and a spacer,
        # then just return since we don't allow the user to delete their only city
        if self.btnGroupBoxLayout.count() < 3:
            return

        # otherwise we care about our actions
        removeAction = contextMenu.addAction('&Remove')
        
        action = contextMenu.exec_(child.mapToGlobal(eventPosition))

        # if removeAction, remove tab button and update JSON
        if action == removeAction:
            # check for the button that is enabled
            locationToReselect = None
            for btnObj in self.findChildren(QPushButton):
                if btnObj.isChecked():
                    locationToReselect = btnObj.text()

            # we remove the button (and reselect location if needed)
            location = child.text()
            child.setParent(None) 
            self.btnGroup.removeButton(child)
            self.btnGroupBoxLayout.removeWidget(child)
            #self.reselectLocation(locationToReselect) # if location that was enabled no longer found, we will set btn[0]

            # we read JSON file to obj
            bookmarks_obj = jh.fread('/bookmarks.json')

            # we reorganize index and pop JSON entry of removed button
            count = 0
            indexToPop = None
            for item in bookmarks_obj:
                if item['location'] == location:
                    indexToPop = count
                else:
                    item['id'] = count
                    count = count + 1
            bookmarks_obj.pop(indexToPop)

            # we write obj to JSON file
            jh.fwrite('/bookmarks.json', bookmarks_obj)

            # reselect location of previously enabled btn
            # if location not found, set first button
            if self.reselectLocation(locationToReselect) == True:
                self.weatherDisplay.upd_weather(btnObj.text(), self.getUserCityStr())
            

    # when user clicks a button in the Tab section, update the weather
    def reupdateWeather(self):
        btn = self.sender()
        self.weatherDisplay.upd_weather(btn.text(), self.getUserCityStr())
        self.setFocus(False)

    def reloadButtons(self):
        # get path and update JSON file
        bookmarks_obj = jh.fread('/bookmarks.json')

        location = self.clearButtons()      # clear button, and get location of selected location before it was cleared
        self.loadButtons(bookmarks_obj)
        self.reselectLocation(location)     # if location still exists after reloading buttons, reselect it

    def reselectLocation(self, location):
        # if we find the location we had cleared, reselect it
        # that is, add a check to it and return
        for btnObj in self.findChildren(QPushButton):
            if location == btnObj.text():
                btnObj.setChecked(True)
                return False        

        # otherwise set the first button
        btnObj.setChecked(True)
        return True

    # get users current city
    def getUserCityStr(self):
        currentCity = geocoder.ip('me')
        if currentCity.current_result.country == 'US':
            currentState = stateStr_to_abbrev.get(currentCity.current_result.state)
            currentCityStr = currentCity.current_result.city + ", " + currentState
        else:
            currentCityStr = currentCity.current_result.city + ", " + currentCity.current_result.country
        return currentCityStr

    # get city of selected tab
    def getSelectedTabCity(self):
        for btnObj in self.findChildren(QPushButton):
            if btnObj.isChecked():
                return btnObj.text()