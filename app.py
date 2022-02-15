#---------------------------------------------------------------------#
# File: /home/will/OneDrive/PiSpace/ByProject/Power Supply/Python-Controller/app.py
# Project: Power Supply/Python-Controller
# Created Date: Tuesday, February 15th 2022, 10:23:36 am
# Description: A custom-written program that interacts with a DPS3005 power supply module over bluetooth
# Author: Will Hall
# Copyright (c) 2022 Lime Parallelogram
# -----
# Last Modified: Tue Feb 15 2022
# Modified By: Will Hall
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	---------------------------------------------------------
#---------------------------------------------------------------------#
# ------------------------------ Imports Modules ----------------------------- #
from tkinter import Widget
from DPS3005 import DPS3005
from time import sleep
import PyQt5.QtCore as qtCore
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QColor
from darktheme.widget_template import DarkPalette
import sys

# ----------------------------- Program constants ---------------------------- #
DEVICE_MAC = "98:DA:20:01:13:09"

supply = DPS3005()

# -------------------------- Main Application Window ------------------------- #
class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("dashboard.ui", self)

        self.voltsSubmit.clicked.connect(self.updateVolts)
        self.ampsSubmit.clicked.connect(self.updateAmps)
        self.actionConnect.triggered.connect(self.connect)
        
    # -- Update the displayed set volts -- #
    def updateVolts(self):
        volts = self.voltsSpinBox.value()
        self.voltsSetting.display(volts)
        supply.setVoltage(volts)
    
    # -- Update the displayed amps value -- #
    def updateAmps(self):
        amps = self.ampsSpinBox.value()
        self.ampsSetting.display(amps)
        supply.setCurrent(amps)

    # -- Connect to device -- #
    def connect(self):
        print("Connecting To Device")
        supply.connect(DEVICE_MAC)
    
    # -- Disconnect device -- #
    def disconnect(self):
        print("Disconnecting Device")
        supply.close()

# ------------------------ Initiate Window and loading ----------------------- #
app = QApplication(sys.argv)
app.setPalette(DarkPalette())

window = DashboardWindow()
window.show()

app.exec()

