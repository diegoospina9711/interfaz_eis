
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal,QEventLoop, QTimer
import serial.tools.list_ports as p
from threading import Thread
import serial , time
import threading
from queue import Queue
from time import sleep
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import pandas as exp
import serial as sr
import csv
import numpy as np
import math
import asyncio

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('interfaz.ui', self)

        self.devices = None
        self.target_device = None

        #self.acceleracion_absoluta  = canvas_grafica(parent=self)
        
        self.canvas = canvas_grafica(parent=self, ui=self)
        self.grafica_acceleracion_g.addWidget(self.canvas)
        self.updateConnStatus(False)
        self.refreschbotton.clicked.connect(self.refresh)
        self.guardar_btn.clicked.connect(self.guardar)
        self.conectar_botton.clicked.connect(self.connect)
        self.desconectarbotton.clicked.connect(self.disconnect)
        self.enviar_btn.clicked.connect(self.enviar)
        self.show()
        self.ser = None

    def guardar(self) -> None: 

        None

    def enviar(self) -> None: 
        
        None

    def usuario(self) -> None:
        hz_verf      =   self.freq_input.text()
        paso    =   self.paso_input.text()
        min_hz      =   self.rango_min_input.text()
        max_hz      =   self.rango_max_input.text()
        ciclos        =   self.ciclo_input.text()
        log_mode   =   self.log_mode_comboBox.currentText()

    def updateConnStatus(self, status) -> None:
        if status:
            self.label.setText("Connected")
            self.label.setStyleSheet("background-color: lightgreen")
            self.label.adjustSize()
        else:
            self.label.setText("Disconnected")
            self.label.setStyleSheet("background-color: red")
            self.label.adjustSize()
    
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
                self, 'Cerrar Programa',
                'Desea cerrar el programa EIS',
                QtWidgets.QMessageBox.Yes , QtWidgets.QMessageBox.No
            )

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.disconnect()
        else:
            event.ignore()
              
        
    def setComboBox(self) -> None:
        self.devicecombobox.clear()
        self.devices = p.comports()
        for ith, device in enumerate(self.devices):
             if device.name is not None:
                print(f"Device {ith + 1} : {device.name}")
                self.devicecombobox.addItem(device.name)
                self.status = False
    def refresh(self) -> None:
        self.status = False
        self.refreschbotton.setEnabled(False)
        self.setComboBox()

        
    def connect(self) -> None:
        try:
            target_device_name = self.devicecombobox.currentText()
            for device in self.devices:
                if device.name == target_device_name:
                    self.target_device = device
            if self.status == False:
                self.ser = sr.Serial(self.puerto_seleccionado,
                                    baudrate=921600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    bytesize=8,
                                    timeout= None)
                print("Conectado al puerto:", self.puerto_seleccionado)
                #self.texestado.delete(1.0, tkinter.END)
                info_serial = f"Puerto: {self.ser.port} Velocidad de transmisión: {self.ser.baudrate}\n Paridad:{self.ser.parity} Bitsrate:{self.ser.bytesize}"
                print(info_serial)
                #self.texestado.insert("0.0", str(info_serial))
                self.status = True

        except Exception as e:
            print("Error al abrir el puerto:", str(e))

    def disconnect(self) -> None:
        try:
            self.status == True
            self.ser.close()
            print("Puerto cerrado")
        except Exception as e:
            print("Error al cerrar el puerto:", str(e))
        # Cierra el puerto si sigue abierto
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Forzado a cerrar el puerto")
            self.status = False

class canvas_grafica(FigureCanvas):

    def __init__(self, parent=None, ui=None):
        self.ui = ui
        self.acc_canvas = None
        self.fig, self.ax = plt.subplots(dpi=100, figsize=(5, 5), sharey=True, facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)

    def acc_graph(self):

        try:
           
            # Actualizar el widget de la interfaz con el nuevo lienzo del gráfico """
            self.ui.grafica_acceleracion_g.addWidget( self)
            self.ui.grafica_acceleracion_g.update()

        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")


    """ def procesar_fila(self,fila):
    
        try:
            datos = fila.strip().split(',')  
            if len(datos) >= 7:
                sample_rate = float(datos[0])
                gyrx = float(datos[1])
                gyry = float(datos[2])
                gyrz = float(datos[3])
                accx = float(datos[4])
                accy = float(datos[5])
                accz = float(datos[6])
                return sample_rate, gyrx, gyry, gyrz, accx, accy, accz
            else:
                return None 
        except (ValueError, IndexError):
            return None   """
