
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
        self.validar_array = []
        self.datos_resp = []
        self.status = False
        self.muestras = None
        self.validado = False
        self.puerto_seleccionado = None

        #self.acceleracion_absoluta  = canvas_grafica(parent=self)
        
        self.canvas = canvas_grafica(parent=self, ui=self)
        self.grafica_acceleracion_g.addWidget(self.canvas)
        self.updateConnStatus(False)
        self.refreschbotton.clicked.connect(self.refresh)
        self.guardar_btn.clicked.connect(self.guardar)
        self.verificar_botton.clicked.connect(self.verificar) #verifica la freq en el DDS
        self.validar_btn.clicked.connect(self.validar) #valida los datos (limites y rangos)
        self.conectar_botton.clicked.connect(self.connect)
        self.desconectarbotton.clicked.connect(self.disconnect)
        self.enviar_btn.clicked.connect(self.enviar)
        self.show()
        self.ser = None

    def guardar(self) -> None: 

        None

    def verificar(self) -> None: 
        try:
            hz_verf     =   int(self.freq_input.text())
            if self.status == True:
                frecuencia = hz_verf
                frecuencia_enviar =  frecuencia #chacon
                frecuencia_str = str(frecuencia)
                print(f"Frecuencia enviada: {frecuencia}") 
                print(f"Frecuencia enviada: {frecuencia_enviar}") #chacon
                self.lineEdit_8.setText(" ")
                self.lineEdit_8.setText(f"Frecuencia enviada: {frecuencia_enviar}")
                data_to_send = f"{frecuencia_enviar}\n" #chacon
                self.ser.write(data_to_send.encode('utf-8'))
                time.sleep(3)
                print(data_to_send.encode('utf-8'))
        except Exception as e:
            print("Error:", str(e))
            self.romper_event()
            self.disconnect()
        

    def enviar(self) -> None:  # Envia los datos para iniciar recopilacion de datos.
        
        None

    def validar(self) -> None:

        try: 

            
            paso        =   int(self.paso_input.text())
            min_hz      =   int(self.rango_min_input.text())
            max_hz      =   int(self.rango_max_input.text())
            ciclos      =   int(self.ciclos_input.text())
            log_mode    =   self.log_mode_comboBox.currentText()
            
        
            if not all(isinstance(valor, int) for valor in [min_hz, max_hz]) or \
                not (1 <= min_hz < max_hz <= 4000000) or \
                max_hz <= min_hz:
                    raise ValueError("Los valores de rango_minimo y rango_max no cumplen con las restricciones.")
                # Restricciones para pas_val (número par)
            if not isinstance(paso, int) or paso % 2 != 0 or not (min_hz <= paso <= max_hz):
                raise ValueError("El valor de pas_val debe ser un número entero par dentro del rango especificado.")

                # Restricciones para muestreo_val, ciclos_val y barrido_val
            if not all(isinstance(valor, int) for valor in [ciclos]) or \
            not ( 1 < ciclos):
                raise ValueError("Los valores de  ciclos_val no cumplen con las restricciones.")

            if self.uv_chek_box.isChecked():
                    self.uv     = 1
            else: 
                    self.uv     = 0

            if self.debug_radio_btn.isChecked():
                    self.debug  = 1
            else:
                    self.debug  = 0
            
            #self.validar_array=['FI'+ str(self.rango_minimo),'FM'+str(self.rango_max),'P'+ str(self.pas_val),'M'+ str(self.muestreo_val),'C'+ str(self.ciclos_val),'BA'+ str(self.barrido_val)]
            self.validar_array=[ str(min_hz),str(max_hz), str(paso),str(ciclos),str(self.debug),str(log_mode),str(self.uv)] #modificado (21/08/2024) Falta DEBUG, LOGMODE Y UV --> DF
            print(f"datos a enviar: {self.validar_array}")
            info_validar = f"Se ha verificado correctamente los datos \n "
            self.validado = True
            self.lineEdit_8.setText(" ")
            self.lineEdit_8.setText(str(info_validar))

        except ValueError as e:
            self.validado = False
            # Mostrar el mensaje de error en la interfaz
            self.lineEdit_8.setText(" ")
            info_validar = f"Error en los datos validados \n "
            self.lineEdit_8.setText(str(info_validar))
            print(str(e)) 

    def enviar_prueba(self): #revisado 22/08/2024
        
        # Parte 1
        self.muestras = ((int(self.validar_array[1])) - (int(self.validar_array[0]))) / ((int(self.validar_array[2])) + 1)
        print("Cantidad muestras:", self.muestras)
        self.lineEdit_8.setText(" ")
        self.lineEdit_8.setText("Cantidad muestras:", self.muestras)

        try:
            if self.status and self.validado:
                print(f"Datos a enviar por separado: {self.validar_array}")
                data_to_send = '/'.join(self.validar_array)
                data = f"{data_to_send}\n"
                print(f"Dato enviado: {data.encode()}")
                self.enviar_status = True 
                self.ser.write(data.encode())
                print("Esperando respuesta...")
                # Parte 2

                while True:
                    respuesta = self.ser.readline().decode().strip()  
                    print("Respuesta recibida:", respuesta)
                    if respuesta == "SYS_END":
                        print("Recibido SYS_END")
                        break
                    else:
                        self.datos_resp.append(respuesta)
                
                    # Parte 3   separa los resultados independientes
                    
                    #self.resultado_datos = self.separar_array()

                    #self.formulas() #realiza los calculos pertinentes para el analisis


                    """ cuando el almacena los datos lo ideal seria mandar esos datos
                    a la funcion de separarlos y posterior graficarlos por separado
                    posterior a esto realizar el post procesado de los datos par asi
                     obtener los resultados esperados """
                    
                    """ fig, ax = plt.subplots()
                    for sub_array in self.resultado_datos:
                        etiqueta = sub_array[1]
                        datos = sub_array[2:]
                        x = list(range(len(datos)))  

                        def map(valor, in_min, in_max, out_min, out_max):
                            return (valor - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

                        valores_y = [map(int(dato), 0, 4096, 0, 3.3) for dato in datos]  
                        ax.plot(x, valores_y, label=etiqueta)
                        
                    ax.set_xlabel('Índice')
                    ax.set_ylabel('Valor')
                    ax.set_title('Plot de datos')
                    ax.legend()
                    plt.show()  """
                                         
        except Exception as e:
            print(f"Error : {e}")
            self.enviar_status = False       
            send = "Puerto cerrado, no se puede enviar"
            self.lineEdit_8.setText(" ")
            self.lineEdit_8.setText(send)

        except KeyboardInterrupt:
            print("Programa interrumpido por el usuario.")
            self.enviar_status = False
            self.lineEdit_8.setText(" ")
            self.lineEdit_8.setText("Programa interrumpido por el usuario.")
        return        


    def updateConnStatus(self, status) -> None:
        try:
            if status:
                self.label.setText("Connected")
                self.label.setStyleSheet("background-color: lightgreen")
                self.label.adjustSize()
            else:
                self.label.setText("Disconnected")
                self.label.setStyleSheet("background-color: red")
                self.label.adjustSize()
        
        except ValueError as e:
            self.lineEdit_8.setText(" ")
            info_validar = f"Error  \n "
            self.lineEdit_8.setText(str(info_validar))
            print(str(e)) 
    
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
                    self.lineEdit_8.setText(" ")
                    self.lineEdit_8.setText("se conecto a :" , self.target_device)
            if self.status == False:
                self.ser = sr.Serial(self.target_device,
                                    baudrate=9600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    bytesize=8,
                                    timeout= None)
                print("Conectado al puerto:", self.puerto_seleccionado)
                #self.texestado.delete(1.0, tkinter.END)
                info_serial = f"Puerto: {self.ser.port} Velocidad de transmisión: {self.ser.baudrate}\n Paridad:{self.ser.parity} Bitsrate:{self.ser.bytesize}"
                self.lineEdit_8.setText(" ")
                self.lineEdit_8.setText(info_serial)
                print(info_serial)
                #self.texestado.insert("0.0", str(info_serial))
                self.status = True

        except Exception as e:
            print("Error al abrir el puerto:", str(e))

    def disconnect(self) -> None:
        try:
            if self.puerto_seleccionado == None:
                print("no se ha conectado a ningun puerto")
                self.lineEdit_8.setText(" ")
                self.lineEdit_8.setText("no se ha conectado a ningun puerto")
            else:
                self.status == True
                self.ser.close()
                print("Puerto cerrado")
        except Exception as e:
            print("Error al cerrar el puerto:", str(e))
            self.lineEdit_8.setText(" ")
            self.lineEdit_8.setText("Error al cerrar el puerto:", str(e))
        # Cierra el puerto si sigue abierto
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Forzado a cerrar el puerto")
            self.status = False
            self.lineEdit_8.setText(" ")
            self.lineEdit_8.setText("Forzado a cerrar el puerto")

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
