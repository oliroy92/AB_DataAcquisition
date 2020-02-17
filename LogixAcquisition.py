import sys
import time

from pylogix import PLC

import numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QSizePolicy, QInputDialog, QLineEdit, QLabel
from PyQt5 import QtGui, QtCore

global ipAddress 
ipAddress = "0.0.0.0"

class Popup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Configuration')

        IPlabel = QLabel("Enter PLC IP Address:", self)
        IPlabel.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        IPlabel.move(10,5)

        self.IPtextbox = QLineEdit(self)
        self.IPtextbox.setGeometry(10,35,150,20)
        self.IPtextbox.setFont(QtGui.QFont("Arial",12))

        applyButton = QPushButton("Apply",self)
        applyButton.setToolTip('Press to apply changes')
        applyButton.clicked.connect(self.setIP)
        applyButton.move(10,60)

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

        Record = 0

        # Create Buttons
        PauseButton = _createButton('images/pause-icon.png','Press to pause',35)
        PlayButton = _createButton('images/play-icon.png','Press to play',35)
        SettingsButton = _createButton('images/settings-icon.png','Press to go into settings',35)
        BackwardButton = _createButton('images/backward-icon.png','Press to go backward in time',35)
        ForwardButton = _createButton('images/forward-icon.png','Press to go forward in time',35)

        PauseButton.clicked.connect(self._pause_Clicked)
        PlayButton.clicked.connect(self._play_Clicked)
        SettingsButton.clicked.connect(self.buildPopup)
        BackwardButton.clicked.connect(self._backward_Clicked)
        ForwardButton.clicked.connect(self._forward_Clicked)

        # Layout of GUI
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0,500)
        grid.setRowMinimumHeight(0, 500)

        # Buttons layout
        ButtonLayout = QVBoxLayout()
        button_widget = QWidget()
        button_widget.setLayout(ButtonLayout)
        button_widget.setFixedWidth(100)

        # Add Buttons to button layout
        ButtonLayout.addWidget(BackwardButton) 
        ButtonLayout.addWidget(PlayButton)
        ButtonLayout.addWidget(PauseButton)
        ButtonLayout.addWidget(ForwardButton)   
        ButtonLayout.addWidget(SettingsButton)

        # Header layout
        HeaderLayout = QHBoxLayout()
        header_widget = QWidget()
        header_widget.setLayout(HeaderLayout)
        header_widget.setFixedHeight(100)

        # Graph layout
        GraphLayout = QVBoxLayout()
        graph_widget = QWidget()
        graph_widget.setLayout(GraphLayout)
     
        # Create canvas
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        
        # Add widgets to GUI
        GraphLayout.addWidget(dynamic_canvas)
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
        self.popup_window.setGeometry(100,100,400,200)
        self.popup_window.show()

    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()

    def _play_Clicked(self):
        print("play")

    def _pause_Clicked(self):
        print("pause")

    def _backward_Clicked(self):
        print("Backward")

    def _forward_Clicked(self):
        print("Forward")

def _getLogixData(ipAddress):
    tag_list = [ 'LogixData1', 'LogixDataUnit1', 'LogixData2', 'LogixDataUnit2', 'LogixData3', 'LogixDataUnit3',
                 'LogixData4', 'LogixDataUnit4', 'LogixData5', 'LogixDataUnit5' ]
    with PLC() as comm:
        comm = PLC()
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