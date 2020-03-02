import sys
import time
import datetime

from pylogix import PLC
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.ticker

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSizePolicy, QInputDialog, QLineEdit, QLabel, QComboBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap

plt.style.use('dark_background')

global ipAddress 
global refreshTime
global simulation
global dataLog
dataLog = [ [],[],[],[],[] ]
simulation = False
ipAddress = "0.0.0.0"
refreshTime = "1"

class Popup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configuration')
        self.setFixedSize(600,400)

        CurrentIPlabel = QLabel("Current PLC IP Address:")
        CurrentIPlabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        self.CurrentIP = QLabel(ipAddress)
        self.CurrentIP.setFont(QtGui.QFont("Arial", 12))

        EnterIPlabel = QLabel("Enter PLC IP Address:")
        EnterIPlabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

        self.IPComboBox = QComboBox()
        IPlist = DiscoverDevicesIP()
        self.IPComboBox.addItems(IPlist)
        self.IPComboBox.setFixedHeight(35)
        self.IPComboBox.setFont(QtGui.QFont("Arial", 10))

        CurrentRefTimeLabel = QLabel("Current refresh time:")
        CurrentRefTimeLabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        self.CurrentRefTime = QLabel(str(refreshTime)+" sec")
        self.CurrentRefTime.setFont(QtGui.QFont("Arial", 12))

        RefreshTimeLabel = QLabel("New refresh time (sec):")
        RefreshTimeLabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

        self.TimeComboBox = QComboBox()
        Items = ["0.5","1","2","5","10","30","60","120","300","600"]
        self.TimeComboBox.addItems(Items)
        self.TimeComboBox.setFixedHeight(35)
        self.TimeComboBox.setFont(QtGui.QFont("Arial", 10))
        self.TimeComboBox.setCurrentIndex(Items.index(refreshTime))

        applyButton = createButton("Apply", "Press to apply changes", 12)
        applyButton.clicked.connect(self.ApplyChanges)

        # Popup layout
        grid = QGridLayout()
        grid.setVerticalSpacing(50)
        grid.setHorizontalSpacing(20)

        grid.addWidget(CurrentIPlabel,0,0)
        grid.addWidget(self.CurrentIP,0,1)
        grid.addWidget(EnterIPlabel,1,0)
        grid.addWidget(self.IPComboBox,1,1)
        grid.addWidget(CurrentRefTimeLabel,2,0)
        grid.addWidget(self.CurrentRefTime,2,1)
        grid.addWidget(RefreshTimeLabel,3,0)
        grid.addWidget(self.TimeComboBox,3,1)
        grid.addWidget(applyButton,4,1)

        self.setGeometry(600,600,400,100)
        self.setLayout(grid)

    def ApplyChanges(self):
        global ipAddress
        global refreshTime

        if self.IPComboBox.currentText() != ipAddress:
            ipAddress = self.IPComboBox.currentText()

        if self.TimeComboBox.currentText() != refreshTime:
            refreshTime = self.TimeComboBox.currentText()

        self.CurrentIP.setText(ipAddress)
        self.CurrentRefTime.setText(str(refreshTime)+" sec")
        

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.displayedPlot = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyLogix Data Acquisition')   
        # Create Buttons
        PauseButton = createIconButton('images/pause-icon.png','Press to pause',35)
        PlayButton = createIconButton('images/play-icon.png','Press to play',35)
        SettingsButton = createIconButton('images/settings-icon.png','Press to go into settings',35)
        BackwardButton = createIconButton('images/backward-icon.png','Press to go backward in time',35)
        ForwardButton = createIconButton('images/forward-icon.png','Press to go forward in time',35)
        NextPlotButton = createButton("Next Plot", "Press to display next plot", 10)

        # What to do if buttons are clicked
        PauseButton.clicked.connect(self._pause_Clicked)
        PlayButton.clicked.connect(self._play_Clicked)
        SettingsButton.clicked.connect(self._buildPopup)
        BackwardButton.clicked.connect(self._backward_Clicked)
        ForwardButton.clicked.connect(self._forward_Clicked)
        NextPlotButton.clicked.connect(self._nextPlot)

        # Layout of GUI
        grid = QGridLayout()
        grid.setVerticalSpacing(5)

        # Button layout
        ButtonLayout = QVBoxLayout()
        button_widget = QWidget()
        button_widget.setLayout(ButtonLayout)
        button_widget.setFixedWidth(100)

        ButtonLayout.addWidget(BackwardButton) 
        ButtonLayout.addWidget(PlayButton)
        ButtonLayout.addWidget(PauseButton)
        ButtonLayout.addWidget(ForwardButton)   
        ButtonLayout.addWidget(SettingsButton)
        ButtonLayout.addWidget(NextPlotButton)  

        # Header layout
        HeaderLogo = QLabel()
        HeaderLogo.setPixmap(QPixmap('images/logo.jpg').scaled(150, 75, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation))

        HeaderTitle = QLabel('Title',self)
        HeaderTitle.setFont(QtGui.QFont("Arial",36))
        
        HeaderLayout = QHBoxLayout()
        HeaderLayout.addWidget(HeaderLogo)
        HeaderLayout.addWidget(HeaderTitle)

        header_widget = QWidget()
        header_widget.setLayout(HeaderLayout)
        header_widget.setFixedHeight(75)

        # Create figure for plotting and layout
        self.fig = Figure(figsize=(5, 3))
        self.dynamic_canvas = FigureCanvas(self.fig)
        GraphLayout = QVBoxLayout()
        GraphLayout.addWidget(self.dynamic_canvas)
        graph_widget = QWidget()
        graph_widget.setLayout(GraphLayout)

        # Add widgets to GUI
        grid.addWidget(header_widget,0,0)
        grid.addWidget(graph_widget,1,0)
        grid.addWidget(button_widget,1,1)
        
        # Set layout to main window
        self.setLayout(grid)

        # Plot
        self.plot_data = []
        self.max_length = 10
        self.time = []
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._timer = self.dynamic_canvas.new_timer(int(float(refreshTime)*1000), [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        if ipAddress == "0.0.0.0":
            return
        self._dynamic_ax.clear()                                                    # clear graph
        now = datetime.datetime.now()
        currentTime = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second) + "." +  str(round(now.microsecond/10000)) # Get actual time
        self.time.append(currentTime)                                               # append actual time
        data, dataName, dataUnit = getLogixData()                                   # Get new data from PLC
        exportData(data, dataName, dataUnit)                                        # Export new data
        
        newdata = data[self.displayedPlot]
        newdataName = dataName[self.displayedPlot]
        self._dynamic_ax.set_title("Graph of " + str(newdataName) + " from " + str(self.time[0]) + " to " + str(self.time[-1]))

        self.plot_data.append(newdata)                      # Add new data to plotted data

        if len(self.plot_data) > self.max_length:           
            self.plot_data.pop(0)
            self.time.pop(0)
        self._dynamic_ax.plot(self.time, self.plot_data)    # Set the data to draw
        self._dynamic_ax.figure.canvas.draw()               # Plot graph

        # Update refresh time
        self._timer.stop()
        self._timer = self.dynamic_canvas.new_timer(int(float(refreshTime)*1000), [(self._update_canvas, (), {})])
        self._timer.start()

    def _nextPlot(self):
        self.displayedPlot = self.displayedPlot + 1
        if self.displayedPlot > 4:
            self.displayedPlot = 0

    def _buildPopup(self):
        self.popup_window = Popup()
        self.popup_window.show()

    def _play_Clicked(self):
        print(_getLogixData(self))

    def _pause_Clicked(self):
        print("pause")

    def _backward_Clicked(self):
        print("Backward")

    def _forward_Clicked(self):
        print("Forward")

def exportData(datalist, dataNamelist, dataUnitlist):
    global dataLog
    for idx, data in enumerate(datalist):
        dataLog[idx].append(data)
    #with open('datalog.csv','a') as fd:
        #fd.write(myCsvRow)

def simulate():
    return random.random()              # Simulate random data

def getPLCtime():
    with PLC() as comm:
        ret = comm.GetPLCTime()         # Get PLC date and time.
    return ret

def DiscoverDevicesIP():
    IPList = []
    with PLC() as comm:
        devices = comm.Discover()       # Discover devices on Ethernet/IP network.
        for device in devices.Value:    
            IPList.append(device.IPAddress)
    return IPList

def getLogixData():
    # gets data from the PLC at the entered ipAdress.
    data_taglist = [ 'LogixData1',  'LogixData2','LogixData3','LogixData4','LogixData5'                   ]
    name_taglist = [ 'LogixDataName1','LogixDataName2','LogixDataName3','LogixDataName4','LogixDataName5' ]
    unit_taglist = [ 'LogixDataUnit1','LogixDataUnit2', 'LogixDataUnit3','LogixDataUnit4','LogixDataUnit5']

    dataName = ["","","","",""]
    dataUnit = ["","","","",""]
    if not simulation:
        with PLC() as comm:
            data = []
            dataName = []
            dataUnit = []
            comm.IPAddress = ipAddress
            ret = comm.Read(data_taglist)
            for response in ret:
                data.append(response.Value)
            ret = comm.Read(name_taglist)
            for response in ret:
                dataName.append(response.Value)
            ret = comm.Read(unit_taglist)
            for response in ret:
                dataUnit.append(response.Value)

    else:
        data0 = simulate()
        data1 = simulate()
        data2 = simulate()
        data3 = simulate()
        data4 = simulate()

        data = [data0, data1, data2, data3, data4]

        dataName[0] = "dataName1"
        dataName[1] = "dataName2"
        dataName[2] = "dataName3"
        dataName[3] = "dataName4"
        dataName[4] = "dataName5"

        dataUnit[0] = "N"
        dataUnit[1] = "N"
        dataUnit[2] = "N"
        dataUnit[3] = "N"
        dataUnit[4] = "N"
    return data, dataName, dataUnit 

def createIconButton(iconStr, toolTipStr, iconSize):
    button = QPushButton("")
    button.setToolTip(toolTipStr)
    button.setIcon(QtGui.QIcon(iconStr))
    button.setIconSize(QtCore.QSize(iconSize,iconSize))
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return button

def createButton(text, toolTipStr, textsize):
    button = QPushButton(text)
    button.setFont(QtGui.QFont("Arial", textsize, QtGui.QFont.Bold))
    button.setToolTip(toolTipStr)
    return button


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    app = MainWindow()
    app.showMaximized()
    qapp.exec_()