import sys
import os
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

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore

# Global variables initialisation

global ipAddress 
global refreshTime
global simulation
global logPeriod
global currentLogFile
global numberOfTrends
global displayedTrend
global dataScaling

dataScaling = "Auto"
displayedTrend = 0
numberOfTrends = 1
currentLogFile = "log.csv"
simulation = False
ipAddress = "0.0.0.0"
refreshTime = "1"
logPeriod = "1 Month"
plt.style.use('dark_background')

class SettingsPopup(QtWidgets.QDialog):
    def __init__(self):
        super(SettingsPopup, self).__init__()
        uic.loadUi(os.path.dirname(os.path.abspath(__file__)) +  "\\SettingsPopup.ui",self)
        self.show()
        self._initUI()

    def _initUI(self):
            # ------ LEFT PANEL: App and export Settings -------
        # Change IP Address Combo Box
        self.IPComboBox = self.findChild(QtWidgets.QComboBox, 'CB_ipAddress')
        IPlist = DiscoverDevicesIP()
        self.IPComboBox.addItems(IPlist)
        if ipAddress in IPlist:
            self.IPComboBox.setCurrentIndex(IPlist.index(ipAddress))

        # Current IP Address Label
        self.labelIP = self.findChild(QtWidgets.QLabel, 'LB_IP')
        self.labelIP.setText(ipAddress)

        # Refresh Time Combo Box
        self.refreshTimeCB = self.findChild(QtWidgets.QComboBox, 'CB_refreshTime')
        Items = ["0.5","1","2","5","10","30","60","120","300","600"]
        self.refreshTimeCB.addItems(Items)
        self.refreshTimeCB.setCurrentIndex(Items.index(refreshTime))

        # Number of trends Combo Box
        self.trendNumberCB = self.findChild(QtWidgets.QComboBox, 'CB_tagNumber')
        Items = [ "1","2","3","4","5","6","7","8","9","10",
                  "11","12","13","14","15","16","17","18","19","20" ]
        self.trendNumberCB.addItems(Items)
        self.trendNumberCB.setCurrentIndex(Items.index(str(numberOfTrends)))

        # Log Time Combo Box
        self.LogComboBox = self.findChild(QtWidgets.QComboBox, 'CB_logPeriod')
        Items = ["1 Day","7 Days","14 Days","1 Month"]
        self.LogComboBox.addItems(Items)
        self.LogComboBox.setCurrentIndex(Items.index(logPeriod))

        # Apply and Cancel Buttons
        applyButton = self.findChild(QtWidgets.QPushButton, 'PB_Apply')
        applyButton.clicked.connect(self._applyChanges)
        cancelButton = self.findChild(QtWidgets.QPushButton, 'PB_Cancel')
        cancelButton.clicked.connect(self.close)

            # ------ RIGHT PANEL: Trend Settings -------
        # Previous and Next Trend Buttons
        nextTrendButton = self.findChild(QtWidgets.QPushButton, "PB_nextTrend")
        nextTrendButton.clicked.connect(self._nextTrendSettings)
        prevTrendButton = self.findChild(QtWidgets.QPushButton, "PB_prevTrend")
        prevTrendButton.clicked.connect(self._prevTrendSettings)

        # Displayed Trend Settings
        displayedTrendSettings = self.findChild(QtWidgets.QLabel, "LB_trendNumber")

        # Data Scaling Radio Buttons:
        dataScalingAuto = self.findChild(QtWidgets.QRadioButton, "RB_Auto")
        dataScalingPreset = self.findChild(QtWidgets.QRadioButton, "RB_Preset")
        if dataScaling == "Auto":
            dataScalingAuto.setChecked(True)
        else:
            dataScalingPreset.setChecked(True)

        # Data Axis Scaling Max input
        self.dataScalingMax = self.findChild(QtWidgets.QLineEdit, "LE_yAxisMax")
        self.dataScalingMax.hide()
        self.LB_dataScalingMax = self.findChild(QtWidgets.QLabel, "LB_yAxisMax")
        self.LB_dataScalingMax.hide()

        # Data Axis Scaling Max input
        self.dataScalingMin = self.findChild(QtWidgets.QLineEdit, "LE_yAxisMin")
        self.dataScalingMin.hide()
        self.LB_dataScalingMin = self.findChild(QtWidgets.QLabel, "LB_yAxisMin")
        self.LB_dataScalingMin.hide()
        

    def _applyChanges(self):
        global ipAddress
        global refreshTime
        global logPeriod
        global numberOfTrends

        if self.IPComboBox.currentText() != ipAddress:
            ipAddress = self.IPComboBox.currentText()
        if self.refreshTimeCB.currentText() != refreshTime:
            refreshTime = self.refreshTimeCB.currentText()
        if self.LogComboBox.currentText() != logPeriod:
            logPeriod = self.LogComboBox.currentText()
        if self.trendNumberCB.currentText() != numberOfTrends:
            numberOfTrends = int(self.trendNumberCB.currentText())

        self.close()

    def _nextTrendSettings(self):
        print("next Trend")
    
    def _prevTrendSettings(self):
        print("prev Trend")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi('MainWindow.ui',self)
        self.initUI()
    
    def initUI(self):
        global ipAddress

        # Find buttons in the UI
        self.PauseButton = self.findChild(QtWidgets.QPushButton, 'PauseButton')
        self.PlayButton = self.findChild(QtWidgets.QPushButton, 'PlayButton')
        self.SettingsButton = self.findChild(QtWidgets.QPushButton, 'SettingsButton')
        self.NextPlotButton = self.findChild(QtWidgets.QPushButton, 'NextButton')
        self.PrevPlotButton = self.findChild(QtWidgets.QPushButton, 'PrevButton')
        self.NavPlotButton = self.findChild(QtWidgets.QPushButton, 'NavButton')

        # What to do if buttons are clicked
        self.PauseButton.clicked.connect(self._pause_Clicked)
        self.PlayButton.clicked.connect(self._play_Clicked)
        self.SettingsButton.clicked.connect(self._buildSettings)
        self.NavPlotButton.clicked.connect(self._buildNavPlot)
        self.PrevPlotButton.clicked.connect(self._prevPlot)
        self.NextPlotButton.clicked.connect(self._nextPlot)

        # Create figure for plotting and layout
        self.fig = Figure(figsize=(5, 3))
        self.dynamic_canvas = FigureCanvas(self.fig)
        self.GraphLayout = self.findChild(QtWidgets.QVBoxLayout, 'GraphLayout')
        self.GraphLayout.addWidget(self.dynamic_canvas)

        # Plot
        self.maxvalue = 1
        self.minvalue = 0
        self.plot_data = []
        self.max_length = 20
        self.time = []
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._timer = self.dynamic_canvas.new_timer(int(float(refreshTime)*1000), [(self._update_canvas, (), {})])
        self._timer.start()
        self.IPlist = DiscoverDevicesIP()
        self.name_list = []
    
    def _update_canvas(self):
        if ipAddress not in self.IPlist:
            return

        self.name_list = getLogixData("LogixName")
        starttime = time.time()
    
        self._dynamic_ax.clear()                                                  # clear graph
        datalist = getLogixData("LogixData")
        exportData(datalist, self.name_list)                                                # Export new data
        data, name, self.time = readData(self.max_length)
        
        self.plot_data = [float(item[displayedTrend]) for item in data] 
        
        if max(self.plot_data) > self.maxvalue:
            self.maxvalue = max(self.plot_data)
        if min(self.plot_data) < self.minvalue:
            self.minvalue = min(self.plot_data)

        rangedifferential = self.maxvalue - self.minvalue
        minrange = self.minvalue - (0.1*rangedifferential)
        maxrange = self.maxvalue + (0.1*rangedifferential)

        dataName = name[displayedTrend]
        
        self._dynamic_ax.tick_params(axis='x', labelrotation = -90)
        self._dynamic_ax.set_ylim(minrange, maxrange)
        self._dynamic_ax.set_title("Graph of " + str(dataName) )#+ " from " + str(self.time[0]) + " to " + str(self.time[-1]))
        self._dynamic_ax.plot(self.time, self.plot_data)    # Set the data to draw
        self._dynamic_ax.figure.canvas.draw()               # Plot graph
        
        endtime = time.time()
        exec_time = endtime-starttime
        print(exec_time)
        timerPreset = (float(refreshTime) - exec_time)
        self._timer.stop()
        self._timer = self.dynamic_canvas.new_timer(timerPreset*1000, [(self._update_canvas, (), {})])
        self._timer.start()

    def _prevPlot(self):
        global displayedTrend

        displayedTrend -= 1
        if displayedTrend < 0:
            displayedTrend = numberOfTrends-1

    def _nextPlot(self):
        global displayedTrend
        displayedTrend += 1
        if displayedTrend > numberOfTrends-1:
            displayedTrend = 0

    def _buildSettings(self):
        self.popup_window = SettingsPopup()

    def _play_Clicked(self):
        print("play")

    def _pause_Clicked(self):
        print("pause")

    def _buildNavPlot(self):
        print("Nav")


