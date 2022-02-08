'''
    settings.py
    TMWRK

    Settings contains:
        extended options to change default settings which are saved to settings.json
        options include:
            - changing theme (again)
            - changing theme accent
            - changing preferred measure (Fahrenheit / Celsius)
            - changing preferred time (standard time / military time)
            - any other miscellaneous options that the user wants

    References:
        https://www.delftstack.com/tutorial/pyqt5/pyqt5-radiobutton/
'''

import jsonhelper as jh
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QAction, QMainWindow, QButtonGroup, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QMainWindow, QPushButton, QRadioButton, QVBoxLayout, QSlider
from qt_material import apply_stylesheet

class Settings(QDialog, QMainWindow):
    def __init__(self, window):
        super(Settings, self).__init__(window)
        
        # don't allow user to interact with parent window
        self.setWindowModality(Qt.ApplicationModal)
        
        # but parent window can reflect changes when applying settings like theme
        self.settings = window

        # load current JSON data (in case need to revert changes)
        self.obj = jh.fread('/settings.json')

        # temporary variables (when user clicks SAVE, write to json file with values stored in tmp)
        # note: value of these tmp variables is set by state of widget
        self.tmpAcnt = str(self.obj['theme-accent'])
        self.tmpTheme = str(self.obj['theme'])
        self.tmpTime = str(self.obj['time'])
        self.tmpTemper = str(self.obj['temp-unit'])
        self.tmpSidebar = str(self.obj['sidebar'])
        
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
        self.btnSave = QPushButton(chr(0xf0c7) + '    Save')
        self.btnCancel = QPushButton(chr(0xf057) + '    Cancel')

        btnBox = QDialogButtonBox()
        btnBox.setStyleSheet("* { button-layout: 2; }") # sets default order of buttons
        btnBox.addButton(self.btnSave, QDialogButtonBox.AcceptRole)
        btnBox.addButton(self.btnCancel, QDialogButtonBox.RejectRole)

        # set layout of settings
        settingsLayout = QVBoxLayout()
        settingsLayout.addLayout(self.formVBox)
        settingsLayout.addStretch()
        settingsLayout.addWidget(btnBox)
        self.setLayout(settingsLayout)

        quit = QAction('Quit', self)

        self.btnSave.clicked.connect(self.saveChanges)
        self.btnCancel.clicked.connect(self.cancelChanges)
        quit.triggered.connect(self.reject)

    def setformVBox(self):
        # set layout of settings form and create vbox to hold settings in vertical order
        self.formVBox = QVBoxLayout()

        # hacky alignment adjustment since auto option was recently added by Mahim + it's the last day of iteration 4
        # and I don't really feel like messing around with QGridLayout to properly align fields
        self.emptyLabel = QLabel('')

        # widgets for accent options
        self.acntLabel = QLabel('Theme Accent:')
        self.acntSlider = QSlider(Qt.Horizontal)
        self.acntSlider.setMaximum(7)
        self.acntSlider.valueChanged.connect(self.onSlideAcnt)

        # widgets for theme options
        self.themeLabel = QLabel('Theme:')
        self.themeRadBtn1 = QRadioButton('Dark')
        self.themeRadBtn2 = QRadioButton('Light')
        self.themeRadBtn3 = QRadioButton('Auto')
        
        # widgets for time options
        self.timeLabel = QLabel('Time:')
        self.timeRadBtn1 = QRadioButton('Standard')
        self.timeRadBtn2 = QRadioButton('Military')
        
        # widgets for temperature options
        self.temperLabel = QLabel('Temperature Unit:')
        self.temperRadBtn1 = QRadioButton('Fahrenheit')
        self.temperRadBtn2 = QRadioButton('Celsius')

        # widgets for sidebar state options
        self.sideLabel = QLabel('Sidebar:')
        self.sideRadBtn1 = QRadioButton('Expanded')
        self.sideRadBtn2 = QRadioButton('Collapsed')

        # button groups for each option that uses radiobutton
        self.themeBtnGroup = QButtonGroup()
        self.timeBtnGroup = QButtonGroup()
        self.temperBtnGroup = QButtonGroup()
        self.sideBtnGroup = QButtonGroup()

        # add buttons for each button group
        self.themeBtnGroup.addButton(self.themeRadBtn1)
        self.themeBtnGroup.addButton(self.themeRadBtn2)
        self.themeBtnGroup.addButton(self.themeRadBtn3)
        self.timeBtnGroup.addButton(self.timeRadBtn1)
        self.timeBtnGroup.addButton(self.timeRadBtn2)
        self.temperBtnGroup.addButton(self.temperRadBtn1)
        self.temperBtnGroup.addButton(self.temperRadBtn2)
        self.sideBtnGroup.addButton(self.sideRadBtn1)
        self.sideBtnGroup.addButton(self.sideRadBtn2)

        # set values to widgets according to json data
        self.setWidgetValues(self.obj['theme-accent'])

        # connect theme radio input to function
        self.themeRadBtn1.toggled.connect(self.onClickedTheme)
        self.themeRadBtn2.toggled.connect(self.onClickedTheme)
        self.themeRadBtn3.toggled.connect(self.onClickedTheme)

        # connect time radio input to function
        self.timeRadBtn1.toggled.connect(self.onClickedTime)
        self.timeRadBtn2.toggled.connect(self.onClickedTime)        
        
        # connect temperature radio input to function
        self.temperRadBtn1.toggled.connect(self.onClickedTemper)
        self.temperRadBtn2.toggled.connect(self.onClickedTemper)

        # connect sidebar expand/collapse to function
        self.sideRadBtn1.toggled.connect(self.onClickedSide)
        self.sideRadBtn2.toggled.connect(self.onClickedSide)

        # accent layout with accent widgets
        acntLayout = QHBoxLayout()
        acntLayout.addWidget(self.acntLabel)
        acntLayout.addWidget(self.acntSlider)

        # theme layout with theme widgets
        themeLayout = QHBoxLayout()
        themeLayout.addWidget(self.themeLabel)
        themeLayout.addWidget(self.themeRadBtn1)
        themeLayout.addWidget(self.themeRadBtn2)
        themeLayout.addWidget(self.themeRadBtn3)

        # time layout with time widgets
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.timeLabel)
        timeLayout.addWidget(self.timeRadBtn1)
        timeLayout.addWidget(self.timeRadBtn2)
        timeLayout.addWidget(self.emptyLabel)

        # temperature layout with temperature widgets
        temperLayout = QHBoxLayout()
        temperLayout.addWidget(self.temperLabel)
        temperLayout.addWidget(self.temperRadBtn1)
        temperLayout.addWidget(self.temperRadBtn2)
        temperLayout.addWidget(self.emptyLabel)

        # sidebar layout with sidebar widgets
        sidebarLayout = QHBoxLayout()
        sidebarLayout.addWidget(self.sideLabel)
        sidebarLayout.addWidget(self.sideRadBtn1)
        sidebarLayout.addWidget(self.sideRadBtn2)
        sidebarLayout.addWidget(self.emptyLabel)

        # set each layout to group box
        self.formVBox.addLayout(acntLayout)
        self.formVBox.addLayout(themeLayout)
        self.formVBox.addLayout(timeLayout)
        self.formVBox.addLayout(temperLayout)
        self.formVBox.addLayout(sidebarLayout)

    # since some values can be changed OUTSIDE of the settings window,
    # like theme and sidebar state, we need to reload those SPECIFIC rad buttons
    def reloadRadButtons(self, theme_toggled):
        obj = jh.fread('/settings.json')

        # theme
        if theme_toggled == True:
            if obj['theme'] == 'dark':
                self.themeRadBtn1.setChecked(True)
        #     # else:
            elif obj['theme'] == 'light':
                self.themeRadBtn2.setChecked(True)
            else:
                self.themeRadBtn3.setChecked(True) #auto dark mode
                
            self.tmpTheme = obj['theme']
        else:
            if self.tmpTheme == 'dark':
                self.themeRadBtn1.setChecked(True)
            # else:
            elif self.tmpTheme == 'light':
                self.themeRadBtn2.setChecked(True)
            else:
                self.themeRadBtn3.setChecked(True) #auto dark mode
            obj['theme'] = self.tmpTheme
            jh.fwrite('/settings.json', self.obj)

        
        # sidebar state
        if obj['sidebar'] == 'expanded':
            self.sideRadBtn1.setChecked(True)
        else:
            self.sideRadBtn2.setChecked(True)


    def onSlideAcnt(self, value):
        self.tmpAcnt = self.lookupAcnt(value)

        set_auto = False
        # only 'dark' and 'light' themes work,
        # so need to take auto out of theme name, apply stylesheet, 
        # then set theme back to auto
        obj = jh.fread('/settings.json')
        if ('auto' in str(obj['theme'])):
            set_auto = True
            if (str(obj['theme']) == 'auto-dark'):
                self.tmpTheme = 'dark'
            elif (str(obj['theme']) == 'auto-light'):
                self.tmpTheme = 'light'

        apply_stylesheet(self.settings, theme=(self.tmpTheme + '_' + self.tmpAcnt + '.xml'))
        if (set_auto == True):
            self.tmpTheme = 'auto-' + obj['theme']

    def lookupAcnt(self, value):
        return {
            0: 'red', 1: 'amber', 2: 'lightgreen', 3: 'teal',
            4: 'cyan', 5: 'blue', 6: 'purple', 7: 'pink'
        }[value]

    def onClickedTheme(self):
        radBtn = self.sender()
        if radBtn.isChecked():
            obj = jh.fread('/settings.json')

            set_auto = False

            # if user clicked on auto mode, set theme based on time
            if (radBtn.text().lower() == 'auto'):
                user_clicked_auto = True
                self.autoDark_toggle(user_clicked_auto)
                return

            #if user didn't click auto, they want dark or light mode    
            elif (radBtn.text().lower() != 'auto'):
                self.tmpTheme = radBtn.text().lower()

            apply_stylesheet(self.settings, theme=(self.tmpTheme + '_' + self.tmpAcnt + '.xml'))
            

    def onClickedTime(self):
        radBtn = self.sender()
        if radBtn.isChecked():
            self.tmpTime = radBtn.text().lower()

    def onClickedTemper(self):
        radBtn = self.sender()
        if radBtn.isChecked():
            self.tmpTemper = radBtn.text().lower()

    def onClickedSide(self):
        sideBtn = self.sender()
        if sideBtn.isChecked():
            self.tmpSidebar = sideBtn.text().lower()
            self.settings.sideBar.toggleResizeOnState(self.tmpSidebar)

    def setWidgetValues(self, value):
        # set accent values in widgets based on json data
        colors = ['red', 'amber', 'lightgreen', 'teal', 'cyan', 'blue', 'purple', 'pink']
        for c in colors:
            if str(value) == c:
                self.acntSlider.setValue(colors.index(c))
                break

        # set theme values in widgets based on json data
        if str(self.obj['theme']) == 'dark':
            self.themeRadBtn1.setChecked(True) # dark
        # else:
        elif str(self.obj['theme']) == 'light':
            self.themeRadBtn2.setChecked(True) # light
        else: 
            self.themeRadBtn3.setChecked(True) # auto

        # set time values in widgets based on json data
        if str(self.obj['time']) == 'standard':
            self.timeRadBtn1.setChecked(True) # standard
        else:
            self.timeRadBtn2.setChecked(True) # military

        # set temperature values in widgets based on json data
        if str(self.obj['temp-unit']) == 'fahrenheit':
            self.temperRadBtn1.setChecked(True) # fahrenheit
        else:
            self.temperRadBtn2.setChecked(True) # celsius

        # set sidebar state values in widgets based on json data
        if str(self.obj['sidebar']) == 'expanded':
            self.sideRadBtn1.setChecked(True) # expanded
            self.settings.sideBar.toggleResizeOnState(self.tmpSidebar)
        else:
            self.sideRadBtn2.setChecked(True) # collapsed
            self.settings.sideBar.toggleResizeOnState(self.tmpSidebar)
    
    def autoDark_toggle(self, user_clicked_auto):
        obj = jh.fread('/settings.json')

        time = QTime.currentTime()
        hour = time.hour()
        
        set_auto = False
        # only 'dark' and 'light' themes work,
        # so need to take auto out of theme name, apply stylesheet, 
        # then set theme back to auto
        
        if (user_clicked_auto == True):
            set_auto = True

        #10 pm = 22   #if time is >= 10 pm and <7 am:   
        if ( (hour >= 22) or (hour < 7) ):  
            #dark mode
            obj['theme'] = 'dark'
            apply_stylesheet(self.settings, theme=('dark_' + str(obj['theme-accent']) + '.xml'))

        #if time is >= 7 am <10 pm: 
        elif ( (hour >= 7) or (hour < 22) ): 
            #light mode
            obj['theme'] = 'light'
            apply_stylesheet(self.settings, theme=('light_' + str(obj['theme-accent']) + '.xml'))
            
        if (set_auto == True):
            obj['theme'] = 'auto-' + obj['theme']   
        
        self.tmpTheme = obj['theme']

    def saveChanges(self):
        # write changes to obj
        self.obj['theme-accent'] = self.tmpAcnt
        self.obj['theme'] = self.tmpTheme
        self.obj['time'] = self.tmpTime
        self.obj['temp-unit'] = self.tmpTemper
        self.obj['sidebar'] = self.tmpSidebar
        
        # write obj to settings.json
        jh.fwrite('/settings.json', self.obj)

        self.close()

    def cancelChanges(self):
        # restore original changes
        self.setWidgetValues(str(self.obj['theme-accent']))
        return super().reject()

    def reject(self) -> None:
        # closing window (clicking 'x') defaults to cancel behavior
        self.cancelChanges()
