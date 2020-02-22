import sys
import time

from pylogix import PLC

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSizePolicy, QInputDialog, QLineEdit, QLabel, QComboBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap

global ipAddress 
global refreshTime
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

        self.IPtextbox = QLineEdit()
        self.IPtextbox.setGeometry(10,35,150,20)
        self.IPtextbox.setFont(QtGui.QFont("Arial",12))

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

        applyButton = createButton("Apply", "Press to apply changes", 12)
        applyButton.clicked.connect(self.ApplyChanges)

        # Popup layout
        grid = QGridLayout()
        grid.setVerticalSpacing(50)
        grid.setHorizontalSpacing(20)

        grid.addWidget(CurrentIPlabel,0,0)
        grid.addWidget(self.CurrentIP,0,1)
        grid.addWidget(EnterIPlabel,1,0)
        grid.addWidget(self.IPtextbox,1,1)
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

        if self.IPtextbox.text() != ipAddress:
            splitIP = self.IPtextbox.text().split(".")
            splitIP = [i for i in splitIP if i]
            if len(splitIP) == 4:
                ipAddress = self.IPtextbox.text()

        if self.TimeComboBox.currentText() != refreshTime:
            refreshTime = self.TimeComboBox.currentText()

        self.CurrentIP.setText(ipAddress)
        self.CurrentRefTime.setText(str(refreshTime)+" sec")
        

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.displayedPlot = 1
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyLogix Data Acquisition')   

        # Create Buttons
        PauseButton = createIconButton('images/pause-icon.png','Press to pause',35)
        PlayButton = createIconButton('images/play-icon.png','Press to play',35)
        SettingsButton = createIconButton('images/settings-icon.png','Press to go into settings',35)
        BackwardButton = createIconButton('images/backward-icon.png','Press to go backward in time',35)
        ForwardButton = createIconButton('images/forward-icon.png','Press to go forward in time',35)
        NextPlotButton = createButton("Next Plot", "Press to display next plot", 16)

        # What to do if buttons are clicked
        PauseButton.clicked.connect(self._pause_Clicked)
        PlayButton.clicked.connect(self._play_Clicked)
        SettingsButton.clicked.connect(self.buildPopup)
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

        # Create figure for plotting
        self.fig = plt.figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        ax = self.fig.add_subplot(1,1,1)
        xs = []
        ys = []

        # Graph layout
        GraphLayout = QVBoxLayout()
        GraphLayout.addWidget(self.canvas)
        graph_widget = QWidget()
        graph_widget.setLayout(GraphLayout)

        # Add widgets to GUI
        grid.addWidget(header_widget,0,0)
        grid.addWidget(graph_widget,1,0)
        grid.addWidget(button_widget,1,1)
        
        # Set layout to main window
        self.setLayout(grid)

        

        # Establish communication with PLC
        if ipAddress == "0.0.0.0":
            DiscoverPLC()
        else:
            _update_graph(self)

    def _nextPlot(self):
        self.displayedPlot = displayedPlot + 1
        if displayedPlot > 5:
            displayedPlot = 1

    def buildPopup(self):
        self.popup_window = Popup()
        self.popup_window.show()

    def _update_graph(self):
        ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
        plt.show()
    
    def animate(i, xs, ys):

        dataToRead = displayedPlot - 1
        # Read temperature (Celsius) from TMP102
        newdata, dataNames, dataUnits = getLogixData()
        newtime = getPLCtime()

        # Add x and y to lists
        xs.append(newtime)
        ys.append(newdata[dataToRead])

        # Limit x and y lists to 20 items
        xs = xs[-30:]
        ys = ys[-30:]

        # Draw x and y lists
        ax.clear()
        ax.plot(xs, ys)

        # Format plot
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('Graph of ' + dataNames[dataToRead] + " from " + xs[0] + " to " + xs[29])
        plt.ylabel(dataNames[dataToRead])    

    def _play_Clicked(self):
        print(_getLogixData(self))

    def _pause_Clicked(self):
        print("pause")

    def _backward_Clicked(self):
        print("Backward")

    def _forward_Clicked(self):
        print("Forward")

def getPLCtime():
    with PLC() as comm:
        ret = comm.GetPLCTime()
    return ret

def DiscoverPLC():
    with PLC() as comm:
        devices = comm.Discover()
        for device in devices.value:
            if device.DeviceType == 'Programmable Logic Controller':
                if ipAddress != device.IPAddress:
                    ipAddress = device.IPAddress
                    with PLC() as comm:
                        comm.IPAddress = ipAddress
                    print("PLC found! IP address configured")
                    return

def getLogixData():
    # gets data from the PLC at the entered ipAdress.
    tag_list = [ 'LogixData1',  'LogixData2','LogixData3','LogixData4','LogixData5','LogixDataName1','LogixDataName2','LogixDataName3','LogixDataName4','LogixDataName5'
                    ,'LogixDataUnit1','LogixDataUnit2', 'LogixDataUnit3','LogixDataUnit4','LogixDataUnit5']
    with PLC() as comm:
        comm.IPAddress = ipAddress
        ret = comm.Read(tag_list)
        data = ret[0:4]
        dataName = ret[5:9] 
        dataUnit = ret[10:14]

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