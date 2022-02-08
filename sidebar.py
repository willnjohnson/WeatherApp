'''
    sidebar.py
    TMWRK

    Sidebar contains:
        create side bar which will have buttons to open settings, bookmarks, change themes, collapse/expand
'''

import os
import jsonhelper as jh
import browsehelper as bh
from PyQt5.QtWidgets import QDialog, QMainWindow, QShortcut, QVBoxLayout, QGroupBox, QPushButton
from PyQt5.QtGui import QIcon, QKeySequence
from settings import Settings
from bookmarks import Bookmarks
from history import History
from hourlyForecast import HourlyForecast
from dining import Dining
from confirmationdialog import ConfirmationDialog
from qt_material import apply_stylesheet
from PyQt5.QtCore import QTime

class SideBar(QGroupBox, QMainWindow):
    def __init__(self, window):
        super().__init__()

        self.theme_toggled = False
        # path to sun.png (to share with different windows)
        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.sun_path = self.main_path + '/sun.png'

        # windows
        self.side = window
        self.settingsWindow = None
        self.bookmarksWindow = None
        self.historyWindow = None
        self.hourlyForecastWindow = None
        self.diningOptionsWindow = None
        self.confirmationdialogWindow = None

        # bookmark button
        self.btnBook = QPushButton(chr(0xf097) + '    Bookmarks')
        self.btnBook.clicked.connect(self.openBookmarksWindow)
        self.btnBook.setToolTip('Manage bookmarks (Ctrl + B)')
        self.shortcutBook = QShortcut(QKeySequence('Ctrl+B'), self)
        self.shortcutBook.activated.connect(self.openBookmarksWindow)

        # settings button
        self.btnSettings = QPushButton(chr(0xf085) + '    Settings')
        self.btnSettings.clicked.connect(self.openSettingsWindow)
        self.btnSettings.setToolTip('Choose default settings (Ctrl + S)')
        self.shortcutSettings = QShortcut(QKeySequence('Ctrl+S'), self)
        self.shortcutSettings.activated.connect(self.openSettingsWindow)
        
        # wiki button
        self.btnWiki = QPushButton(chr(0xf266) + '    Wikipedia')
        self.btnWiki.clicked.connect(self.browseWiki)
        self.btnWiki.setToolTip('Open a Wikipedia article for the selected city')

        # Github button
        self.btnGithub = QPushButton(chr(0xf09b) + '    Github')
        self.btnGithub.clicked.connect(self.browseGithub)
        self.btnGithub.setToolTip('Visit WeatherApp Github page')

        # historical data button
        self.btnHistory = QPushButton(chr(0xf080) + '    Historical')
        self.btnHistory.clicked.connect(self.openHistoryWindow)
        self.btnHistory.setToolTip('View historical weather data (Ctrl + H)')
        self.shortcutHistory = QShortcut(QKeySequence('Ctrl+H'), self)
        self.shortcutHistory.activated.connect(self.openHistoryWindow)

        # hourly weather data button
        self.btnHourlyForecast = QPushButton(chr(0xf252) + '    Hourly')
        self.btnHourlyForecast.clicked.connect(self.openHourlyForecastWindow)
        self.btnHourlyForecast.setToolTip('View hourly forecast (Ctrl + G)')
        self.shortcutHourly = QShortcut(QKeySequence('Ctrl+G'), self)
        self.shortcutHourly.activated.connect(self.openHourlyForecastWindow)

        # dining button
        self.btnDining = QPushButton(chr(0xf000) + '    Dining')
        self.btnDining.clicked.connect(self.openDiningWindow)
        self.btnDining.setToolTip('Open the top rated restaurants for the selected city (Ctrl + D)')
        self.shortcutDining = QShortcut(QKeySequence('Ctrl+D'), self)
        self.shortcutDining.activated.connect(self.openDiningWindow)

        # quick-access dark/light theme button
        self.btnThemeAdjust = QPushButton(chr(0xf042) + '    Theme')
        self.btnThemeAdjust.clicked.connect(self.toggleTheme)
        self.btnThemeAdjust.setToolTip('Change theme (Ctrl + T)')
        self.shortcutThemeAdjust = QShortcut(QKeySequence('Ctrl+T'), self)
        self.shortcutThemeAdjust.activated.connect(self.toggleTheme)

        # expand/collapse (default: expanded)
        self.btnResize = QPushButton(chr(0xf101) + '    Collapse')
        self.btnResize.clicked.connect(self.toggleResize)
        self.btnResize.setToolTip('Expand/Collapse (Ctrl + R)')
        self.shortcutResize = QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcutResize.activated.connect(self.toggleResize)

        # on init: to expand or not to expand, that is the question
        obj = jh.fread('/settings.json')
        if obj['sidebar'] == 'collapsed':
            self.resizeSidebar()

        # organize buttons in button group layout
        btnGroupLayout = QVBoxLayout()
        btnGroupLayout.addWidget(self.btnBook)
        btnGroupLayout.addWidget(self.btnSettings)
        btnGroupLayout.addWidget(self.btnWiki)
        btnGroupLayout.addWidget(self.btnGithub)
        btnGroupLayout.addWidget(self.btnHistory)
        btnGroupLayout.addWidget(self.btnHourlyForecast)
        btnGroupLayout.addWidget(self.btnDining)
        btnGroupLayout.addStretch()
        btnGroupLayout.addWidget(self.btnThemeAdjust)
        btnGroupLayout.addWidget(self.btnResize)

        # make groupbox and buttons look nicer
        self.setStyleSheet('''
            QGroupBox {
                padding: 0;
            }
            QPushButton {
                padding-top: 6px;
                padding-bottom: 6px;
                border-radius: 20%;
                font-family: "FontAwesome";
            }
        ''')

        # set group button layout
        self.setLayout(btnGroupLayout)

    def openBookmarksWindow(self):
        # load bookmarks stored in bookmarks.json
        obj = jh.fread('/bookmarks.json')

        if self.bookmarksWindow is None:
            self.bookmarksWindow = Bookmarks(self)
            self.bookmarksWindow.resize(800, 550)
            self.bookmarksWindow.setMinimumWidth(600)
            self.bookmarksWindow.setWindowTitle('Bookmarks - WeatherApp')
            self.bookmarksWindow.setWindowIcon(QIcon(self.sun_path))
        
        self.bookmarksWindow.loadBookmarks(obj)
        self.bookmarksWindow.show()
        self.bookmarksWindow.activateWindow()
        self.side.setFocus(True)

    def openSettingsWindow(self):
        if not self.btnSettings.isEnabled():
            return

        if self.settingsWindow is None:
            self.settingsWindow = Settings(self.side)
            self.settingsWindow.resize(600, 550)
            self.settingsWindow.setMinimumWidth(500)
            self.settingsWindow.setWindowTitle('Settings - WeatherApp')
            self.settingsWindow.setWindowIcon(QIcon(self.sun_path))

        self.settingsWindow.reloadRadButtons(self.theme_toggled)
        self.theme_toggled = False
        self.settingsWindow.show()
        self.settingsWindow.activateWindow()
        self.side.setFocus(True)

    def openHistoryWindow(self):
        self.historyWindow = History(self)
        self.historyWindow.resize(800, 600)
        self.historyWindow.setWindowTitle('Historical Data - WeatherApp')
        self.historyWindow.setWindowIcon(QIcon(self.sun_path))
        self.historyWindow.show()
        self.historyWindow.activateWindow()
        self.side.setFocus(True)

    def openHourlyForecastWindow(self):
        selectedCity = self.side.tabs.getSelectedTabCity()
        self.hourlyForecastWindow = HourlyForecast(self, selectedCity)
        self.hourlyForecastWindow.resize(600, 600)
        self.hourlyForecastWindow.setWindowTitle(selectedCity + "'s Hourly Forecast - WeatherApp")
        self.hourlyForecastWindow.setWindowIcon(QIcon(self.sun_path))
        self.hourlyForecastWindow.show()
        self.hourlyForecastWindow.activateWindow()
        self.side.setFocus(True)

    def openDiningWindow(self):
        selectedCity = self.side.tabs.getSelectedTabCity()
        self.diningOptionsWindow = Dining(self, selectedCity)
        self.diningOptionsWindow.resize(800, 600)
        self.diningOptionsWindow.setWindowTitle(selectedCity + "'s Top Rated Restaurants - WeatherApp")
        self.diningOptionsWindow.setWindowIcon(QIcon(self.sun_path))
        self.diningOptionsWindow.show()
        self.diningOptionsWindow.activateWindow()
        self.side.setFocus(True)

    def openConfirmationDialog(self):
        if self.confirmationdialogWindow is None:
            self.confirmationdialogWindow = ConfirmationDialog(self)
            self.confirmationdialogWindow.resize(450, 250)
            self.confirmationdialogWindow.setWindowTitle('Browser Alert - WeatherApp')
            self.confirmationdialogWindow.setWindowIcon(QIcon(self.sun_path))
        return self.confirmationdialogWindow.exec_() # exec_ instead of show: to get return val

    def toggleTheme(self):
        if not self.btnThemeAdjust.isEnabled():
           return 
        
        # path to settings.json
        obj = jh.fread('/settings.json')

        # only 'dark' and 'light' themes work for stylesheets,
        # so need to take auto out of theme name, apply stylesheet, 
        # then set theme back to auto
        if ('auto' in obj['theme']):
            if (str(obj['theme']) == 'auto-dark'):
                obj['theme'] = 'dark'
            elif (str(obj['theme']) == 'auto-light'):
                obj['theme'] = 'light'
        
        # change theme based on value of 'theme'
        if str(obj['theme']) == 'light':
            obj['theme'] = 'dark'
            apply_stylesheet(self.side, theme=('dark_' + str(obj['theme-accent']) + '.xml'))
        elif str(obj['theme']) == 'dark':
            obj['theme'] = 'light'
            apply_stylesheet(self.side, theme=('light_' + str(obj['theme-accent']) + '.xml'))
        jh.fwrite('/settings.json', obj)
        self.theme_toggled = True
        self.side.setFocus(True)
        
    def autoDark_toggle(self):
        obj = jh.fread('/settings.json')
        time = QTime.currentTime()
        hour = time.hour()
        
        set_auto = False
        # only 'dark' and 'light' themes work,
        # so need to take auto out of theme name, apply stylesheet, 
        # then set theme back to auto
        if ('auto' in str(obj['theme'])):
            set_auto = True

        #10 pm = 22   #if time is >= 10 pm and <7 am:   
        if ( (hour >= 22) or (hour < 7) ):  
            #dark mode
            obj['theme'] = 'dark'
            apply_stylesheet(self.side, theme=('dark_' + str(obj['theme-accent']) + '.xml'))

        #if time is >= 7 am <10 pm: 
        elif ( (hour >= 7) or (hour < 22) ): 
            #light mode
            obj['theme'] = 'light'
            apply_stylesheet(self.side, theme=('light_' + str(obj['theme-accent']) + '.xml'))
            
        if (set_auto == True):
            obj['theme'] = 'auto-' + obj['theme']    

        

    # called either after saving the JSON value OR saving settings from settings window
    def resizeSidebar(self):
        # text for each button
        textBook = self.btnBook.text()
        textSettings = self.btnSettings.text()
        textThemeAdjust = self.btnThemeAdjust.text()
        textResize = self.btnResize.text()
        textWiki = self.btnWiki.text()
        textGithub = self.btnGithub.text()
        textHistory = self.btnHistory.text()
        textDining = self.btnDining.text()
        textHourly = self.btnHourlyForecast.text()

        # toggle text
        self.btnBook.setText(chr(0xf097) if textBook == (chr(0xf097) + '    Bookmarks') else (chr(0xf097) + '    Bookmarks'))
        self.btnSettings.setText(chr(0xf085) if textSettings == (chr(0xf085) + '    Settings') else (chr(0xf085) + '    Settings'))
        self.btnThemeAdjust.setText(chr(0xf042) if textThemeAdjust == (chr(0xf042) + '    Theme') else (chr(0xf042) + '    Theme'))
        self.btnResize.setText(chr(0xf100) if textResize == (chr(0xf101) + '    Collapse') else (chr(0xf101) + '    Collapse'))
        self.btnWiki.setText(chr(0xf266) if textWiki == (chr(0xf266) + '    Wikipedia') else (chr(0xf266) + '    Wikipedia'))
        self.btnGithub.setText(chr(0xf09b) if textGithub == (chr(0xf09b) + '    Github') else (chr(0xf09b) + '    Github'))
        self.btnHistory.setText(chr(0xf080) if textHistory == (chr(0xf080) + '    Historical') else (chr(0xf080) + '    Historical'))
        self.btnDining.setText(chr(0xf000) if textDining == (chr(0xf000) + '    Dining') else (chr(0xf000) + '    Dining'))
        self.btnHourlyForecast.setText(chr(0xf252) if textHourly == (chr(0xf252) + '    Hourly') else (chr(0xf252) + '    Hourly'))

        # flip chevron the other way
        if textResize == (chr(0xf101) + '    Collapse'):
            self.btnResize.setText(chr(0xf100))
        else:
            self.btnResize.setText(chr(0xf101) + '    Collapse')

    # check if we need to toggle based on selected state
    def toggleResizeOnState(self, state):
        textResize = self.btnResize.text()
        if (state == 'collapsed' and textResize == (chr(0xf101) + '    Collapse')) or (state == 'expanded' and textResize == (chr(0xf100))):
            self.resizeSidebar()

    # before toggling the resize, set sidebar state value to JSON
    def toggleResize(self):
        textResize = self.btnResize.text()
        obj = jh.fread('/settings.json')

        if textResize == (chr(0xf101) + '    Collapse'):
            obj['sidebar'] = 'collapsed'
        else:
            obj['sidebar'] = 'expanded'
        
        jh.fwrite('/settings.json', obj)
        self.resizeSidebar()

    def browseWiki(self):
        selectedCity = self.side.tabs.getSelectedTabCity()
        
        conf = self.openConfirmationDialog()
        if conf == True:
            selectedCity = self.side.tabs.getSelectedTabCity()
            bh.Wiki.search(selectedCity)

    def browseGithub(self):
        conf = self.openConfirmationDialog()
        if conf == True:
            bh.Generic.searchURL('https://github.com/utk-cs/TMWRK/')
