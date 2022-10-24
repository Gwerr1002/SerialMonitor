#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 14:26:58 2022

@author: Gerardo Ortíz Montúfar
"""

import serial
from threading import Thread
from resources.Monitor import Ui_MainWindow, QtWidgets, QtCore, list_ports
from time import sleep


class receptor(QtCore.QObject):
    messageChanged=QtCore.pyqtSignal(str)
    end = QtCore.pyqtSignal(str)
    is_alive=False
    def __init__(self,port):
        super().__init__()
        self.port = port
        self.message = ""

    def start(self):
        receptor.is_alive = True
        self.ejex=Thread(target=self.loop)
        self.ejex.start()

    def stop(self):
        receptor.is_alive = False
        self.message = ""

    def loop(self):
        self.end.emit(self.message)
        while receptor.is_alive:
            self.message=self.port.read().decode(encoding='utf-8')
            #self.message=str(self.port.read())
            self.messageChanged.emit(self.message)
        self.message="Welcome to SerialMonitorG 1.0 (SMG_1.0)\n"
        self.end.emit(self.message)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._translate = QtCore.QCoreApplication.translate

        self.SETTINGS={
            'bytesize': serial.EIGHTBITS,
            'baudrate': 9600,
            'stopbits': serial.STOPBITS_ONE,
            'timeout': None,
            'parity': serial.PARITY_NONE,
            'xonxoff': False,
            'rtscts': False,
            'dsrdtr':False
            }

        self.bits = {
            "FIVEBITS" : serial.FIVEBITS,
            "SIXBITS" : serial.SIXBITS,
            "SEVENBITS" : serial.SEVENBITS,
            "EIGHTBITS" : serial.EIGHTBITS
            }
        self.stopbits = {
            "ONE" : serial.STOPBITS_ONE,
            "ONE POINT FIVE" : serial.STOPBITS_ONE_POINT_FIVE,
            "TWO" : serial.STOPBITS_TWO
            }
        self.parity = {
            "None" : serial.PARITY_NONE,
            "Even" : serial.PARITY_EVEN,
            "Mark" : serial.PARITY_MARK,
            "Names" : serial.PARITY_NAMES,
            "ODD" : serial.PARITY_ODD,
            "Space" : serial.PARITY_SPACE
            }

        self.timeout = None
        self.baudrate = 9600
        self.rtscts = False
        self.xonxoff = False
        self.dsrdtr = False

        #configuración check box
        self.ui.EnRTSCTS.stateChanged.connect(self.En_dis_rts)
        self.ui.EnDSRDTR.stateChanged.connect(self.En_dis_dsr)
        self.ui.EnXonXoff.stateChanged.connect(self.En_dis_x)
        #configuracion combobox
        #self.ui.SelectPort.currentIndexChanged(self.updatePorts)
        #configuracion del boton
        self.ui.Start_Stop.clicked.connect(self.init)


    def En_dis_rts(self):
        self.rtscts ^= True

    def En_dis_dsr(self):
        self.dsrdtr ^= True

    def En_dis_x(self):
        self.xonxoff ^= True

    def updatePorts(self):
        for i in range(self.ui.i+1):
            self.ui.SelectPort.removeItem(i)
        self.ui.ports = {p[0]:p[0] for i,p in enumerate(list_ports.comports())}
        self.ui.i=0
        for key in self.ui.ports.keys():
            self.ui.SelectPort.addItem("")
            self.ui.SelectPort.setItemText(self.ui.i,self._translate("MainWindow",key))
            self.ui.i+=1

    def init(self):
        self.SETTINGS['bytesize'] = self.bits[self.ui.SelectBITS.currentText()]
        self.SETTINGS['baudrate'] = self.ui.SelectBaudrate.value()
        self.SETTINGS['stopbits'] = self.stopbits[self.ui.SelectStopbits.currentText()]
        if self.ui.SelectTimeout.value() == 0.0:
            self.SETTINGS['timeout'] = None
        else:
            self.SETTINGS['timeout'] = self.ui.SelectTimeout.value()
        self.SETTINGS['parity'] = self.parity[self.ui.SelectParity.currentText()]
        self.SETTINGS['xonxoff'] = self.xonxoff
        self.SETTINGS['dsrdtr'] = self.dsrdtr
        self.SETTINGS['rtscts'] = self.rtscts

        self.port = serial.Serial(self.ui.ports[self.ui.SelectPort.currentText()])
        self.port.apply_settings(self.SETTINGS)
        self.ui.Start_Stop.clicked.connect(self.stop)
        self.ui.Start_Stop.setText(self._translate("MainWindow", "Stop"))
        self.ui.plainTextEdit.clear()

        self.r = receptor(self.port)
        self.r.messageChanged.connect(self.ui.plainTextEdit.insertPlainText)
        self.r.end.connect(self.ui.plainTextEdit.setPlainText)
        self.r.start()

    def stop(self):
        self.r.stop()
        while self.r.ejex.is_alive():
            pass
        self.ui.Start_Stop.setText(self._translate("MainWindow", "Start"))
        self.updatePorts()
        self.port.close()
        self.ui.Start_Stop.clicked.connect(self.init)
        self.ui.plainTextEdit.clear()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
