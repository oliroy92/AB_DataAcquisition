import sys, os
import re
import time, datetime

from pylogix import PLC

import csv
import glob

import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.ticker

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *

from NumericKB import Input as KB

plt.style.use('dark_background')

class trendSettings:
    dataScaling = "Auto"
    dataScalingMax = 10
    dataScalingMin = 0
    dataToDisplay = ""
    minmaxMode = "Disabled"
    minValue = 0
    maxValue = 0

class appSettings:
    displayedTrend = 0
    numberOfTrends = 1
    currentLogFile = "log.csv"
    ipAddress = "0.0.0.0"
    refreshTime = "1"
    logPeriod = "1 Month"    

class SettingsPopup(QtWidgets.QDialog):
    def __init__(self, trendSet, appSet):
        super(SettingsPopup, self).__init__()
        uic.loadUi(os.path.dirname(os.path.abspath(__file__)) +  "\\SettingsPopup.ui",self)
        self.trendSet = trendSet
        self.appSet = appSet
        self.show()
        self._initUI()

    def _initUI(self):
            # ------ LEFT PANEL: App and export Settings -------
        # Change IP Address Push Button
        self.PB_ip = self.findChild(QtWidgets.QPushButton, 'PB_ipAddress')
        self.PB_ip.clicked.connect(self._changeIP)
        self.PB_ip.setText(self.appSet.ipAddress)

        # Refresh Time Combo Box
        self.refreshTimeCB = self.findChild(QtWidgets.QComboBox, 'CB_refreshTime')
        Items = ["0.5","1","2","5","10","30","60","120","300","600"]
        self.refreshTimeCB.addItems(Items)
        self.refreshTimeCB.setCurrentIndex(Items.index(self.appSet.refreshTime))

        # Number of trends Combo Box
        self.trendNumberCB = self.findChild(QtWidgets.QComboBox, 'CB_tagNumber')
        Items = [ "1","2","3","4","5","6","7","8","9","10",
                  "11","12","13","14","15","16","17","18","19","20" ]
        self.trendNumberCB.addItems(Items)
        self.trendNumberCB.setCurrentIndex(Items.index(str(self.appSet.numberOfTrends)))
        self.trendNumberCB.currentIndexChanged.connect(self._updateTrends)

        # Log Time Combo Box
        self.LogComboBox = self.findChild(QtWidgets.QComboBox, 'CB_logPeriod')
        Items = ["1 Day","7 Days","14 Days","1 Month"]
        self.LogComboBox.addItems(Items)
        self.LogComboBox.setCurrentIndex(Items.index(self.appSet.logPeriod))

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
        self.displayedTrendSettings = self.findChild(QtWidgets.QLabel, "LB_trendNumber")
        
        # Data Scaling Radio Buttons:
        self.dataScalingAuto = self.findChild(QtWidgets.QRadioButton, "RB_Auto")
        self.dataScalingPreset = self.findChild(QtWidgets.QRadioButton, "RB_Preset")
        self.dataScalingAuto.toggled.connect(self._toggleScalingMode)

        # Data Axis Scaling Max input
        self.PB_dataScalingMax = self.findChild(QtWidgets.QPushButton, "PB_yAxisMax")
        self.PB_dataScalingMax.clicked.connect(self._changeScalingMax)
        self.LB_dataScalingMax = self.findChild(QtWidgets.QLabel, "LB_yAxisMax")

        # Data Axis Scaling Min input
        self.PB_dataScalingMin = self.findChild(QtWidgets.QPushButton, "PB_yAxisMin")
        self.PB_dataScalingMin.clicked.connect(self._changeScalingMin)
        self.LB_dataScalingMin = self.findChild(QtWidgets.QLabel, "LB_yAxisMin")

        # Minimum & Maximum Mode
        self.CB_minmaxLimit = self.findChild(QtWidgets.QComboBox, "CB_minMax")
        self.minmaxItems = ["Maximum", "Minimum", "Maximum & Minimum", "Disabled"]
        self.CB_minmaxLimit.addItems(self.minmaxItems)
        self.CB_minmaxLimit.currentTextChanged.connect(self._togglehide)

        # Maximum value
        self.PB_maxValue = self.findChild(QtWidgets.QPushButton, "PB_dataMax")
        self.PB_maxValue.clicked.connect(self._changeMaxValue)
        self.LB_maxValue = self.findChild(QtWidgets.QLabel, "LB_dataMax")

        # Minimum value
        self.PB_minValue = self.findChild(QtWidgets.QPushButton, "PB_dataMin")
        self.PB_minValue.clicked.connect(self._changeMinValue)
        self.LB_minValue = self.findChild(QtWidgets.QLabel, "LB_dataMin") 

        # Selected data
        self.data_PB = []
        dataList = []
        if self.trendSet[self.appSet.displayedTrend].dataToDisplay:
            dataList = self.trendSet[self.appSet.displayedTrend].dataToDisplay.split(",")
        for x in range(1,20):
            self.data_PB.append(self.findChild(QtWidgets.QPushButton, "PB_d"+ str(x)))
        for i,PB in enumerate(self.data_PB):
            if dataList:
                if str(i) in dataList:
                    PB.setChecked(True)
            PB.clicked.connect(self._pressedDataPB(i))

        # Initializing:
        if self.trendSet[self.appSet.displayedTrend].dataScaling == "Auto":
            self.dataScalingAuto.setChecked(True)
        else:
            self.dataScalingPreset.setChecked(True)
        
        self.CB_minmaxLimit.setCurrentIndex(self.minmaxItems.index(self.trendSet[self.appSet.displayedTrend].minmaxMode))
        self._updateTrendSettings()

    def _pressedDataPB(self,i):
        def togglePB():
            print(self.data_PB[i].isChecked())
            if not self.data_PB[i].isChecked():
                self.data_PB[i].setChecked(False)
            elif self.data_PB[i].isChecked():
                self.data_PB[i].setChecked(True)
        return togglePB

    def _nextTrendSettings(self):
        self.appSet.displayedTrend += 1
        if self.appSet.displayedTrend > self.appSet.numberOfTrends-1:
            self.appSet.displayedTrend = 0
        self._updateTrendSettings()
    
    def _prevTrendSettings(self):
        self.appSet.displayedTrend -= 1
        if self.appSet.displayedTrend < 0:
            self.appSet.displayedTrend = self.appSet.numberOfTrends-1
        self._updateTrendSettings()

    def _toggleScalingMode(self):
        self._updateTrendSettings()

    def _changeIP(self):
        numeric_keyboard = KB()
        if numeric_keyboard.exec_():
            ipInput = numeric_keyboard.InputText
            splitIP = ipInput.split(".")
            if len(splitIP) == 4:
                self.PB_ip.setText(ipInput)
            
    def _changeScalingMax(self):
        self.PB_dataScalingMax.setText(self._getNumericValue())

    def _changeScalingMin(self):
        self.PB_dataScalingMin.setText(self._getNumericValue())

    def _changeMaxValue(self):
        self.PB_maxValue.setText(self._getNumericValue())

    def _changeMinValue(self):
        self.PB_minValue.setText(self._getNumericValue())

    def _getNumericValue(self):
        numeric_keyboard = KB()
        if numeric_keyboard.exec_():
            numericInput = numeric_keyboard.InputText
            return numericInput

    def _updateTrendSettings(self):
        self.displayedTrendSettings.setText("Trend #" + str(self.appSet.displayedTrend + 1) )
        
        self.PB_dataScalingMax.setText(str(self.trendSet[self.appSet.displayedTrend].dataScalingMax))
        self.PB_dataScalingMin.setText(str(self.trendSet[self.appSet.displayedTrend].dataScalingMin))

        self.PB_maxValue.setText(str(self.trendSet[self.appSet.displayedTrend].maxValue))
        self.PB_minValue.setText(str(self.trendSet[self.appSet.displayedTrend].minValue))

        self._togglehide()

        
    def _updateTrends(self):
        # Updates the number of trends settings to adjust for the selected number of trends
        if int(self.trendNumberCB.currentText()) > self.appSet.numberOfTrends:
            while len(self.trendSet) != int(self.trendNumberCB.currentText()):
                self.trendSet.append(trendSettings())
        elif int(self.trendNumberCB.currentText()) < self.appSet.numberOfTrends:
            while len(self.trendSet) != int(self.trendNumberCB.currentText()):
                self.trendSet.pop()

    def _togglehide(self):
        if self.dataScalingAuto.isChecked():
            self.LB_dataScalingMax.hide()
            self.PB_dataScalingMax.hide()
            self.LB_dataScalingMin.hide()
            self.PB_dataScalingMin.hide()
        else:
            self.LB_dataScalingMax.show()
            self.PB_dataScalingMax.show()
            self.LB_dataScalingMin.show()
            self.PB_dataScalingMin.show()       
        
        if self.CB_minmaxLimit.currentText() == "Disabled":
            self.LB_minValue.hide()
            self.PB_minValue.hide()
            self.LB_maxValue.hide()
            self.PB_maxValue.hide()
        elif self.CB_minmaxLimit.currentText() == "Minimum":
            self.LB_minValue.show()
            self.PB_minValue.show()
            self.LB_maxValue.hide()
            self.PB_maxValue.hide()
        elif self.CB_minmaxLimit.currentText() == "Maximum":
            self.LB_maxValue.show()
            self.PB_maxValue.show()
            self.LB_minValue.hide()
            self.PB_minValue.hide()
        else:
            self.LB_minValue.show()
            self.PB_minValue.show()
            self.LB_maxValue.show()
            self.PB_maxValue.show()

    def _applyChanges(self):
        # Apply application settings
        if self.PB_ip.text() != self.appSet.ipAddress:
            self.appSet.ipAddress = self.PB_ip.text()
        if self.refreshTimeCB.currentText() != self.appSet.refreshTime:
            self.appSet.refreshTime = self.refreshTimeCB.currentText()
        if self.LogComboBox.currentText() != self.appSet.logPeriod:
            self.appSet.logPeriod = self.LogComboBox.currentText()
        if self.trendNumberCB.currentText() != self.appSet.numberOfTrends:
            self.appSet.numberOfTrends = int(self.trendNumberCB.currentText())

        # Apply displayed trend settings
        self.trendSet[self.appSet.displayedTrend].dataScalingMax = float(self.PB_dataScalingMax.text())
        self.trendSet[self.appSet.displayedTrend].dataScalingMin = float(self.PB_dataScalingMin.text())
        self.trendSet[self.appSet.displayedTrend].maxValue = float(self.PB_maxValue.text())
        self.trendSet[self.appSet.displayedTrend].minValue = float(self.PB_minValue.text())

        self.trendSet[self.appSet.displayedTrend].minmaxMode  = self.CB_minmaxLimit.currentText()
        if self.dataScalingAuto.isChecked():
            self.trendSet[self.appSet.displayedTrend].dataScaling = "Auto"
        else:
            self.trendSet[self.appSet.displayedTrend].dataScaling = "Preset"

        data = ""
        for i,PB in enumerate(self.data_PB):
            if PB.isChecked():
                data += str(i) + ","
        self.trendSet[self.appSet.displayedTrend].dataToDisplay = data[:-1]

        self.close()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        uic.loadUi('MainWindow.ui',self)
        self.appSet = appSettings()
        self.initUI()
    
    def initUI(self):
        self.trendSet = [ trendSettings() ]

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
        self._timer = self.dynamic_canvas.new_timer(int(float(self.appSet.refreshTime)*1000), [(self._update_canvas, (), {})])
        self._timer.start()

        self.commError = False

    def _update_canvas(self):
        if self.appSet.ipAddress == "0.0.0.0":
            return
        
        name_list = getLogixData("LogixName", self.appSet.ipAddress)
        if name_list == -1:
            self.appSet.ipAddress = "0.0.0.0"
            return

        starttime = time.time()
    
        datalist = getLogixData("LogixData", self.appSet.ipAddress)
        exportData(datalist, name_list)                                                # Export new data

        data, name, self.time = readData(self.max_length)
        self._dynamic_ax.clear()                                                  # clear graph
        self.plot_data = [float(item[self.appSet.displayedTrend]) for item in data] 
        
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
        self._dynamic_ax.set_title("Graph of " + str(dataName) ) 
        self._dynamic_ax.plot(self.time, self.plot_data)            # Set the data to draw
        self._dynamic_ax.figure.canvas.draw()                       # Plot graph
        
        endtime = time.time()
        exec_time = endtime-starttime
        timerPreset = (float(self.appSet.refreshTime) - exec_time)
        self._timer.stop()
        self._timer = self.dynamic_canvas.new_timer(timerPreset*1000, [(self._update_canvas, (), {})])
        self._timer.start()

    def _prevPlot(self):
        self.appSet.displayedTrend -= 1
        if self.appSet.displayedTrend < 0:
            self.appSet.displayedTrend = self.appSet.numberOfTrends-1

    def _nextPlot(self):
        self.appSet.displayedTrend += 1
        if self.appSet.displayedTrend > self.appSet.numberOfTrends-1:
            self.appSet.displayedTrend = 0

    def _buildSettings(self):
        self.popup_window = SettingsPopup(self.trendSet, self.appSet)

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

def getLogixData(TagName, ipAddress):
    # gets data from the PLC at the entered ipAdress.
    with PLC() as comm:
        comm.IPAddress = ipAddress      # Search for tags in the PLC at the current IP Address 
        try:
            ret = comm.Read(TagName,20)   # Read data tags
        except:
            data = -1
            return data
        data = ret.Value
    return data


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    app = MainWindow()
    app.showMaximized()
    qapp.exec_()