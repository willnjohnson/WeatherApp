'''
    dining.py
    TMWRK

    Open browser with the top rated restaurants per yelp.com

'''

import json
import os
import urllib
from PyQt5.QtGui import QColor, QIcon, QPixmap
import qtawesome
from yelpapi import YelpAPI
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect, QGridLayout, QLabel, QMainWindow, QDialog, QDialogButtonBox, QHBoxLayout, QMainWindow, QMessageBox, QPushButton, QScrollArea, QVBoxLayout
from qt_material import apply_stylesheet
from tabs import Tabs

YELP_API_KEY = "iHXQoOowzlqjKNzSBSAGkPZ0bfJIjzGRyOgsdXX4E7wU8Q9yrqmEePkxSThIRUdqZFUbAdM_DKVB7lUeV_x5Ao0NFY40d0721MMO9aCWHh-Kzk2Po0gs24QQUk6AYXYx"

class Dining(QDialog, QMainWindow):

    def __init__(self, window, location):
        super(Dining, self).__init__(window)

        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)

        # but parent window can reflect changes when applying settings like theme
        self.book = window
        self.error = False

        self.diningLayout = DiningDisplay(location)

        self.setFixedHeight(600)
        self.setFixedWidth(600)
        self.setLayout(self.diningLayout)



class DiningDisplay(QGridLayout):
    def __init__(self, location):
        super(DiningDisplay, self).__init__()

        try:
            self.response = self.search(location)
        except Exception as e:
            self.showErrorMessage(e)
        else:
            self.diningDisplayBox = QVBoxLayout()
            self.diningFrame = QFrame()
            self.oneDiningLayout = QGridLayout()
            self.diningDisplay(self.response)

    def diningDisplay(self, response):
        numbusinesses = len(response['businesses'])
        for i in range(numbusinesses):

            self.oneDiningLayout = QGridLayout()
            oneDiningFrame = QFrame()

            # add shadow for elegance
            self.oneDiningLayout.shadow = QGraphicsDropShadowEffect()
            self.oneDiningLayout.shadow.setColor(QColor(0,0,0,127))
            self.oneDiningLayout.shadow.setBlurRadius(8)
            self.oneDiningLayout.shadow.setXOffset(5)
            self.oneDiningLayout.shadow.setYOffset(5)

            oneDiningFrame.setGraphicsEffect(self.oneDiningLayout.shadow)
            oneDiningFrame.setMaximumHeight(75)
            oneDiningFrame.setMinimumWidth(450)
            oneDiningFrame.setFrameStyle(QFrame.StyledPanel)
            oneDiningFrame.setStyleSheet('''
            QFrame {
                background-color: rgb(150, 150, 150);
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

            hyperlink = response['businesses'][i]['url']

            self.oneDiningLayout.nameLabel = QLabel(response['businesses'][i]['name'])
            self.oneDiningLayout.nameLabel.setWordWrap(True)
            self.oneDiningLayout.nameLabel.setObjectName('heading')
            self.oneDiningLayout.nameLabel.setToolTip(response['businesses'][i]['name'])

            self.oneDiningLayout.ratingLabel = QLabel('Rating: ' + str(response['businesses'][i]['rating']) + " " + chr(0xf005))
            self.oneDiningLayout.ratingLabel.setObjectName('heading')
            self.oneDiningLayout.ratingLabel.setToolTip('Yelp rating of ' + response['businesses'][i]['name'])
            
            self.oneDiningLayout.linkLabel = QLabel('<a href=\"{hyperlink}\"style=\"color: white;\">Yelp Page</a>'.format(hyperlink=hyperlink))
            self.oneDiningLayout.linkLabel.setOpenExternalLinks(True)
            self.oneDiningLayout.linkLabel.setAlignment(Qt.AlignRight)

            self.oneDiningLayout.addWidget(self.oneDiningLayout.nameLabel, 0, 0, 1, 2)
            self.oneDiningLayout.addWidget(self.oneDiningLayout.ratingLabel, 0, 8, 1, 2)
            self.oneDiningLayout.addWidget(self.oneDiningLayout.linkLabel, 0, 8, 1, 2)

            oneDiningFrame.setLayout(self.oneDiningLayout)
            self.diningDisplayBox.addWidget(oneDiningFrame)

        # make scrollable
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setFixedHeight(600)
        scrollArea.setWidget(self.diningFrame)
        scrollArea.grabGesture
        self.addWidget(scrollArea) 

        self.diningFrame.setLayout(self.diningDisplayBox)
        self.addWidget(self.diningFrame)

    def search(self, location):
        self.yelp_api = YelpAPI(YELP_API_KEY)
        response = self.yelp_api.search_query(categories='Restaurants', location=location, sort_by='rating')
        return response 

    def showErrorMessage(self, error):
        self.errorLabel = QLabel(error.args[0])
        self.errorLabel.setStyleSheet('''
        QLabel {
            background-color: rgb(150, 150, 150);
            border: none;
            color: #fff;
            font-family: "FontAwesome";
            font-size: 20pt;
        }
        ''')
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.setAlignment(Qt.AlignTop)
        self.errorLabel.setMaximumHeight(75)
        self.errorLabel.setMinimumWidth(450)
        self.errorLabel.adjustSize()
        self.errorLabel.setWordWrap(True)
        self.addWidget(self.errorLabel, 0, 0, 1, 2, alignment=Qt.AlignTop)