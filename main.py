'''
    main.py
    TMWRK

    Main window which contains layouts for the following:
        - Search box layout
        - Weather display layout
        - Side bar layout
'''

import time
import sys
import os
import jsonhelper as jh
import geocoder
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QListWidget, QMainWindow, QDesktopWidget, QHBoxLayout, QProgressBar, QSplashScreen, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from search import Search
from sidebar import SideBar
from weatherdisplay import WeatherDisplay
from tabs import Tabs
from qt_material import apply_stylesheet
from PyQt5.QtGui import QFontDatabase, QFont
from api import Api
from stateStr_and_abbrevs import stateStr_to_abbrev

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()  

        self.settings_obj = self.getSettings()
        self.bookmarks_obj = self.getBookmarks()

        self.sideBar = SideBar(self)
        #if auto dark mode is enabled, then set theme based on what time it is
        if ('auto' in str(self.settings_obj['theme'])):
            self.sideBar.autoDark_toggle()  
            self.settings_obj = self.getSettings()

        self.theme = str(self.settings_obj['theme'])

        # for iteration 4 shenanigans
        self.consumed = False
        self.easter = ''
        self.thread = QThread()
        self.worker = EasterEgg()
        self.worker.moveToThread(self.thread)

        # apply theme and accent from settings.json
        # only 'dark' and 'light' themes work,
        # so need to take auto out of theme name, apply stylesheet, 
        # then set theme back to auto
        set_auto = False
        if ('auto' in str(self.theme)):
            set_auto = True
            if (str(self.theme) == 'auto-dark'):
                self.theme = 'dark'
            elif (str(self.theme) == 'auto-light'):
                self.theme = 'light'
            
        apply_stylesheet(self, self.theme + '_' + str(self.settings_obj['theme-accent']) + '.xml')
        
        if (set_auto == True):
            self.theme = 'auto-' + self.theme

        # central widget to hold the outer layout
        self.centralWidget = QWidget()

        # create an outer layout for central widget
        self.outerLayout = QHBoxLayout()
        self.centralWidget.setLayout(self.outerLayout)

        # list box for search which overlays on our central widget
        self.listWidget = QListWidget(self.centralWidget)
        self.listWidget.hide()

        # create an inner layout
        self.innerLayout = QVBoxLayout()

        # get city of index 0 from bookmarks.json
        # this sets startup city to first city in bookmarks json
        # self.location_input = self.bookmarks_obj[0]["location"]

        # this sets the starrtup location as the users current location via IP address
        self.location_input = self.getUserCityStr()
        
        # assign layout to class
        self.searchBoxLayout = Search(self)
        self.weatherDisplayLayout = WeatherDisplay(self.location_input)
        self.weatherDisplayLayout.upd_weather(self.location_input, self.getUserCityStr())
        self.tabs = Tabs(self.location_input)
        self.tabs.loadButtons(self.bookmarks_obj)

        # add layouts and widgets to outer layout               General Structure:
        self.innerLayout.addLayout(self.searchBoxLayout)        # top:     searchBoxLayout
        self.innerLayout.addLayout(self.weatherDisplayLayout)   # center:  weatherDisplayLayout
        self.innerLayout.addStretch()
        self.innerLayout.addWidget(self.tabs)                   # bottom:  tabs
        self.outerLayout.addLayout(self.innerLayout)            # left:    innerLayout (searchBoxLayout and weatherDisplayLayout)
        self.outerLayout.addWidget(self.sideBar)                # right:   sideBar

        # set the central widget
        self.setCentralWidget(self.centralWidget)

        self.searchBoxLayout.listWidget.itemActivated.connect(self.convert_item_to_location)
        self.searchBoxLayout.listWidget.itemClicked.connect(self.convert_item_to_location)

        need_new_search = Api(self.location_input)
        if (need_new_search.new_search == 1):
            self.searchBoxLayout.listWidget.itemActivated.connect(self.convert_item_to_location)
            self.searchBoxLayout.listWidget.itemClicked.connect(self.convert_item_to_location)

        # set focus to window
        self.setFocus(True)

    def initUI(self):
        # add application font
        QFontDatabase.addApplicationFont(':/FontAwesome.otf')

        # path to sun.png
        main_path = os.path.dirname(os.path.abspath(__file__))
        sun_path = main_path + '/sun.png'

        self.resize(1152, 768)
        self.center()
        self.setWindowTitle('Home - WeatherApp')
        self.setWindowIcon(QIcon(sun_path))

    def center(self):
        res = self.frameGeometry()
        pos = QDesktopWidget().availableGeometry().center()
        res.moveCenter(pos)
        self.move(res.topLeft())

    def convert_item_to_location(self, item):
        self.location_input = item.text()

        self.searchBoxLayout.searchBar.clear()
        self.searchBoxLayout.listWidget.clear()
        self.searchBoxLayout.listWidget.hide()
        self.get_location()

    def get_searchbar_text(self):
        self.location_input = self.searchBoxLayout.searchBar.text()
        self.searchBoxLayout.searchBar.clear()
        self.get_location()

    # this now sends the location_input to the upd_weather function which handles the
    # API request on separate thread
    def get_location(self):
        self.weatherDisplayLayout.location = self.location_input

        cityCountry = self.getUserCityStr()        
        words = cityCountry.split(", ")
        city = words[0]
        country = words[1]
        if (len(city) == 0 or len(country) != 2) :
            print("invalid city or country code")
        else :
            self.weatherDisplayLayout.upd_weather(self.location_input, self.getUserCityStr())
            self.bookmarks_obj = self.tabs.addLocationToJSON(self.bookmarks_obj, self.location_input)
            self.tabs.onBtnChange(self.location_input)
    
    # get users current city
    def getUserCityStr(self):
        currentCity = geocoder.ip('me')
        if currentCity.current_result.country == 'US':
            currentState = stateStr_to_abbrev.get(currentCity.current_result.state)
            currentCityStr = currentCity.current_result.city + ", " + currentState
        else:
            currentCityStr = currentCity.current_result.city + ", " + currentCity.current_result.country
        return currentCityStr

    def getBookmarks(self):
        # open bookmarks.json
        if jh.find('/bookmarks.json'):
            pass
        else:
            # set default data if no file found
            data = [
                {'id':0,
                 'location':'Knoxville, TN'
                }
            ]
            
            jh.fwrite('/bookmarks.json', data)

        # load bookmarks stored in bookmarks.json
        bookmarks_obj = jh.fread('/bookmarks.json')

        return bookmarks_obj

    def getSettings(self):
        # open settings.json
        if jh.find('/settings.json'):
            pass
        else:
            # set default data if no file found
            data = {
                'theme' : 'light',
                'theme-accent' : 'red',
                'time' : 'standard',
                'temp-unit' : 'fahrenheit',
                'sidebar' : 'expanded',
                'auto-dark-mode' : 'off'
            }
            
            jh.fwrite('/settings.json', data)

        # load settings stored in settings.json
        settings_obj = jh.fread('/settings.json')

        return settings_obj

    # iteration 4 shenanigans (looks for a unique sequence of keys and does some crazy stuff)
    def keyPressEvent(self, event):
        # what could this be?
        secret = '^^vv<><>BA'

        if event.key() == Qt.Key_Up:
            self.easter += '^'
        elif event.key() == Qt.Key_Down:
            self.easter += 'v'
        elif event.key() == Qt.Key_Left:
            self.easter += '<'
        elif event.key() == Qt.Key_Right:
            self.easter += '>'
        elif event.key() == Qt.Key_B:
            self.easter += 'B'
        elif event.key() == Qt.Key_A:
            self.easter += 'A'
        elif (event.modifiers() & Qt.ControlModifier) and (event.key() == Qt.Key_X):
            # stop Easter egg thread and go back to user's theme
            if self.consumed == True:
                self.worker.stop = True
                apply_stylesheet(self, self.theme + '_' + str(self.settings_obj['theme-accent']) + '.xml')
                # user gets full control of sidebar
                self.sideBar.btnSettings.setDisabled(False)
                self.sideBar.btnThemeAdjust.setDisabled(False)

        if secret.startswith(self.easter): # wait, what?
            # run Easter egg thread
            if secret == self.easter and self.consumed == False:
                self.worker.stop = False
                self.consumed = True

                self.i = 0
                self.accent = ['red', 'amber', 'lightgreen', 'teal', 'cyan', 'blue', 'purple', 'pink']

                self.thread.started.connect(self.worker.run)
                self.thread.start()
                self.worker.progress.connect(self.strobe)
                self.easter = ''

                # no point in accessing these buttons in this mode
                self.sideBar.btnSettings.setDisabled(True)
                self.sideBar.btnThemeAdjust.setDisabled(True)
        else:
            self.easter = '' # reset

    # apply strobe effect
    def strobe(self):
        apply_stylesheet(self, self.theme + '_' + self.accent[self.i] + '.xml')
        self.i = (self.i+1) % 8

class EasterEgg(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.stop = False

    def run(self):
        while(True):
            if self.stop:
                break

            self.progress.emit()
            time.sleep(0.20)
        self.finished.emit()

if __name__ == "__main__":
    font = QFont()
    font.setPointSize(10)

    app = QApplication(sys.argv)
    app.setFont(font)

    # Reference for splash screen: http://gist.github.com/345161974/8897f9230006d51803c987122b3d4f17
    main_path = os.path.dirname(os.path.abspath(__file__))
    splash_pix = QPixmap(main_path + '/sun.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(100)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
    progressBar.setStyleSheet('''QProgressBar::chunk { background-color: #cc1100; }''')

    splash.show()
    splash.showMessage("<h2><font color='white'><i>Initializing...</i></font></h2>", Qt.AlignTop | Qt.AlignCenter, Qt.black)
    
    app.processEvents()

    for i in range(1, 101):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
            app.processEvents()

    time.sleep(1)

    window = Window()
    window.show()
    splash.finish(window)

    sys.exit(app.exec_())