def readData(length):
    WorkingDirectory = os.path.dirname(os.path.abspath(__file__))           # Get the current working directory of the executable.
    os.chdir(WorkingDirectory + "/Log")                                     # Navigate to Log directory

    data = []
    inputtime = []

    with open(currentLogFile, "r") as f:                # Open file for reading and read all lines in file
        csvData = f.readlines()
    csvName = csvData[0]                                # Save the first line as the header
    csvData.pop(0)                                      # Remove the first line (header) from the read data
    csvData = csvData[-length:]                         # Keep only last "length" elements of the list (number of lines)
    csvData = [ item.strip() for item in csvData ]      # Remove end of line (\n) characters
    
    lines = [ item.split(";") for item in csvData ]     # Split each lines into sublists
    inputtime = [item[0] for item in lines]             # Get all first elements of each sublists as time values
    
    for line in lines:
        del line[0]                                     # Delete all first elements of each sublists to save only data
    data = lines
    
    csvName = csvName.strip()                           
    name = csvName.split(';')
    name.pop(0)                                         # Remove the first header (time)

    return data, name, inputtime
    

def exportData(data_list, name_list):
    global currentLogFile
    
    currenttime = str(datetime.datetime.now().strftime("%H:%M:%S.%f"))                # Get actual time
    currenttime = currenttime[:-4]

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
        writeCSVheader(name_list, CSVFileName)
        appendCSVrow(currenttime, data_list, CSVFileName)
        
    else:
        appendCSVrow(currenttime, data_list, CSVFileName)

    currentLogFile = CSVFileName
    os.chdir(WorkingDirectory)


def writeCSVheader(NameList, FileName):
    HeaderRow = "Time"

    if not isinstance(NameList, list): 
        NameList = [ NameList ]

    for name in NameList:
        HeaderRow += ";" + name
    HeaderRow = HeaderRow + "\n"

    f = open(FileName, "w+")
    f.write(HeaderRow)

def appendCSVrow(Time, DataList, FileName):
    DataRow = Time 

    if not isinstance(DataList, list): 
        DataList = [ DataList ]

    for Data in DataList:
        DataRow += ";" + str(Data)
    DataRow += "\n"

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

def getLogixData(TagName):
    # gets data from the PLC at the entered ipAdress.
    with PLC() as comm:
        comm.IPAddress = ipAddress      # Search for tags in the PLC at the current IP Address 
        ret = comm.Read(TagName,20)   # Read data tags
        data = ret.Value
    return data


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    app = MainWindow()
    app.showMaximized()
    qapp.exec_()