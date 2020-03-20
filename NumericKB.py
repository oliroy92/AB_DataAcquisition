import sys, os
from PyQt5 import uic
from PyQt5 import QtWidgets

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
        PB0 = self.findChild(QtWidgets.QPushButton, "PB0")
        PB0.clicked.connect(self.PB0_Pressed)
        PB1 = self.findChild(QtWidgets.QPushButton, "PB1")
        PB1.clicked.connect(self.PB1_Pressed)
        PB2 = self.findChild(QtWidgets.QPushButton, "PB2")
        PB2.clicked.connect(self.PB2_Pressed)
        PB3 = self.findChild(QtWidgets.QPushButton, "PB3")
        PB3.clicked.connect(self.PB3_Pressed)
        PB4 = self.findChild(QtWidgets.QPushButton, "PB4")
        PB4.clicked.connect(self.PB4_Pressed)
        PB5 = self.findChild(QtWidgets.QPushButton, "PB5")
        PB5.clicked.connect(self.PB5_Pressed)
        PB6 = self.findChild(QtWidgets.QPushButton, "PB6")
        PB6.clicked.connect(self.PB6_Pressed)
        PB7 = self.findChild(QtWidgets.QPushButton, "PB7")
        PB7.clicked.connect(self.PB7_Pressed)
        PB8 = self.findChild(QtWidgets.QPushButton, "PB8")
        PB8.clicked.connect(self.PB8_Pressed)
        PB9 = self.findChild(QtWidgets.QPushButton, "PB9")
        PB9.clicked.connect(self.PB9_Pressed)
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
        

    def PB0_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
                return
        elif len(text) >= 8:
                return
        else:
            text += "0"
        self.LB_Input.setText(text)
    
    def PB1_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "1"
        elif len(text) >= 8:
            return
        else:
            text += "1"
        self.LB_Input.setText(text)
    
    def PB2_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "2"
        elif len(text) >= 8:
            return
        else:
            text += "2"
        self.LB_Input.setText(text)

    def PB3_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "3"
        elif len(text) >= 8:
            return
        else:
            text += "3"
        self.LB_Input.setText(text)    

    def PB4_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "4"
        elif len(text) >= 8:
            return
        else:
            text += "4"
        self.LB_Input.setText(text)

    def PB5_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "5"
        elif len(text) >= 8:
            return
        else:
            text += "5"
        self.LB_Input.setText(text)
    
    def PB6_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "6"
        elif len(text) >= 8:
            return
        else:
            text += "6"
        self.LB_Input.setText(text)

    def PB7_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "7"
        elif len(text) >= 8:
            return
        else:
            text += "7"
        self.LB_Input.setText(text)
    
    def PB8_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "8"
        elif len(text) >= 8:
            return
        else:
            text += "8"
        self.LB_Input.setText(text)

    def PB9_Pressed(self):
        text = self.LB_Input.text()
        if text == "0":
            text = "9"
        elif len(text) >= 8:
            return
        else:
            text += "9"
        self.LB_Input.setText(text)

    def PBDot_Pressed(self):
        text = self.LB_Input.text()
        if "." in text:
            return
        elif len(text) >= 8:
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