import sys, os
from PyQt5 import uic
from PyQt5 import QtWidgets
global maxInputLen
maxInputLen = 15

class Input(QtWidgets.QDialog):
    def __init__(self):
        super(Input, self).__init__()
        uic.loadUi(os.path.dirname(os.path.abspath(__file__)) +  "\\numericInput.ui",self)
        self.show()
        self._initUI()

    def _initUI(self):
        self.LB_Input = self.findChild(QtWidgets.QLabel, "LB_Input")
        self.LB_Input.setText("0")
        # Numeric inputs push buttons (0-9 and .)
        self.numPB = []
        for x in range(0,10):
            self.numPB.append(self.findChild(QtWidgets.QPushButton, "PB" + str(x)))
        for i,PB in enumerate(self.numPB):
            PB.clicked.connect(self._numPressed(i))

        PBDot = self.findChild(QtWidgets.QPushButton, "PB_Dot")
        PBDot.clicked.connect(self.PBDot_Pressed)

        self.PB_Sign = self.findChild(QtWidgets.QPushButton, "PB_Sign")
        self.PB_Sign.clicked.connect(self._SignPressed)
        self.PB_Enter = self.findChild(QtWidgets.QPushButton, "PB_Enter")
        self.PB_Enter.clicked.connect(self._EnterPressed)
        self.PB_Clear = self.findChild(QtWidgets.QPushButton, "PB_Clear")
        self.PB_Clear.clicked.connect(self._ClearPressed)
        self.PB_Backspace = self.findChild(QtWidgets.QPushButton, "PB_Backspace")
        self.PB_Backspace.clicked.connect(self._ErasePressed)
        
    def _numPressed(self,i):
        def num():
            text = self.LB_Input.text()
            number = str(i)
            if number == "0" and text == "0":
                return
            elif text == "0":
                text = number
            elif len(text) >= maxInputLen:
                return
            else:
                text += str(i)
            self.LB_Input.setText(text)
        return num

    def PBDot_Pressed(self):
        text = self.LB_Input.text()
        if len(text) >= maxInputLen:
            return
        else:
            text += "."
        self.LB_Input.setText(text)

    def _EnterPressed(self):
        self.InputText = self.LB_Input.text()
        self.accept()

    def _SignPressed(self):
        text = self.LB_Input.text()
        if "-" in text:
            text = text[1:]
        else:
            if text == "0":
                return
            else:
                text = "-" + text
        self.LB_Input.setText(text)

    def _ClearPressed(self):
        self.LB_Input.setText("0")

    def _ErasePressed(self):
        text = self.LB_Input.text()
        text = text[:-1]
        if text == "":
            self.LB_Input.setText("0")
        else:
            self.LB_Input.setText(text)