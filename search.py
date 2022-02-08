'''
    search.py
    TMWRK

    Search contains:
        Search bar where user can lookup city
'''
import os
import sys
import jsonhelper as jh
from PyQt5 import QtCore
from PyQt5.QtCore import QEvent, QPoint, Qt
import qtawesome as qta
from PyQt5.QtWidgets import QApplication, QFrame, QLineEdit, QListWidget, QMainWindow, QToolButton, QVBoxLayout

class Search(QVBoxLayout, QMainWindow):

    def __init__(self, window):
        super().__init__()

        self.app = window

        # create the search bar and embed clear button for search bar
        self.searchBar = QLineEdit()
        self.searchBar.setClearButtonEnabled(True)
        self.searchBar.setStyleSheet('font-weight: 500;')
        self.searchBar.findChild(QToolButton).setIcon(
            qta.icon('fa.square', 'fa.close', 
                options=[{'color':'#232629', 'opacity':0.33, 'scale_factor':1.25}, 
                {'color':'white', 'opacity': 0.9}]
            )
        )
        self.searchBar.addAction(
            qta.icon('fa.square', 'fa.search', 
                options=[{'color':'#232629', 'opacity':0.33, 'scale_factor':1.25}, 
                {'color':'#f5f5f5'}]
            ),
            QLineEdit.LeadingPosition
        )

        # Reference: https://github.com/ismailsunni/scripts/blob/master/autocomplete_from_url.py
        self.listWidget = QListWidget(self.searchBar)
        self.listWidget.setWindowFlags(Qt.Popup)
        self.listWidget.setFocusProxy(self.searchBar)
        self.listWidget.setMouseTracking(True)
        self.listWidget.setEditTriggers(QListWidget.NoEditTriggers)
        self.listWidget.setSelectionBehavior(QListWidget.SelectRows)
        self.listWidget.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.hide()

        # changed place holder to Knoxville since it is the current default city
        self.searchBar.setPlaceholderText("Knoxville, TN")
        self.addWidget(self.searchBar)

        # show dropdown
        self.searchBar.textChanged.connect(self.updateSearch)

        # detect actions of keypresses
        self.listWidget.installEventFilter(self)

    def updateSearch(self):
        if (len(self.searchBar.text())) > 1:
            self.letter_search = self.searchBar.text().lower()
            self.first_two_letters = ""
            self.first_two_letters = self.letter_search[0] + self.letter_search[1]
            
            # Example: user begins typing "Sa"
            # self.cityList = ['Salvador, BR', 'Samara, RU', 'San Antonio, TX', 'San Diego, CA', 'Sanaa, YM', 'Santa Cruz, BV', 'Santiago, CL', 'Santo Domingo, DR', 'Sao Paulo, BR', 'Sapporo, JP']
            # update self.cityList with the results
            self.cityList = []

            self.city_list()

            # we only show dropdown when there is AT LEAST 1 result in the list
            if (len(self.cityList) > 0):
                self.listWidget.clear()
                self.populateList()
                self.showListWidget()

        else:
            self.listWidget.clear()
            self.listWidget.hide()

    def city_list(self):
        #read json file:
        main_path = os.path.dirname(os.path.abspath(__file__))
        try:
            open(main_path + "/cities/" + self.first_two_letters + ".json", encoding="utf8")
        except OSError:
            return
       
        all_city_names_in_file = jh.fread("/cities/" + self.first_two_letters + ".json")

        count = 0
        #search list of cities in file for at most 10 cities (from all of the prefixes in the search entry)
        for element in all_city_names_in_file:
            e = element.lower()
            if (e.startswith(self.letter_search)): #if element starts with letter_search
                if count < 10:
                    #add to self.city_list
                    #get list of at most 10 cities that begins with [:n] where n is length of search entry
                    self.cityList.append(element) 
                    count += 1

        # ideally I want self.listWidget.setFixedHeight( [height of listWidget item] * count ) so I don't have to depend on an arbitrary value
        if (count < 5 ):
            self.listWidget.setFixedHeight(48*count)
        else:
            self.listWidget.setFixedHeight(180)

    def showListWidget(self):
        self.listWidget.move(self.searchBar.mapToGlobal(QPoint(0, self.searchBar.frameGeometry().height())))
        self.listWidget.setFixedWidth(self.searchBar.width())
        self.listWidget.show()

    def populateList(self):
        # add cities to list
        for c in self.cityList:
            self.listWidget.addItem(c)

    # Reference: https://github.com/ismailsunni/scripts/blob/master/autocomplete_from_url.py
    def eventFilter(self, object, event):
        if object != self.listWidget:
            return False

        if event.type() == QEvent.KeyPress and event.key() == QtCore.Qt.Key_Up and self.listWidget.item(0).isSelected():
            self.searchBar.setFocus()
            self.listWidget.clearSelection()
            return True

        if event.type() == QEvent.KeyPress and event.key() == QtCore.Qt.Key_Down and (len(self.listWidget.selectedItems()) == 0):
            self.listWidget.setCurrentItem(self.listWidget.item(-1))

        if event.type() == QEvent.MouseButtonPress:
            self.listWidget.hide()
            self.searchBar.setFocus()
            return True

        if event.type() == QEvent.KeyPress:
            consumed = False
            key = event.key()
            if key in [Qt.Key_Enter, Qt.Key_Return]:
                if self.listWidget.currentItem():
                    pass
                else:
                    self.app.get_searchbar_text()
                    self.searchBar.setFocus()
                    self.listWidget.hide()
            elif key == Qt.Key_Escape:
                self.searchBar.setFocus()
                self.listWidget.hide()
                self.app.setFocus(True)
                consumed = True
            elif key in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown]:
                pass
            else:
                self.searchBar.setFocus()
                self.searchBar.event(event)
            return consumed

        return False