'''
    confirmationdialog.py
    TMWRK

    Prompts user if they want to open browser to a webpage.
'''

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QLabel, QListWidget, QMainWindow, QDialog, QDialogButtonBox, QHBoxLayout, QMainWindow, QPushButton, QScrollBar, QVBoxLayout

class ConfirmationDialog(QDialog, QMainWindow):
    def __init__(self, window):
        super(ConfirmationDialog, self).__init__(window)

        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)
        
        # but parent window can reflect changes when applying settings like theme
        self.confirm = window

        self.setformVBox()
        self.setStyleSheet('''
            QPushButton {
                padding-top: 6px;
                padding-bottom: 6px;
                border-radius: 20%;
                font-family: "FontAwesome";
            }
        ''')

        # buttons Save and Cancel
        self.btnAccept = QPushButton(chr(0xf0ac) + '    Browse')
        self.btnReject = QPushButton(chr(0xf057) + '    Cancel')

        btnBox = QDialogButtonBox()
        btnBox.setStyleSheet("* { button-layout: 2; }") # sets default order of buttons
        btnBox.addButton(self.btnAccept, QDialogButtonBox.AcceptRole)
        btnBox.addButton(self.btnReject, QDialogButtonBox.RejectRole)

        # set layout of settings
        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(self.formVBox)
        settingsLayout.addStretch()
        settingsLayout.addWidget(btnBox)
        self.setLayout(settingsLayout)

        quit = QAction('Quit', self)

        self.btnAccept.clicked.connect(self.acceptBrowse)
        self.btnReject.clicked.connect(self.rejectBrowse)
        quit.triggered.connect(self.reject)

    def setformVBox(self):
        # set layout of bookmarks form in horizontal order
        self.formVBox = QVBoxLayout()

        # title
        self.lbTitle = QLabel(chr(0xf06a) + '    Opening Web Browser')
        self.lbTitle.setStyleSheet('font-family: "FontAwesome"; font-size: 16pt; font-weight: bold;')

        # information text
        self.lbInfo = QLabel('\nYou are about to open a webpage which may take some time to load!\n\n\nAre you sure you want to browse this webpage?')\

        # add list box
        self.formVBox.addWidget(self.lbTitle)
        self.formVBox.addWidget(self.lbInfo)

    def acceptBrowse(self):
        return QDialog.done(self, 1) # True

    def rejectBrowse(self):
        return QDialog.done(self, 0) # False

    def reject(self) -> None:
        # closing window (clicking 'x') defaults to reject browse behavior
        self.rejectBrowse()