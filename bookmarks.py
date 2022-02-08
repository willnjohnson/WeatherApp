'''
    bookmarks.py
    TMWRK

    Bookmarks contains:
        List of cities
        Buttons to arrange order of cities (up or down) or remove a city
        Buttons to save changes or exit
'''

import jsonhelper as jh
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QAction, QListWidget, QMainWindow, QDialog, QDialogButtonBox, QHBoxLayout, QMainWindow, QPushButton, QScrollBar, QVBoxLayout
from qt_material import apply_stylesheet
class Bookmarks(QDialog, QMainWindow):
    def __init__(self, window):
        super(Bookmarks, self).__init__(window)

        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)
        
        # but parent window can reflect changes when applying settings like theme
        self.book = window

        self.setformHBox()
        self.setStyleSheet('''
            QPushButton {
                padding-top: 6px;
                padding-bottom: 6px;
                border-radius: 20%;
                font-family: "FontAwesome";
            }
        ''')

        # buttons Save and Cancel
        self.btnSave = QPushButton(chr(0xf0c7) + '    Save')
        self.btnCancel = QPushButton(chr(0xf057) + '    Cancel')

        btnBox = QDialogButtonBox()
        btnBox.setStyleSheet("* { button-layout: 2; }") # sets default order of buttons
        btnBox.addButton(self.btnSave, QDialogButtonBox.AcceptRole)
        btnBox.addButton(self.btnCancel, QDialogButtonBox.RejectRole)

        # set layout of settings
        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(self.formHBox)
        settingsLayout.addStretch()
        settingsLayout.addWidget(btnBox)
        self.setLayout(settingsLayout)

        quit = QAction('Quit', self)

        self.btnSave.clicked.connect(self.saveChanges)
        self.btnCancel.clicked.connect(self.cancelChanges)
        quit.triggered.connect(self.reject)

    def setformHBox(self):
        # set layout of bookmarks form in horizontal order
        self.formHBox = QHBoxLayout()

        # list box for cities
        self.listBox = QListWidget()
        self.listBox.setVerticalScrollBar(QScrollBar(self))

        # buttons to the right of list widget
        self.upBtn = QPushButton(chr(0xf077))
        self.upBtn.clicked.connect(self.moveUpListItem)

        self.downBtn = QPushButton(chr(0xf078))
        self.downBtn.clicked.connect(self.moveDownListItem)

        self.removeBtn = QPushButton(chr(0xf1f8))
        self.removeBtn.clicked.connect(self.removeListItem)

        # add buttons to a vertical box
        self.btnVBox = QVBoxLayout()
        self.btnVBox.addWidget(self.upBtn)
        self.btnVBox.addWidget(self.downBtn)
        self.btnVBox.addWidget(self.removeBtn)

        # add list box
        self.formHBox.addWidget(self.listBox)
        self.formHBox.addLayout(self.btnVBox)

    def removeListItem(self):
        self.listBox.setFocus()

        # must have more than one item in list in order to remove
        if (self.listBox.count() > 1):
            index = self.listBox.currentRow()
            item = self.listBox.takeItem(index)
            if index != 0:
                self.listBox.setCurrentRow(index-1)
            self.bookmarks_obj.pop(index)

        # after removing items, disable buttons if we're left with one item
        # so user knows he/she cannot interact anymore
        if (self.listBox.count() <= 1):
            self.upBtn.setDisabled(True)
            self.downBtn.setDisabled(True)
            self.removeBtn.setDisabled(True)

    def moveUpListItem(self):
        self.listBox.setFocus()

        index = self.listBox.currentRow()
        if index != 0:
            item = self.listBox.takeItem(index)
            self.listBox.insertItem(index-1, item)
            self.listBox.setCurrentRow(index-1)
            self.objSwap(index-1, index)

    def moveDownListItem(self):
        self.listBox.setFocus()

        index = self.listBox.currentRow()
        if index != self.listBox.count()-1:
            item = self.listBox.takeItem(index)
            self.listBox.insertItem(index+1, item)
            self.listBox.setCurrentRow(index+1)
            self.objSwap(index, index+1)

    def objSwap(self, id_1, id_2):
        # don't worry about reordering indices since we'll do that if user decides to save
        self.bookmarks_obj[id_1], self.bookmarks_obj[id_2] = self.bookmarks_obj[id_2], self.bookmarks_obj[id_1]

    def saveChanges(self):
        # now reorder indices in ascending order
        i = 0
        for obj in self.bookmarks_obj:
            obj['id'] = i
            i += 1

        # now write updated object to bookmarks.json
        self.updateBookmarksJSON(self.bookmarks_obj)

        # reload buttons in the tab
        self.book.side.tabs.reloadButtons()

        # copy updated bookmarks obj to the bookmarks obj in main
        self.book.side.bookmarks_obj = self.bookmarks_obj

        self.close()

    def updateBookmarksJSON(self, obj):
        jh.fwrite('/bookmarks.json', obj)

    def cancelChanges(self):
        # restore original changes
        return super().reject()

    def reject(self) -> None:
        # closing window (clicking 'x') defaults to cancel behavior
        self.cancelChanges()

    def loadBookmarks(self, loaded_bookmarks_obj):
        # clear existing list and add bookmarks to list
        self.listBox.clear()
        for obj in loaded_bookmarks_obj:
            self.listBox.insertItem(obj['id'], obj['location'])

        # give bookmarks.py access to our loaded_bookmarks_obj
        self.bookmarks_obj = loaded_bookmarks_obj

        # enable/disable buttons based on how many items were loaded into the listbox
        if (self.listBox.count() > 1):
            self.upBtn.setDisabled(False)
            self.downBtn.setDisabled(False)
            self.removeBtn.setDisabled(False)
        else:
            self.upBtn.setDisabled(True)
            self.downBtn.setDisabled(True)
            self.removeBtn.setDisabled(True)

        # set focus to listbox, which makes highlighting vibrant rather than faded
        # and also start the selection on first item
        self.listBox.setFocus()
        self.listBox.setCurrentRow(0)