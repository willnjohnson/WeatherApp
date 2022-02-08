'''
    hourlyForecast.py
    TMWRK

    HourlyForecast contains:
        Display for hourly forecast data of current selected city
'''

import json
import os
from PyQt5.QtCore import QSize, Qt, QThreadPool
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWIDGETSIZE_MAX, QFrame, QGraphicsDropShadowEffect, QGridLayout, QLabel, QListWidget, QMainWindow, QDialog, QDialogButtonBox, QHBoxLayout, QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget
from pyowm.commons import databoxes
from qt_material import apply_stylesheet
from api import Api, apiWorker
from datetime import datetime
import qtawesome as qta

class HourlyForecast(QDialog, QMainWindow):
    def __init__(self, window, location):
        super(HourlyForecast, self).__init__(window)

        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)
        
        # but parent window can reflect changes when applying settings like theme
        self.book = window

        self.hourlyLayout = HourlyDisplay(location)
        
        self.setFixedHeight(600)
        self.setFixedWidth(600)
        self.setLayout(self.hourlyLayout)

class HourlyDisplay(QGridLayout):
    def __init__(self, location):
        super(HourlyDisplay, self).__init__()

        self.getSettings()

        # instantiates a pool of usable threads
        self.threadpool = QThreadPool()

        self.location = location
        # searched city api object
        api = Api(location)

        self.hourlyDisplayBox = QVBoxLayout()
        self.hourlyWeatherFrame = QFrame()
        self.oneHourLayout = QGridLayout()
        self.hourlyWeatherDisplay(api)

    def hourlyWeatherDisplay(self, api):

        for i in range(48):

            self.oneHourLayout = QGridLayout()
            oneHourFrame = QFrame()

            # add shadow for elegance
            self.oneHourLayout.shadow = QGraphicsDropShadowEffect()
            self.oneHourLayout.shadow.setColor(QColor(0,0,0,127))
            self.oneHourLayout.shadow.setBlurRadius(8)
            self.oneHourLayout.shadow.setXOffset(5)
            self.oneHourLayout.shadow.setYOffset(5)
        
            oneHourFrame.setGraphicsEffect(self.oneHourLayout.shadow)
            oneHourFrame.setMaximumHeight(75)
            oneHourFrame.setMinimumWidth(450)
            oneHourFrame.setFrameStyle(QFrame.StyledPanel)
            oneHourFrame.setStyleSheet('''
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

            QLabel#hour_temper {
                font-size: 25pt;
            }
            ''')

            self.ts = api.onecall.forecast_hourly[i].ref_time

            # 12 hour time
            if str(self.obj['time']) == "standard":
                self.timeStr = datetime.utcfromtimestamp(self.ts).strftime('%m/%d - %I:%M %p')
            # 24 hour time
            else:
                self.timeStr = datetime.utcfromtimestamp(self.ts).strftime('%m/%d - %H:%M')

            self.oneHourLayout.labelHour = QLabel(self.timeStr)
            self.oneHourLayout.labelHour.setObjectName("heading")   
            self.oneHourLayout.labelHour.setToolTip('Forecast in ' + str(i) + " hours")

            self.oneHourLayout.labelStatus = QLabel(api.onecall.forecast_hourly[i].detailed_status)
            self.oneHourLayout.labelStatus.setObjectName("heading")

            if str(self.obj['temp-unit']) == 'fahrenheit':
                hourTemp = api.onecall.forecast_hourly[i].temperature('fahrenheit')
                self.FC = 'F'
            else:
                hourTemp = api.onecall.forecast_hourly[i].temperature('celsius') 
                self.FC = 'C'

            self.oneHourLayout.labelTemp = QLabel(str(round(hourTemp['temp'])) + "°" + self.FC)
            self.oneHourLayout.labelTemp.setObjectName("hour_temper")
            self.oneHourLayout.labelTemp.setToolTip('Temperature for' + str(i) + ":00")

            self.oneHourLayout.hourWidgetWeatherStatus = qta.IconWidget()
            self.oneHourLayout.hourWidgetWeatherStatus.setIconSize(QSize(60, 60))
            self.oneHourLayout.iconWeatherStatus = self.getWeatherStatus(api, "hourly", i)
            self.oneHourLayout.hourWidgetWeatherStatus.setIcon(self.oneHourLayout.iconWeatherStatus)
            self.oneHourLayout.hourWidgetWeatherStatus.setToolTip('Weather status for' + str(i) + ":00")

            self.oneHourLayout.addWidget(self.oneHourLayout.labelHour, 0, 0, 1, 2)
            self.oneHourLayout.addWidget(self.oneHourLayout.hourWidgetWeatherStatus, 0, 3, 1, 2)
            self.oneHourLayout.addWidget(self.oneHourLayout.labelStatus, 0, 4, 1, 2)
            self.oneHourLayout.addWidget(self.oneHourLayout.labelTemp, 0, 6, 1, 2)

            oneHourFrame.setLayout(self.oneHourLayout)
            self.hourlyDisplayBox.addWidget(oneHourFrame)

        # make scrollable
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setFixedHeight(600)
        scrollArea.setWidget(self.hourlyWeatherFrame)
        scrollArea.grabGesture
        self.addWidget(scrollArea) 

        self.hourlyWeatherFrame.setLayout(self.hourlyDisplayBox)

        self.addWidget(self.hourlyWeatherFrame)

    #updates settings, used for Fahrenheit/Celsius Toggle after settings applied
    def getSettings(self):

        # path to settings.json
        main_path = os.path.dirname(os.path.abspath(__file__))
        settings_path = main_path + '/settings.json'
        
        # load settings stored in settings.json
        with open(settings_path, 'r') as fin:
            data = fin.read()

        self.obj = json.loads(data)
        
        # close file for reading from settings.json
        fin.close()
        
                
    # gets weather status and returns a qta image
    def getWeatherStatus(self, api, searchMode, weekIndex):

        stat = None
        #if searchMode ==  "today":
        #    stat = str(api.onecall.current.detailed_status)
        #elif searchMode == "tomorrow" :
        #    stat = str(api.onecall.forecast_daily[1].detailed_status)
        #else :
        stat = str(api.onecall.forecast_hourly[weekIndex].detailed_status)

        # return icon depending on status
        if (stat == 'clear sky'):
            return qta.icon('fa5s.sun', color='white') # day
            return qta.icon('fa5.moon', color='white') # night
        elif (stat == 'few clouds'):
            return qta.icon('mdi.weather-partly-cloudy', color='white') # day
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