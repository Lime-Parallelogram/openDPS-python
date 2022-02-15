#---------------------------------------------------------------------#
# File: /home/will/OneDrive/PiSpace/ByProject/Power Supply/Python-Controller/DPS3005.py
# Project: Power Supply/Python-Controller
# Created Date: Tuesday, February 15th 2022, 10:26:50 am
# Description: A python module that allows for communication with DPS3005 module
# Author: Will Hall
# Copyright (c) 2022 Lime Parallelogram
# -----
# Last Modified: Tue Feb 15 2022
# Modified By: Will Hall
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	---------------------------------------------------------
# 2022-02-15	WH	Added power control functionality
# 2022-02-15	WH	Added basic register read and write functionality
#---------------------------------------------------------------------#
# ------------------------------ Imports modules ----------------------------- #
from ast import With
import bluetooth
import struct
import time

# ----------------------------- Program constants ---------------------------- #
DEVICE_ADDRESS = 0x01 #The address that the device itself responds to
AFTER_COMMAND_DELAY = 0.1

# ------------------------- Power Supply Class Object ------------------------ #
class DPS3005:
    """Controller for DPS3005 power supply"""

    # -- Initialise attributes and start connection -- #
    def __init__(self):
        # Device Attributes
        self.voltsOut = 0
        self.ampsOut = 0
        self.powerOut = 0
        self.powerOn = 0
        self.voltsSet = 0
        self.ampsSet = 0
    
    def connect(self,deviceMAC):
        #Connect to bluetooth socket
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((deviceMAC,1)) #Connect to specified device on RFCOMM port 1
        print("Device Successfully Connected!")

        time.sleep(0.06)

        self.updateAttributes()

    # -- Calculate the CRC Value for a data set -- #
    def _calcCRC(self,data):
        register = 0xFFFF # Fill register with 1

        for byte in data: # Run for all bytes
            register ^= byte
            for i in range(8):
                lsb = register & 1
                register = register >> 1
                if lsb:
                    register ^= 0xA001
            
        return register & 0xff, register >> 8

    # -- Split a 4-digit hex to two two digit -- #
    def _splitBytes(self, twoBytes): # Convert a 16-bit hex value to two 8-bit bytes
        return divmod(twoBytes, 0x100)

    # -- Write a value to device regisers -- #
    def writeRegister(self,register,data):
        # Build message to send
        functionCode = 0x6
        regHi, regLo = self._splitBytes(register)
        datHi, datLo = self._splitBytes(data)
        CRCHi, CRCLo = self._calcCRC([DEVICE_ADDRESS,functionCode,regHi,regLo,datHi,datLo])
        msg = struct.pack('8B', 
                            DEVICE_ADDRESS,
                            functionCode,
                            regHi, regLo,
                            datHi, datLo,
                            CRCHi, CRCLo)
        
        self.socket.send(msg)

        readback = self.socket.recv(10) #Ignore response for now
        time.sleep(AFTER_COMMAND_DELAY)
    
    # -- Read a value from 1 or more device registers -- #
    def readRegisters(self,startRegister,numRegisters=1): #Read data from registers of device
        if numRegisters > 2:
            raise "Too many registers selected! " #Device will only send back data from up to two different registers

        # Send read data request
        functionCode = 0x03
        startRegHi, startRegLo = 0, startRegister
        numRegHi, numRegLo = 0, numRegisters
        CRCHi, CRCLo = self._calcCRC([DEVICE_ADDRESS,functionCode,startRegHi,startRegLo,numRegHi,numRegLo])
        msg = struct.pack('8B', 
                            DEVICE_ADDRESS,
                            functionCode,
                            startRegHi, startRegLo,
                            numRegHi, numRegLo,
                            CRCHi, CRCLo)

        self.socket.send(msg)

        #Read the response data from device
        readback = self.socket.recv(10)
        
        data = []
        for reg in range(numRegisters):
            data.append(int.from_bytes(readback[3+2*reg:5+2*reg],"big"))
        
        time.sleep(AFTER_COMMAND_DELAY)
        return data
    
    # -- Close the device socket -- #
    def close(self):
        self.socket.close()

    # -- Update the class' attributes to match the registers in the device -- #
    def updateAttributes(self):
        data = self.readRegisters(0,2)
        self.voltsSet = data[0] /100
        self.ampsSet = data[1] /1000
        data = self.readRegisters(2,2)
        self.voltsOut = data[0] /100
        self.ampsOut = data[1] /1000
        data = self.readRegisters(4,2)
        self.powerOut = data[0] /100
        self.voltsIn = data[1]

        self.powerOn = self.readRegisters(9)[0]
    
    # -- Getter methods -- #
    def getVoltageOut(self):
        return self.voltsOut
    
    def getCurrentOut(self):
        return self.ampsOut
    
    def getPowerOut(self):
        return self.powerOut

    def getPowerState(self):
        return self.powerOn

    def getAll(self):
        return {"voltsSet": self.voltsSet,
                "ampsSet": self.ampsSet,
                "voltsOut": self.voltsOut,
                "ampsOut": self.ampsOut,
                "powerOut": self.powerOut,
                "powerState": self.powerOn
        }

    # -- Change Targets -- #
    def setVoltage(self, voltage):
        self.writeRegister(0, int(voltage*100))
        self.updateAttributes()
    
    def setCurrent(self,current):
        self.writeRegister(1,int(current*1000))
        self.updateAttributes()
    
    def setPowerState(self,state):
        self.writeRegister(9,state)
        self.powerOn = state
    
    def togglePowerState(self):
        self.powerOn ^= 1
        self.setPowerState(self.powerOn)