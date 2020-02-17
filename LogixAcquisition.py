import sys
import time

from pylogix import PLC

import numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSizePolicy, QInputDialog, QLineEdit, QLabel
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap

global ipAddress 
ipAddress = "0.0.0.0"

class Popup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configuration')

        CurrentIPlabel = QLabel("Current PLC IP Address:")
        CurrentIPlabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        CurrentIP = QLabel(ipAddress)
        CurrentIP.setFont(QtGui.QFont("Arial", 12))

        EnterIPlabel = QLabel("Enter PLC IP Address:")
        EnterIPlabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

        self.IPtextbox = QLineEdit()
        self.IPtextbox.setGeometry(10,35,150,20)
        self.IPtextbox.setFont(QtGui.QFont("Arial",12))

        applyButton = QPushButton("Apply")
        applyButton.setToolTip('Press to apply changes')
        applyButton.clicked.connect(self.setIP)
        applyButton.move(10,60)

        # Popup layout
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(CurrentIPlabel,0,0)
        grid.addWidget(EnterIPlabel,1,0)
        grid.addWidget(CurrentIP,0,1)
        grid.addWidget(self.IPtextbox,1,1)
        grid.addWidget(applyButton,2,1)

        self.setGeometry(600,600,400,100)
        self.setLayout(grid)

    def setIP(self):
        global ipAddress
        if self.IPtextbox.text() != ipAddress:
            ipAddress = self.IPtextbox.text()
            print(ipAddress)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyLogix Data Acquisition')   

        # Create Buttons
        PauseButton = _createButton('images/pause-icon.png','Press to pause',35)
        PlayButton = _createButton('images/play-icon.png','Press to play',35)
        SettingsButton = _createButton('images/settings-icon.png','Press to go into settings',35)
        BackwardButton = _createButton('images/backward-icon.png','Press to go backward in time',35)
        ForwardButton = _createButton('images/forward-icon.png','Press to go forward in time',35)

        # What to do if buttons are clicked
        PauseButton.clicked.connect(self._pause_Clicked)
        PlayButton.clicked.connect(self._play_Clicked)
        SettingsButton.clicked.connect(self.buildPopup)
        BackwardButton.clicked.connect(self._backward_Clicked)
        ForwardButton.clicked.connect(self._forward_Clicked)

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

        # Graph layout
        GraphLayout = QVBoxLayout()
        graph_widget = QWidget()
        graph_widget.setLayout(GraphLayout)
     
        # Create canvas
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        GraphLayout.addWidget(dynamic_canvas)

        # Add widgets to GUI
        grid.addWidget(header_widget,0,0)
        grid.addWidget(graph_widget,1,0)
        grid.addWidget(button_widget,1,1)
        
        # Set layout to main window
        self.setLayout(grid)

        # Update Plot
        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(100, [(self._update_canvas, (), {})])
        self._timer.start()

    def buildPopup(self):
        self.popup_window = Popup()
        self.popup_window.show()

    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()

    def _play_Clicked(self):
        print(_getLogixData(self))

    def _pause_Clicked(self):
        print("pause")

    def _backward_Clicked(self):
        print("Backward")

    def _forward_Clicked(self):
        print("Forward")

def _getLogixData(self):
    tag_list = [ 'LogixData1', 'LogixDataUnit1', 'LogixData2', 'LogixDataUnit2', 'LogixData3', 'LogixDataUnit3',
                 'LogixData4', 'LogixDataUnit4', 'LogixData5', 'LogixDataUnit5' ]
    with PLC() as comm:
        comm.IPAddress = ipAddress
        ret = comm.Read(tag_list)
    return ret

def _createButton(iconStr, toolTipStr, iconSize):
    button = QPushButton("")
    button.setToolTip(toolTipStr)
    button.setIcon(QtGui.QIcon(iconStr))
    button.setIconSize(QtCore.QSize(iconSize,iconSize))
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    return button

if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    app = MainWindow()
    app.showMaximized()
    qapp.exec_()