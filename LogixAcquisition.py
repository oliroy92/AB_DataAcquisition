import sys
import os
import re
import time
import datetime

from pylogix import PLC
import random

import pandas
from pandas.io.excel import ExcelWriter
import csv
import glob

import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.ticker

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSizePolicy, QInputDialog, QLineEdit, QLabel, QComboBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap

# Global variables initialisation

global ipAddress 
global refreshTime
global simulation
global logPeriod
global currentLogFile

currentLogFile = "log.csv"
simulation = False
ipAddress = "0.0.0.0"
refreshTime = "1"
logPeriod = "1 Month"
plt.style.use('dark_background')

class Popup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configuration')
        self.setFixedSize(800,400)

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

        # Data refresh time
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

        # Apply changes button
        applyButton = createButton("Apply", "Press to apply changes", 12)
        applyButton.clicked.connect(self.ApplyChanges)

        # New log period setting
        NewLogTimeLabel = QLabel("Period to create new log file:")
        NewLogTimeLabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

        self.LogComboBox = QComboBox()
        Items = ["1 Day","7 Days","14 Days","1 Month"]
        self.LogComboBox.addItems(Items)
        self.LogComboBox.setFixedHeight(35)
        self.LogComboBox.setFont(QtGui.QFont("Arial", 10))
        self.LogComboBox.setCurrentIndex(Items.index(logPeriod))


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
        grid.addWidget(NewLogTimeLabel, 0,2)
        grid.addWidget(self.LogComboBox, 0,3)

        self.setGeometry(600,600,400,100)
        self.setLayout(grid)

    def ApplyChanges(self):
        global ipAddress
        global refreshTime
        global logPeriod

        if self.IPComboBox.currentText() != ipAddress:
            ipAddress = self.IPComboBox.currentText()

        if self.TimeComboBox.currentText() != refreshTime:
            refreshTime = self.TimeComboBox.currentText()

        self.CurrentIP.setText(ipAddress)
        self.CurrentRefTime.setText(str(refreshTime)+" sec")

        if self.LogComboBox.currentText() != logPeriod:
            logPeriod = self.LogComboBox.currentText()

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
        self.maxvalue = 1
        self.minvalue = 0
        self.plot_data = []
        self.max_length = 10
        self.time = []
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._timer = self.dynamic_canvas.new_timer(int(float(refreshTime)*1000), [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        IPlist = DiscoverDevicesIP()
        if ipAddress not in IPlist:
            return
    
        self._dynamic_ax.clear()                                                  # clear graph

        exportData()                                                             # Export new data
        data, name, self.time = readData(self.max_length)
        
        self.plot_data = [float(item[self.displayedPlot]) for item in data] 
        
        if max(self.plot_data) > self.maxvalue:
            self.maxvalue = max(self.plot_data)
        if min(self.plot_data) < self.minvalue:
            self.minvalue = min(self.plot_data)

        rangedifferential = self.maxvalue - self.minvalue
        minrange = self.minvalue - (0.1*rangedifferential)
        maxrange = self.maxvalue + (0.1*rangedifferential)

        dataName = name[self.displayedPlot]
        
        self._dynamic_ax.set_ylim(minrange, maxrange)
        self._dynamic_ax.set_title("Graph of " + str(dataName) )#+ " from " + str(self.time[0]) + " to " + str(self.time[-1]))
        self._dynamic_ax.plot(self.time, self.plot_data)    # Set the data to draw
        self._dynamic_ax.figure.canvas.draw()               # Plot graph
        
        #plt.ylim(self.minvalue, self.maxvalue)
        #_updateRefreshTime(self)


    def _updateRefreshTime(self):
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

def readData(length):
    WorkingDirectory = os.path.dirname(os.path.abspath(__file__))           # Get the current working directory of the executable.
    os.chdir(WorkingDirectory + "/Log")                                     # Navigate to Log directory

    data = []
    time = []

    with open(currentLogFile, "r") as f:                # Open file for reading
        csvData = f.readlines()
    csvName = csvData[0]                                # Save the first line as the header
    csvData.pop(0)                                      # Remove the first line (header)
    csvData = csvData[-length:]                         # Keep only last "length" elements of the list (number of lines)
    csvData = [ item.strip() for item in csvData ]      # Remove end of line (\n) characters
    
    lines = [ item.split(";") for item in csvData ]    
    time = [item[0] for item in lines]                  # Get all first elements of each sublists as time values
    
    for line in lines:
        del line[0]                                     # Delete all first elements of each sublists to save only data
    data = lines
    
    csvName = csvName.strip()                           
    name = csvName.split(';')
    name.pop(0)                                         # Remove the first header (time)
    return data, name, time
    

def exportData():
    global currentLogFile
    
    datalist, dataNamelist = getLogixData()
    time = str(datetime.datetime.now().strftime("%H:%M:%S"))                # Get actual time

    WorkingDirectory = os.path.dirname(os.path.abspath(__file__))           # Get the current working directory of the executable.
    os.chdir(WorkingDirectory)
    CurrentDirectoryList = os.listdir()

    if "Log" not in CurrentDirectoryList:
        os.mkdir(WorkingDirectory + "/Log")
    os.chdir(WorkingDirectory + "/Log")

    csvFilesList = glob.glob("*.csv")
    csvFilesList.sort()

    filetime = datetime.datetime.now().strftime("%Y-%m-%d")
    CSVFileName = filetime + "_DataLog.csv"

    if CSVFileName not in csvFilesList:
        writeCSVheader(dataNamelist, CSVFileName)
        appendCSVrow(time, datalist, CSVFileName)
        
    else:
        appendCSVrow(time, datalist, CSVFileName)

    currentLogFile = CSVFileName
    os.chdir(WorkingDirectory)


def writeCSVheader(NameList, FileName):
    HeaderRow = "Time"
    for name in NameList:
        HeaderRow = HeaderRow + ";" + name
    HeaderRow = HeaderRow + "\n"

    f = open(FileName, "w+")
    f.write(HeaderRow)

def appendCSVrow(Time, DataList, FileName):
    DataRow = Time 
    for Data in DataList:
        DataRow = DataRow + ";" + str(Data)
    DataRow = DataRow + "\n"
    
    with open(FileName, "a") as f:
        f.write(DataRow)


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

def getCurrentTime():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    millisec = now.microsecond/1000
    return year, month, day, hour, minute, second, millisec

def getLogixData():
    # gets data from the PLC at the entered ipAdress.
    data_taglist = [ 'LogixData1',  'LogixData2','LogixData3','LogixData4','LogixData5'                   ]
    name_taglist = [ 'LogixDataName1','LogixDataName2','LogixDataName3','LogixDataName4','LogixDataName5' ]

    data = []
    dataName = []

    if simulation:
        dataName = ["","","","",""]
        while True:
            data.append(simulate())
            if len(data) == 5:
                break
    
    else:
        with PLC() as comm:
            comm.IPAddress = ipAddress      # Search for tags in the PLC at the current IP Address 
            ret = comm.Read(data_taglist)   # Read data tags
            print(ret)
            for response in ret:
                data.append(response.Value) 
            ret = comm.Read(name_taglist)   # Read name tags
            for response in ret:
                dataName.append(response.Value)

    return data, dataName
   

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