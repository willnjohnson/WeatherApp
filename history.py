'''
    history.py
    TMWRK

    History contains:
        Display for historical data of current selected city
'''

import os
from types import new_class
from PyQt5 import QtCore
from PyQt5.QtCore import QMetaMethod, Qt
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLabel, QLineEdit, QMainWindow, QDialog, QDialogButtonBox, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout
from PyQt5.sip import delete
from qt_material import apply_stylesheet
from tabs import Tabs
from historicaldata import HistoricalData
from historygraph import HistoryGraph

class History(QDialog, QMainWindow):
    def __init__(self, window):
        super(History, self).__init__(window)

        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)
        
        # but parent window can reflect changes when applying settings like theme
        self.book = window

        self.userIn = HistoryUserIn()
        self.setLayout(self.userIn.layout)

class HistoryUserIn:
    def __init__(self):
        self.data = HistoricalData()

        self.layout = QGridLayout()
        self.locTypeLable = QLabel()
        self.locLabel = QLabel()
        self.startDate = QLabel()
        self.endDate = QLabel()
        self.unitsLabel = QLabel()
        self.dataCatLabel = QLabel()
        self.badLocation = QLabel()
        self.hitEnter = QLabel()
        self.locCatDrop = QComboBox()
        self.dataCats = QComboBox()
        self.units = QComboBox()
        self.locBox = QLineEdit()
        self.sDay = QLineEdit()
        self.sMonth = QLineEdit()
        self.sYear = QLineEdit ()
        self.eDay = QLineEdit()
        self.eMonth = QLineEdit()
        self.eYear = QLineEdit ()
        self.graphButton = QPushButton('Create Graph')

        self.graph = HistoryGraph()

        self.graphButton.hide()
        self.initWindow()

    def initWindow(self):
        self.startDate.setText('Enter Start Date(MM/DD/YYYY):')
        self.endDate.setText('Enter End Date(MM/DD/YYYY):')
        self.unitsLabel.setText('Select Units:')
        self.badLocation.setText("Bad location entered. Please Try again.")
        self.locTypeLable.setText("Select Location Type:")
        self.hitEnter.setText("Hit Enter")

        self.sDay.setMaxLength(2)
        self.sMonth.setMaxLength(2) 
        self.sYear.setMaxLength(4)
        self.eDay.setMaxLength(2)
        self.eMonth.setMaxLength(2) 
        self.eYear.setMaxLength(4)       
     
        self.units.addItem('Units')
        self.units.addItem('Standard')
        self.units.addItem('Metric')
        
        self.layout.setRowStretch(50,1)
        self.layout.setColumnStretch(50,1)

        self.data.getLocationCategories()
        self.locCatDrop.addItem('Location Types')
        for [cat, id] in self.data.locCats:
            self.locCatDrop.addItem(cat)

        
        self.layout.addWidget(self.locTypeLable, 0, 0,)
        self.layout.addWidget(self.locCatDrop, 1, 0)
        self.layout.addWidget(self.badLocation, 1, 2)
        self.layout.addWidget(self.hitEnter, 1, 2)

        self.badLocation.hide()
        self.hitEnter.hide()

        self.locCatDrop.setAccessibleName("Location Categories")
        

        self.count = 0
        self.locCatDrop.currentIndexChanged.connect(self.locationSelect)
        self.dataCats.currentIndexChanged.connect(self.setDataType)
        self.units.currentIndexChanged.connect(self.setUnits)
        self.graphButton.clicked.connect(self.createGraph)
    
    def locationSelect(self, i):
        self.data.locationType = self.data.locCats[i-1][1]
        text = 'Enter ' + self.data.locCats[i-1][0] + ':'
        self.locLabel.setText(text)
        
        self.layout.addWidget(self.locLabel, 0, 1)
        self.layout.addWidget(self.locBox, 1, 1)
        self.badLocation.hide()
        self.hitEnter.show()
        self.locBox.returnPressed.connect(self.dataCatSelect)


    def dataCatSelect(self):
        self.data.location = self.locBox.text()
        self.data.getDataCategories()
        if self.data.isValid:
            self.hitEnter.hide()
            self.badLocation.hide()
            self.locCatDrop.setEnabled(False)
            self.locBox.setEnabled(False)

            self.dataCatLabel.setText('Select Data Category:')
            self.dataCats.addItem('Data Categories')
            for [data, id] in self.data.dataCats:  
                    self.dataCats.addItem(data)

            self.graphButton.show()

            self.layout.addWidget(self.dataCatLabel, 2, 0)
            self.layout.addWidget(self.dataCats, 3, 0)
            self.layout.addWidget(self.unitsLabel, 2, 1)
            self.layout.addWidget(self.units, 3, 1)
            self.layout.addWidget(self.startDate, 4, 0)
            self.layout.addWidget(self.endDate, 5, 0)
            self.layout.addWidget(self.sMonth, 4, 1)
            self.layout.addWidget(self.sDay, 4, 2)
            self.layout.addWidget(self.sYear, 4, 3)
            self.layout.addWidget(self.eMonth, 5, 1)
            self.layout.addWidget(self.eDay, 5, 2)
            self.layout.addWidget(self.eYear, 5, 3)
            self.layout.addWidget(self.graphButton, 6, 3)
        else:
            self.hitEnter.hide()
            self.badLocation.show()

    def setDataType(self, i):
        self.data.dataType = self.data.dataCats[i-1][1]
        self.graph.setLabels('Dates', self.data.dataCats[i-1][0])

    def setUnits(self, i):
        if i == 2:
            self.data.units = 'metric'
        else:
            self.data.units = 'standard'

    def createGraph(self):
        self.data.setStartDate(self.sYear.text(), self.sMonth.text(), self.sDay.text())
        self.data.setEndDate(self.eYear.text(), self.eMonth.text(), self.eDay.text())
        self.data.getData()

        
        self.graph.setValues(self.data.dataList)

        self.graph.createGraph()

        graphLayout = QVBoxLayout()
        graphLayout.addWidget(self.graph.canvas)
        self.layout.addChildLayout(graphLayout)