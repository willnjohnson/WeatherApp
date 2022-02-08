'''
    weatherdisplay.py
    TMWRK

    Weather display contains:
        Display of city and weather which may utilize the weather API
'''

import os

import jsonhelper as jh
import browsehelper as bh
import qtawesome as qta
import geocoder
from datetime import datetime
import sys
from stateStr_and_abbrevs import stateStr_to_abbrev
from api import Api, apiWorker, Time
from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QGridLayout, QLabel, QLayout, QMessageBox, QSplashScreen, QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QSize, QThreadPool, Qt 
from PyQt5.QtGui import QColor, QPixmap

class WeatherDisplay(QGridLayout):
    def __init__(self, location):
        super().__init__()

        self.getSettings()
        self.loadingSplash()

        # instantiates a pool of usable threads
        self.threadpool = QThreadPool()

        self.location = location
        # searched city api object
        api = Api(location)
        # users current city via IP api object
        ccapi = Api(self.getUserCityStr())

        self.ccImagePath = bh.Wiki.getImage(ccapi.lat, ccapi.lon)
        self.isDay = True

        self.currentWeatherGridLayout = QGridLayout()
        self.currentWeatherFrame = QFrame()
        self.currentWeatherDisplay(api)

        self.tomorrowWeatherGridLayout = QGridLayout()
        self.tomorrowWeatherFrame = QFrame()
        self.tomorrowWeatherDisplay(api)

        self.currentCityWeatherGridLayout = QGridLayout()
        self.currentCityWeatherFrame = QFrame()
        self.currentCityWeatherDisplay(ccapi)

        self.weeklyDisplayBox = QVBoxLayout()
        self.weekWeatherFrame = QFrame()
        self.oneDayLayout = QGridLayout()
        self.weekForecastWeatherDisplay(api)

        self.alert_count = 0
    
    # initializes what the loading splash screen will look like
    def loadingSplash(self):
        # Reference for splash screen: http://gist.github.com/345161974/8897f9230006d51803c987122b3d4f17
        main_path = os.path.dirname(os.path.abspath(__file__))
        self.splash_pix = QPixmap(main_path + '/sun.png')
        self.splash = QSplashScreen(self.splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash.setEnabled(False)

    #updates settings, used for Fahrenheit/Celsius Toggle after settings applied
    def getSettings(self): 
        # load settings stored in settings.json
        self.obj = jh.fread('/settings.json')
        
    # note: display test
    def currentWeatherDisplay(self, api):
        self.getSettings()

        if str(self.obj['temp-unit']) == 'fahrenheit':
            temp = api.onecall.current.temperature('fahrenheit')
            self.FC = 'F'
        else: 
            temp = api.onecall.current.temperature('celsius')
            self.FC = 'C'
        wind = api.onecall.current.wnd
        time = Time(api.onecall.timezone)
        
        if str(self.obj['time']) == "standard":
            self.timeStr = time.location12Str
        else:
            self.timeStr = time.location24Str

        # add shadow for elegance
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(0,0,0,127))
        self.shadow.setBlurRadius(8)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)

        # remove widgets in layout when updating
        self.removeLayoutWidgets(self.currentWeatherGridLayout)

        # set frame style
        self.currentWeatherFrame.setGraphicsEffect(self.shadow)
        self.currentWeatherFrame.setFrameStyle(QFrame.StyledPanel)
        self.currentWeatherFrame.setFixedWidth(450)
        self.currentWeatherFrame.setMaximumHeight(200)

        if (time.locationDateTime.hour < 20 and time.locationDateTime.hour > 8):
            self.isDay = True
        else:
            self.isDay = False

        backgroundTime = None
        if self.isDay == True:
            backgroundTime = 'rgb(130, 190, 214);'
        else:
            backgroundTime = 'rgb(22, 22, 45);'

        self.currentWeatherFrame.setStyleSheet('''
        QFrame {
            background-color: ''' + backgroundTime + '''
            border: none;
            color: #fff;
            font-family: "FontAwesome";
        }

        QLabel {
            background: none;
        }

        QLabel#heading {
            font-size: 15pt;
        }

        QLabel#cur_temper {
            font-size: 25pt;
        }
        ''')

        # note: some labels in this widget may be hardcoded
        
        # label for location name
        self.labelLocationName = QLabel(api.location + ', ' + api.country)
        self.labelLocationName.setObjectName('heading')
        self.labelLocationName.setToolTip('Location\'s Name')
        
        # label for location's date and time
        self.labelDateAndTime = QLabel(self.timeStr)
        self.labelDateAndTime.setToolTip('Location\'s Current Date and Time')
        
        # widget with image of weather
        searchMode = "today"
        self.widgetWeatherStatus = qta.IconWidget()
        self.widgetWeatherStatus.setIconSize(QSize(60, 60))
        self.iconWeatherStatus = self.getWeatherStatus(api, searchMode, 0, self.isDay) #using 0 as a placeholder to be able to implement day of the week
        self.widgetWeatherStatus.setIcon(self.iconWeatherStatus)
        self.widgetWeatherStatus.setToolTip('Location\'s Current Weather')

        # label of current temperature
        self.labelCurrentTemper = QLabel(str(round(temp.get('temp'))) + chr(0xb0) + self.FC)
        self.labelCurrentTemper.setObjectName('cur_temper')
        self.labelCurrentTemper.setToolTip('Location\'s Current Temperature')

        # label of current condition
        currentCond = str(api.onecall.current.detailed_status)
        self.labelCurrentCond = QLabel(currentCond[0].upper() + currentCond[1:])
        self.labelCurrentLowHigh = QLabel(str(temp.get('min')) + chr(0xb0) + self.FC + ' | ' + str(temp.get('max')) + chr(0xb0) + self.FC)
        self.labelCurrentFeelsLike = QLabel('Feels like ' + str(round(temp.get('feels_like'))) + chr(0xb0) + self.FC)
        self.labelCurrentWindSpeed = QLabel('Wind speed ' + str(wind.get('speed')) + ' mph')

        # tooltips to guide user
        self.labelCurrentCond.setToolTip('Location\'s Current Weather Condition')
        self.labelCurrentFeelsLike.setToolTip('Location\'s Current \'Feels Like\' Temperature')
        self.labelCurrentWindSpeed.setToolTip('Location\'s Current Wind Speed')

        # align weather 'fluff' to right
        self.labelCurrentCond.setAlignment(Qt.AlignRight)
        self.labelCurrentFeelsLike.setAlignment(Qt.AlignRight)
        self.labelCurrentWindSpeed.setAlignment(Qt.AlignRight)

        # position widgets onto grid; addWidget(widget_name, row, col, rowSpan, colSpan)
        self.currentWeatherGridLayout.addWidget(self.labelLocationName, 0, 0, 1, 14)
        self.currentWeatherGridLayout.addWidget(self.labelDateAndTime, 1, 0, 1, 14)
        self.currentWeatherGridLayout.addWidget(self.widgetWeatherStatus, 2, 0, 6, 6)
        self.currentWeatherGridLayout.addWidget(self.labelCurrentTemper, 2, 3, 6, 6)
        self.currentWeatherGridLayout.addWidget(self.labelCurrentCond, 0, 16)
        self.currentWeatherGridLayout.addWidget(self.labelCurrentFeelsLike, 6, 16)
        self.currentWeatherGridLayout.addWidget(self.labelCurrentWindSpeed, 7, 16)

        # display weather info in a frame widget
        self.currentWeatherFrame.setLayout(self.currentWeatherGridLayout)
        self.addWidget(self.currentWeatherFrame, 0, 0)

    # note: display test
    def tomorrowWeatherDisplay(self, api):
        if str(self.obj['temp-unit']) == 'fahrenheit':
            tmrwTemp = api.onecall.forecast_daily[1].temperature('fahrenheit')
            self.FC = 'F'
        else:
            tmrwTemp = api.onecall.forecast_daily[1].temperature('celsius') 
            self.FC = 'C'
        tmrwWind = api.onecall.forecast_daily[1].wnd 

        # add shadow for elegance
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(0,0,0,127))
        self.shadow.setBlurRadius(8)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)

        # remove widgets in layout when updating
        self.removeLayoutWidgets(self.tomorrowWeatherGridLayout)

        # set frame style
        self.tomorrowWeatherFrame.setGraphicsEffect(self.shadow)
        self.tomorrowWeatherFrame.setFrameStyle(QFrame.StyledPanel)
        self.tomorrowWeatherFrame.setFixedWidth(450)
        self.tomorrowWeatherFrame.setMaximumHeight(200)
        self.tomorrowWeatherFrame.setStyleSheet('''
        QFrame {
            background-color: rgb(100, 100, 194);
            border: none;
            color: #fff;
            font-family: "FontAwesome";
        }

        QLabel {
            background: none;
        }

        QLabel#heading {
            font-size: 15pt;
        }

        QLabel#tmrw_temper {
            font-size: 25pt;
        }
        ''')

        # note: some labels in this widget may be hardcoded
        
        # label for tomorrow
        self.labelTomorrow = QLabel('Tomorrow\'s Forecast')
        self.labelTomorrow.setObjectName('heading')
        self.labelTomorrow.setToolTip('Tomorrow\'s Forecast')
        
        # widget with image of weather
        searchMode = "tomorrow"
        self.tmrwWidgetWeatherStatus = qta.IconWidget()
        self.tmrwWidgetWeatherStatus.setIconSize(QSize(60, 60))
        self.iconWeatherStatus = self.getWeatherStatus(api, searchMode, 0, True) #using 0 as a placeholder to be able to implement the day of the week 
        self.tmrwWidgetWeatherStatus.setIcon(self.iconWeatherStatus)
        self.tmrwWidgetWeatherStatus.setToolTip('Tomorrow\'s Weather')

        # label of tomorrow's temperature
        self.labelTomorrowTemper = QLabel(str(round(tmrwTemp.get('day'))) + chr(0xb0) + self.FC)
        self.labelTomorrowTemper.setObjectName('tmrw_temper')
        self.labelTomorrowTemper.setToolTip('Tomorrow\'s Current Temperature')

        # label of tpmorrow's condition
        tmrCond = str(api.onecall.forecast_daily[1].detailed_status)
        self.labelTomorrowCond = QLabel(tmrCond[0].upper() + tmrCond[1:])
        self.labelTomorrowLowHigh = QLabel(str(round(tmrwTemp.get('min'))) + chr(0xb0) + self.FC + ' | ' + str(round(tmrwTemp.get('max'))) + chr(0xb0) + self.FC)
        self.labelTomorrowWindSpeed = QLabel('Wind speed ' + str(tmrwWind.get('speed')) + ' mph')

        # tooltips to guide user
        self.labelTomorrowCond.setToolTip('Tomorrow\'s Weather Condition')
        self.labelTomorrowLowHigh.setToolTip('Tomorrow\'s Low and High Temperatures')
        self.labelTomorrowWindSpeed.setToolTip('Tomorrow\'s Wind Speed')

        # align weather 'fluff' to right
        self.labelTomorrowCond.setAlignment(Qt.AlignRight)
        self.labelTomorrowLowHigh.setAlignment(Qt.AlignRight)
        self.labelTomorrowWindSpeed.setAlignment(Qt.AlignRight)

        # position widgets onto grid; addWidget(widget_name, row, col, rowSpan, colSpan)
        self.tomorrowWeatherGridLayout.addWidget(self.labelTomorrow, 0, 0, 1, 14)
        self.tomorrowWeatherGridLayout.addWidget(self.tmrwWidgetWeatherStatus, 1, 0, 6, 6)
        self.tomorrowWeatherGridLayout.addWidget(self.labelTomorrowTemper, 1, 3, 6, 6)
        self.tomorrowWeatherGridLayout.addWidget(self.labelTomorrowCond, 0, 16)
        self.tomorrowWeatherGridLayout.addWidget(self.labelTomorrowLowHigh, 5, 16)
        self.tomorrowWeatherGridLayout.addWidget(self.labelTomorrowWindSpeed, 6, 16)

        # display weather info in a frame widget
        self.tomorrowWeatherFrame.setLayout(self.tomorrowWeatherGridLayout)
        self.addWidget(self.tomorrowWeatherFrame, 1, 0)

    # note: display test
    def currentCityWeatherDisplay(self, api):
        if str(self.obj['temp-unit']) == 'fahrenheit':
            temp = api.onecall.current.temperature('fahrenheit')
            self.FC = 'F'
        else: 
            temp = api.onecall.current.temperature('celsius')
            self.FC = 'C'
        wind = api.onecall.current.wnd
        time = Time(api.onecall.timezone)
        
        if str(self.obj['time']) == "standard":
            self.timeStr = time.location12Str
        else:
            self.timeStr = time.location24Str

        # get time of geolocated city (e.g. Knoxville, TN)
        self.isDayGeo = True
        if (time.locationDateTime.hour < 20 and time.locationDateTime.hour > 8):
            self.isDayGeo = True
        else:
            self.isDayGeo = False

        # fixes big with location-dot char not displaying on MacOS
        if sys.platform.startswith('darwin'):
            self.locationChar = chr(0xf041)
        else:
            self.locationChar = chr(0xf3c5)

        # add shadow for elegance
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(0,0,0,127))
        self.shadow.setBlurRadius(8)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)

        # remove widgets in layout when updating
        self.removeLayoutWidgets(self.currentCityWeatherGridLayout)

        # set frame style
        self.currentCityWeatherFrame.setGraphicsEffect(self.shadow)
        self.currentCityWeatherFrame.setFrameStyle(QFrame.StyledPanel)
        self.currentCityWeatherFrame.setFixedWidth(450)
        self.currentCityWeatherFrame.setMaximumHeight(200)
        
        ccFrameBG = None

        if self.ccImagePath == None:
            ccFrameBG = '''
            QFrame {
                background-color: #131619;
                border: none;
                color: #fff;
                font-family: "FontAwesome";
            }'''
        else:
            self.ccImagePath = self.ccImagePath.replace('\\', '/') # curse Windows, Linux is far better
            ccFrameBG = '''
            QFrame {
                background-image: url(''' + self.ccImagePath + ''');
                border: none;
                color: #fff;
                font-family: "FontAwesome";
            }'''

        ccFrameContents = '''
        QLabel {
            background: none;
        }

        QLabel#heading {
            font-size: 15pt;
        }

        QLabel#cur_temper {
            font-size: 25pt;
        }
        '''

        self.currentCityWeatherFrame.setStyleSheet(ccFrameBG + ccFrameContents)

        # note: some labels in this widget may be hardcoded
        self.currentCityLabel = QLabel("Current City")
        self.currentCityLabel.setObjectName('heading')
        self.currentCityLabel.setToolTip('Current City (Nearest Found)')
        
        # label for location name
        self.labelLocationName = QLabel(self.locationChar + '  ' + api.location + ', ' + api.country)
        self.labelLocationName.setObjectName('heading')
        self.labelLocationName.setToolTip('Nearest Location\'s Name')
        
        # label for location's date and time
        self.labelDateAndTime = QLabel(self.timeStr)
        self.labelDateAndTime.setToolTip('Nearest Location\'s Current Date and Time')
        
        # widget with image of weather
        searchMode = "today"
        self.widgetWeatherStatus = qta.IconWidget()
        self.widgetWeatherStatus.setIconSize(QSize(60, 60))
        self.iconWeatherStatus = self.getWeatherStatus(api, searchMode, 0, self.isDayGeo) #using 0 as a placeholder to be able to implement day of the week
        self.widgetWeatherStatus.setIcon(self.iconWeatherStatus)
        self.widgetWeatherStatus.setToolTip('Nearest Location\'s Current Weather')

        # label of current temperature
        self.labelCurrentTemper = QLabel(str(round(temp.get('temp'))) + chr(0xb0) + self.FC)
        self.labelCurrentTemper.setObjectName('cur_temper')
        self.labelCurrentTemper.setToolTip('Nearest Location\'s Current Temperature')

        # label of current condition
        currentCond = str(api.onecall.current.detailed_status)
        self.labelCurrentCond = QLabel(currentCond[0].upper() + currentCond[1:])
        self.labelCurrentLowHigh = QLabel(str(temp.get('min')) + chr(0xb0) + self.FC + ' | ' + str(temp.get('max')) + chr(0xb0) + self.FC)
        self.labelCurrentFeelsLike = QLabel('Feels like ' + str(round(temp.get('feels_like'))) + chr(0xb0) + self.FC)
        self.labelCurrentWindSpeed = QLabel('Wind speed ' + str(wind.get('speed')) + ' mph')

        # tooltips to guide user
        self.labelCurrentCond.setToolTip('Nearest Location\'s Current Weather Condition')
        self.labelCurrentFeelsLike.setToolTip('Nearest Location\'s Current \'Feels Like\' Temperature')
        self.labelCurrentWindSpeed.setToolTip('Nearest Location\'s Current Wind Speed')

        # align weather 'fluff' to right
        self.labelCurrentCond.setAlignment(Qt.AlignRight)
        self.labelCurrentFeelsLike.setAlignment(Qt.AlignRight)
        self.labelCurrentWindSpeed.setAlignment(Qt.AlignRight)

        # position widgets onto grid; addWidget(widget_name, row, col, rowSpan, colSpan)
        self.currentCityWeatherGridLayout.addWidget(self.currentCityLabel, 0, 0, 1, 14)
        self.currentCityWeatherGridLayout.addWidget(self.labelLocationName, 1, 0, 1, 14)
        self.currentCityWeatherGridLayout.addWidget(self.labelDateAndTime, 2, 0, 1, 14)
        self.currentCityWeatherGridLayout.addWidget(self.widgetWeatherStatus, 3, 0, 6, 6)
        self.currentCityWeatherGridLayout.addWidget(self.labelCurrentTemper, 3, 3, 6, 6)
        self.currentCityWeatherGridLayout.addWidget(self.labelCurrentCond, 0, 16)
        self.currentCityWeatherGridLayout.addWidget(self.labelCurrentFeelsLike, 6, 16)
        self.currentCityWeatherGridLayout.addWidget(self.labelCurrentWindSpeed, 7, 16)

        # display weather info in a frame widget
        self.currentCityWeatherFrame.setLayout(self.currentCityWeatherGridLayout)
        self.addWidget(self.currentCityWeatherFrame, 2, 0)

    # Displaying the weekly weather forecast. 
    def weekForecastWeatherDisplay(self, api):
        
        self.removeLayoutWidgets(self.weeklyDisplayBox)        

        headingLayout = QGridLayout()
        headingFrame = QFrame()

        # add shadow for elegance
        headingLayout.shadow = QGraphicsDropShadowEffect()
        headingLayout.shadow.setColor(QColor(0,0,0,127))
        headingLayout.shadow.setBlurRadius(8)
        headingLayout.shadow.setXOffset(5)
        headingLayout.shadow.setYOffset(5)

        headingFrame.setGraphicsEffect(headingLayout.shadow)
        headingFrame.setMinimumWidth(450)
        headingFrame.setFrameStyle(QFrame.StyledPanel)
        headingFrame.setStyleSheet('''
        QFrame {
            background-color: rgb(100, 100, 194); /* rgb(120, 30, 94); */
            border: none;
            color: #fff;
            font-family: "FontAwesome";
        }

        QLabel {
            background: none;
        }

        QLabel#heading {
            font-size: 15pt;
        }

        QLabel#tmrw_temper {
            font-size: 25pt;
        }
        ''')

        headingLayout.heading = QLabel("Weekly Weather Forecast") 
        headingLayout.heading.setObjectName('heading')
        headingLayout.heading.setToolTip("The coming Week's Weather:")
        headingLayout.addWidget(headingLayout.heading, 0, 0, 1, 14)
        headingFrame.setLayout(headingLayout)
        self.weeklyDisplayBox.addWidget(headingFrame)

        for day in range(1,8) :
            # set frame and style
            self.oneDayLayout = QGridLayout()
            oneDayFrame = QFrame()

            # add shadow for elegance
            self.oneDayLayout.shadow = QGraphicsDropShadowEffect()
            self.oneDayLayout.shadow.setColor(QColor(0,0,0,127))
            self.oneDayLayout.shadow.setBlurRadius(8)
            self.oneDayLayout.shadow.setXOffset(5)
            self.oneDayLayout.shadow.setYOffset(5)

            oneDayFrame.setGraphicsEffect(self.oneDayLayout.shadow)
            oneDayFrame.setMinimumWidth(450)
            oneDayFrame.setFrameStyle(QFrame.StyledPanel)
            oneDayFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(100, 100, 194); /* rgb(120, 30, 94); */
                border: none;
                color: #fff;
                font-family: "FontAwesome";
            }

            QLabel {
                background: none;
            }

            QLabel#heading {
                font-size: 15pt;
            }

            QLabel#tmrw_temper {
                font-size: 25pt;
            }
            ''')
            
            # note: some labels in this widget may be hardcoded
            # label for week
            # note: indexing into list of weekdays with '+ day'
            nameOfWeekday = self.getWeekday((datetime.today().weekday() + day) % 7)
            self.oneDayLayout.labelWeek = QLabel(nameOfWeekday + "\'s Forecast") 
            self.oneDayLayout.labelWeek.setObjectName('heading')
            self.oneDayLayout.labelWeek.setToolTip(nameOfWeekday + '\'s Forecast')

            if str(self.obj['temp-unit']) == 'fahrenheit':
                weekTemp = api.onecall.forecast_daily[day].temperature('fahrenheit')
                self.FC = 'F'
            else:
                weekTemp = api.onecall.forecast_daily[day].temperature('celsius') 
                self.FC = 'C'
            weekWind = api.onecall.forecast_daily[day].wnd

            # widget with image of weather
            searchMode = "week"
            self.oneDayLayout.weekWidgetWeatherStatus = qta.IconWidget()
            self.oneDayLayout.weekWidgetWeatherStatus.setIconSize(QSize(60, 60))
            self.oneDayLayout.iconWeatherStatus = self.getWeatherStatus(api, searchMode, day, True)
            self.oneDayLayout.weekWidgetWeatherStatus.setIcon(self.oneDayLayout.iconWeatherStatus)
            self.oneDayLayout.weekWidgetWeatherStatus.setToolTip(nameOfWeekday + '\'s Weather')

            # label of tommorow's temperature
            self.oneDayLayout.labelWeekTemper = QLabel(str(round(weekTemp.get('day'))) + chr(0xb0) + self.FC)
            self.oneDayLayout.labelWeekTemper.setObjectName('tmrw_temper')
            self.oneDayLayout.labelWeekTemper.setToolTip(nameOfWeekday + '\'s Current Temperature')

            # label of tommorow's condition
            tmrCond = str(api.onecall.forecast_daily[day].detailed_status)
            self.oneDayLayout.labelWeekCond = QLabel(tmrCond[0].upper() + tmrCond[1:])
            self.oneDayLayout.labelWeekLowHigh = QLabel(str(round(weekTemp.get('min'))) + chr(0xb0) + ' | ' + str(round(weekTemp.get('max'))) + chr(0xb0))
            self.oneDayLayout.labelWeekWindSpeed = QLabel('Wind speed ' + str(weekWind.get('speed')) + ' mph')

            # tooltips to guide user
            self.oneDayLayout.labelWeekCond.setToolTip(nameOfWeekday + '\'s Weather Condition')
            self.oneDayLayout.labelWeekLowHigh.setToolTip(nameOfWeekday + '\'s Low and High Temperatures')
            self.oneDayLayout.labelWeekWindSpeed.setToolTip(nameOfWeekday + '\'s Wind Speed')

            # align weather 'fluff' to right
            self.oneDayLayout.labelWeekCond.setAlignment(Qt.AlignRight)
            self.oneDayLayout.labelWeekLowHigh.setAlignment(Qt.AlignRight)
            self.oneDayLayout.labelWeekWindSpeed.setAlignment(Qt.AlignRight)

            # position widgets onto grid; addWidget(widget_name, row, col, rowSpan, colSpan)
            self.oneDayLayout.addWidget(self.oneDayLayout.labelWeek, 0, 0, 1, 14)
            self.oneDayLayout.addWidget(self.oneDayLayout.weekWidgetWeatherStatus, 1, 0, 6, 6)
            self.oneDayLayout.addWidget(self.oneDayLayout.labelWeekTemper, 1, 3, 6, 6)
            self.oneDayLayout.addWidget(self.oneDayLayout.labelWeekCond, 0, 16)
            self.oneDayLayout.addWidget(self.oneDayLayout.labelWeekLowHigh, 5, 16)
            self.oneDayLayout.addWidget(self.oneDayLayout.labelWeekWindSpeed, 6, 16)

            oneDayFrame.setLayout(self.oneDayLayout)
            self.weeklyDisplayBox.addWidget(oneDayFrame)
        
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setFixedHeight(600)
        scrollArea.setFixedWidth(500)
        self.weekWeatherFrame.setLayout(self.weeklyDisplayBox)
        scrollArea.setWidget(self.weekWeatherFrame)
        scrollArea.grabGesture
        self.addWidget(scrollArea, 0, 1, 3, 7, alignment= Qt.AlignLeft) 

    # gets weather status and returns a qta image
    def getWeatherStatus(self, api, searchMode, weekIndex, isDay):

        stat = None
        if searchMode ==  "today":
            stat = str(api.onecall.current.detailed_status)
        elif searchMode == "tomorrow" :
            stat = str(api.onecall.forecast_daily[1].detailed_status)
        else :
            stat = str(api.onecall.forecast_daily[weekIndex].detailed_status)

        # return icon depending on status
        if (stat == 'clear sky'):
            if isDay == True:
                return qta.icon('fa5s.sun', color='white') # day
            else:
                return qta.icon('fa5.moon', color='white') # night
        elif (stat == 'few clouds'):
            if isDay == True:
                return qta.icon('mdi.weather-partly-cloudy', color='white') # day
            else:
                return qta.icon('mdi.weather-night-partly-cloudy', color='white') # night
        elif (stat == 'scattered clouds' or stat == 'overcast clouds'):
            return qta.icon('mdi.weather-cloudy', color='white') # day / night
        elif (stat == 'broken clouds'):
            return qta.icon('mdi.weather-cloudy', 'mdi.weather-cloudy', options=[{'offset': (-0.5, -0.25), 'scale_factor':0.75, 'color':'white'}, {'color':'white'}]) # day / night
        elif (stat == 'shower rain' or stat == 'heavy intensity rain'):
            return qta.icon('mdi.weather-pouring', color='white') # day / night
        elif (stat == 'rain' or stat == 'light rain' or stat == 'moderate rain'):
            return qta.icon('mdi.weather-rainy', color='white') # day / night
        elif (stat == 'thunderstorm'):
            return qta.icon('mdi.weather-lightning', color='white') # day / night
        elif (stat == 'snow'):
            return qta.icon('mdi.weather-snowy', color='white') # day / night
        elif (stat == 'mist'):
            return qta.icon('mdi.weather-fog', color='white') # day / night

        # default (weather cannot be determined)
        return qta.icon('mdi.cloud-question', color='white')

    def alert(self, message):
        widget = QWidget()
        alert = QMessageBox.warning(widget, "Warning", message)

    # actually shows loading indication when user searches a city or tabs to another city 
    def showLoading(self):
        self.splash.showMessage("<h2><font color='white'><i>Loading...</i></font></h2>", Qt.AlignTop | Qt.AlignCenter, Qt.black)
        self.splash.show()

    # hides the loading indication when the desired city is displayed
    def hideLoading(self):
        self.splash.hide()

    # this instantiates an apiWorker and process api request on separate thread
    # send api object to weather_result
    def upd_weather(self, location, cc_location):
        self.getSettings()
        self.showLoading()
        worker = apiWorker(location, cc_location)
        worker.signals.result.connect(self.weather_result)
        if (self.alert_count == 0): #fixes issue of multiple warnings popping up
            worker.signals.error.connect(self.alert)
            self.alert_count += 1
        self.threadpool.start(worker)

    # this updates the QLabels created in setupDisplay with new weather data from upd_weather
    def weather_result(self, api, ccapi):
        self.currentWeatherDisplay(api)
        self.tomorrowWeatherDisplay(api)
        # this uss ccapi for current cities weather data
        self.currentCityWeatherDisplay(ccapi)
        self.weekForecastWeatherDisplay(api)
        self.hideLoading()

    # this removes child widgets from a weather layout before adding new widgets
    # Reference: https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    def removeLayoutWidgets(self, weatherLayout):
        while weatherLayout.count():
            child = weatherLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # get users current city
    def getUserCityStr(self):
        currentCity = geocoder.ip('me')
        if currentCity.current_result.country == 'US':
            currentState = stateStr_to_abbrev.get(currentCity.current_result.state)
            currentCityStr = currentCity.current_result.city + ", " + currentState
        else:
            currentCityStr = currentCity.current_result.city + ", " + currentCity.current_result.country
        return currentCityStr

    def getWeekday(self, day) : 
        if (day == 0) :
            return "Monday"
        elif(day == 1): 
            return "Tuesday"
        elif(day == 2): 
            return "Wednesday"
        elif(day == 3): 
            return "Thursday"
        elif(day == 4): 
            return "Friday"
        elif(day == 5): 
            return "Saturday"
        else : #day == 6 
            return "Sunday"