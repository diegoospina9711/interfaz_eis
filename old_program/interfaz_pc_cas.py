#///////////////////////////////////////////////////////////////////////////
        #   Diego Alejandro Ospina Ceron 
        #   Programa de base para la interfaz de la plataforma IEESC 
        #   utilizando python
#///////////////////////////////////////////////////////////////////////////

import serial.tools.list_ports as p
import pandas as exp
import serial as sr
import random
import time
from tkinter import *
import tkinter
from tkinter import filedialog 
import PIL 
from PIL import Image
import os
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkImage
from customtkinter import CTkTabview
import serial , time
import tkinter.messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
global port 
global ports
import matplotlib.gridspec as gridspec
from time import perf_counter
import asyncio


ctk.set_appearance_mode("system") #
ctk.set_default_color_theme("blue") 

def actualizar_puerto():
    ports=p.comports()
    port=[]
    for i in ports:
        port.append(i.device)
    print(port)
    return port
class app(tkinter.Tk):

    def __init__(self):
        super().__init__()
        global datos_reb;   global rango_minimo;    global rango_max;   global pas_val; 
        global rgr_val; global ciclos_val;  global barrido_val; global port
        global ports;   global puerto_seleccionado;    global data_example;    global tag; global muestreo_val
        #///////////////////////////////////////////////////////////////////////////
        # data ejemplo para grafica 
        self.data_example = [round(random.uniform(1.000, 3.999),3) for _ in range(100)]
        self.timer_interval = 250  
        self.plot_duration = 5000 
        #///////////////////////////////////////////////////////////////////////////
        #valores  fijos:
        self.rgr=None
        self.rref_val=None  
        #///////////////////////////////////////////////////////////////////////////
        #Configuracion puertos y puerto serial
        #///////////////////////////////////////////////////////////////////////////
        self.puerto_seleccionado = None
        self.ports = port 
        self.ser = None
        self.data = np.array([])
        self.end_time = None
        self.status = False
        self.validar_array = None
        self.validado = False
        self.line = None
        self.enviar_status = False
        self.Vrgr= None
        self.Vrref= None
        self.rango_minimo = None
        ports = actualizar_puerto()
        self.datos_resp = []
        self.resultado_datos =[]
        
        #///////////////////////////////////////////////////////////////////////////
        #Configuracion GUI principal
        #///////////////////////////////////////////////////////////////////////////

        self.title("Programa atenuador IEESC UAO - 2024")
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_rowconfigure((0, 1, 2,3), weight=1)
        self.sidebar_frame = ctk.CTkFrame(self, width=1,height=1, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        self.sidebar_frame.grid_columnconfigure(1, weight=1)
        current_path= os.path.dirname(os.path.realpath(__file__))

        logo_uao = ctk.CTkImage(Image.open(current_path + "./UAO-logo-acreditacion.png"), size=(100,55))
        self.logo_uao = ctk.CTkLabel(self,bg_color="transparent",compound= "left", image= logo_uao,text="")
        self.logo_uao.grid(row=0, column=0, padx=0, pady=0,sticky="w")
        self.tabview = ctk.CTkTabview(self, height= 100, width=100)
        self.tabview.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.tabview.add("conexion") # create the 'conexion' tab
        self.tabview.tab("conexion").grid_columnconfigure(0, weight=1) 
        self.tabview.tab("conexion").grid_rowconfigure(0, weight=1) 
        self.tabview.add("ajuste")
        self.tabview.tab("ajuste").grid_columnconfigure(0, weight=1)
        self.tabview.tab("ajuste").grid_rowconfigure(0, weight=1)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#--------------------------------------- conexion space ----------------------------------------------------------
        #TAB 1 
        #boton para actualizar los puertos COM
        self.boton_actualizar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="actualizar", 
                                                        command=actualizar_puerto)
        self.boton_actualizar.grid(row=1, column=0, padx=5, pady=5)
        #label puertos
        self.puertos_label = ctk.CTkLabel(self.tabview.tab("conexion"), text="puertos", font=("roboto",15))
        self.puertos_label.grid(row=1, column=1, padx=5, pady=5)
        #lista de puertos
        self.lista_puertos=ctk.CTkOptionMenu(self.tabview.tab("conexion"),width= 60, height= 10,values=ports,command=self.seleccion_puerto)
        self.lista_puertos.grid(row=1, column=2, padx=5, pady=5)
        #boto para conectar
        self.boton_conectar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="conectar", 
                                                        command=self.conectar_puerto)
        self.boton_conectar.grid(row=1, column=3, padx=5, pady=5)

        self.frecuencia = ctk.CTkEntry(self.tabview.tab("conexion"), width= 60, height= 10, placeholder_text= "Freq") # entrada 1 
        self.frecuencia.grid(row=2, column=0, padx=5, pady=5)  

        self.puertos_label = ctk.CTkLabel(self.tabview.tab("conexion"), text="Hz", font=("roboto",15))
        self.puertos_label.grid(row=2, column=1, padx=5, pady=5)
        self.boton_verificar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="verificar", 
                                                        command=self.freq_verif_event)
        self.boton_verificar.grid(row=2, column=2, padx=5, pady=5)
        self.boton_romper = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="romper", 
                                                        command=self.romper_event)
        self.boton_romper.grid(row=2, column=3, padx=5, pady=5)
        #self.configuracion_frame = ctk.CTkScrollableFrame(self, label_text="configuración")
        #self.configuracion_frame.grid(row=3, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        #self.configuracion_label = ctk.CTkLabel(self.tabview.tab("Configuracion"), text="configuracion", font=("roboto",15))
        #self.configuracion_label.grid(row=0, column=2, padx=5, pady=5)
        #-------------------------------------- Ajuste space ------------------------------------------------------
        #TAB 2 
        self.tag_config_label = ctk.CTkLabel(self.tabview.tab("ajuste"), text="Tag", font=("roboto",15))
        self.tag_config_label.grid(row=1, column=0, padx=5, pady=5)
        self.modelos_list=ctk.CTkOptionMenu(self.tabview.tab("ajuste"),width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.modelos_list.grid(row=1, column=1, padx=5, pady=5)
        self.tag_ajuste_label = ctk.CTkLabel(self.tabview.tab("ajuste"), text="Tag", font=("roboto",15))
        self.tag_ajuste_label.grid(row=1, column=2, padx=5, pady=5)
        self.tag_ajuste_list=ctk.CTkOptionMenu(self.tabview.tab("ajuste"),width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.tag_ajuste_list.grid(row=1, column=3, padx=0, pady=0)
        self.poblacion_ajuste_label = ctk.CTkLabel(self.tabview.tab("ajuste"), text="poblacion", font=("roboto",15))
        self.poblacion_ajuste_label.grid(row=2, column=0, padx=5, pady=5)
        self.poblacion_ajuste_entry = ctk.CTkEntry(self.tabview.tab("ajuste"),width= 60, height= 10 )
        self.poblacion_ajuste_entry.grid(row=2, column=1, padx=5, pady=5)
        self.poblacion_dft_ajuste_entry = ctk.CTkCheckBox(self.tabview.tab("ajuste"), width= 20, height= 10, checkmark_color="white", text= "Dft")
        self.poblacion_dft_ajuste_entry.grid(row=2, column=2, padx=5, pady=5)
        self.interacciones_ajuste_label = ctk.CTkLabel(self.tabview.tab("ajuste"), text="interaciones", font=("roboto",15))
        self.interacciones_ajuste_label.grid(row=3, column=0, padx=5, pady=5)
        self.interacciones_ajuste_entry = ctk.CTkEntry(self.tabview.tab("ajuste"),width= 60, height= 10 )
        self.interacciones_ajuste_entry.grid(row=3, column=1, padx=5, pady=5)
        self.interacciones_acp_ajuste_entry = ctk.CTkCheckBox(self.tabview.tab("ajuste"), width= 20, height= 10, checkmark_color="white", text= "Acp")
        self.interacciones_acp_ajuste_entry.grid(row=3, column=2, padx=5, pady=5)
        self.correr_muestra = ctk.CTkButton(self.tabview.tab("ajuste"),anchor="center", compound="left", width= 60, height= 10, text="correr", command=self.sidebar_button_event)
        self.correr_muestra.grid(row=3, column=3, padx=5, pady=5)
        #------------------------------------------------ configuracion space --------------------------------------------
        # frame de ajuste
        self.ajuste_frame= ctk.CTkFrame(self,width=100, height=100, corner_radius=10 )
        self.ajuste_frame.grid(row=2, column=0, sticky="w")
        self.rango_label = ctk.CTkLabel(self.ajuste_frame, text="Rango", font=("roboto",15))
        self.rango_label.grid(row=0, column=0, padx=0, pady=5)
        #entrada de rango
        self.rango_entry = ctk.CTkEntry(self.ajuste_frame,width= 60, height= 10, placeholder_text= "minHz") # entrada 1 
        self.rango_entry.grid(row=0, column=1, padx=5, pady=5,sticky="w") 
        #label rango hz
        self.hz_config_label = ctk.CTkLabel(self.ajuste_frame, text="Hz", font=("roboto",15))
        self.hz_config_label.grid(row=0, column=2, padx=5, pady=5,sticky="w")
        #entrada de hz
        self.hz_config_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "maxHz") # entrada 1 
        self.hz_config_entry.grid(row=0, column=3, padx=5, pady=5,sticky="w") 
        #label de hz
        self.hz_config_label = ctk.CTkLabel(self.ajuste_frame, text="Hz", font=("roboto",15))
        self.hz_config_label.grid(row=0, column=4, padx=5, pady=5,sticky="w")
        self.paso_label = ctk.CTkLabel(self.ajuste_frame, text="paso", font=("roboto",15))
        self.paso_label.grid(row=1, column=0, padx=5, pady=5)
        #entrada de hz
        self.paso_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "int") # entrada 1 
        self.paso_entry.grid(row=1, column=1, padx=5, pady=5,sticky="w") 
        #label de hz
        self.hz_config_label = ctk.CTkLabel(self.ajuste_frame, text="Hz", font=("roboto",15))
        self.hz_config_label.grid(row=1, column=2, padx=5, pady=5,sticky="w")
        self.boton_validar = ctk.CTkButton(self.ajuste_frame,anchor="center", compound="left", width= 60, height= 10, text="Validar", command=self.rangos_datos_event)
        self.boton_validar.grid(row=1, column=3, padx=5, pady=5,sticky="w")
        self.d_f = ctk.CTkCheckBox(self.ajuste_frame, width= 20, height= 10, checkmark_color="white", text= "D.F",command=self.df_event)
        self.d_f.grid (row=1, column=4, padx=5, pady=5,sticky="w")
        # linea muestreo
        self.muestreo_config_label = ctk.CTkLabel(self.ajuste_frame, text="muestreo", font=("roboto",15))
        self.muestreo_config_label.grid(row=2, column=0, padx=5, pady=5)
        self.muestreo_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "int") # entrada 1 
        self.muestreo_entry.grid(row=2, column=1, padx=5, pady=5,sticky="w") 
        self.rgr_config_label = ctk.CTkLabel(self.ajuste_frame, text="RGr", font=("roboto",15))
        self.rgr_config_label.grid(row=2, column=2, padx=5, pady=5,sticky="w")
        self.rgr_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "9.17", state="readonly") # entrada 1 
        self.rgr_entry.grid(row=2, column=3, padx=5, pady=5,sticky="w") 
        self.ohm_config_label = ctk.CTkLabel(self.ajuste_frame, text="Ohm", font=("roboto",15))
        self.ohm_config_label.grid(row=2, column=4, padx=5, pady=5,sticky="w")
         # linea ciclos
        self.ciclos_config_label = ctk.CTkLabel(self.ajuste_frame, text="Ciclos", font=("roboto",15))
        self.ciclos_config_label.grid(row=3, column=0, padx=5, pady=5)
        self.ciclos_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "int") # entrada 1 
        self.ciclos_entry.grid(row=3, column=1, padx=5, pady=5,sticky="w") 

        self.rref_config_label = ctk.CTkLabel(self.ajuste_frame, text="Rref", font=("roboto",15))
        self.rref_config_label.grid(row=3, column=2, padx=5, pady=5,sticky="w")

        self.rref_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "Float") # entrada 1 
        self.rref_entry.grid(row=3, column=3, padx=5, pady=5,sticky="w") 
        self.ohm_config_label = ctk.CTkLabel(self.ajuste_frame, text="Ohm", font=("roboto",15))
        self.ohm_config_label.grid(row=3, column=4, padx=5, pady=5,sticky="w")
         # linea barrido
        self.barrido_config_label = ctk.CTkLabel(self.ajuste_frame, text="barrido", font=("roboto",15))
        self.barrido_config_label.grid(row=4, column=0, padx=5, pady=5)
        self.barrido_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "int") # entrada 1 
        self.barrido_entry.grid(row=4, column=1, padx=5, pady=5,sticky="w") 
        self.ajuste_config_label = ctk.CTkLabel(self.ajuste_frame, text="ajuste", font=("roboto",15))
        self.ajuste_config_label.grid(row=4, column=2, padx=5, pady=5,sticky="w")
        self.ajuste_list=ctk.CTkOptionMenu(self.ajuste_frame,width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.ajuste_list.grid(row=4, column=3, padx=5, pady=5,sticky="w")
        
        #linea tag
        self.tag_config_label = ctk.CTkLabel(self.ajuste_frame, text="Tag", font=("roboto",15))
        self.tag_config_label.grid(row=5, column=0, padx=5, pady=5)

        self.tag_entry = ctk.CTkEntry(self.ajuste_frame, width= 120, height= 10,placeholder_text= "String") # entrada 1 
        self.tag_entry.grid(row=5, column=1,columnspan=2, padx=5, pady=5,sticky="w")

        self.boton_tag = ctk.CTkButton(self.ajuste_frame,anchor="center", compound="left", width= 60, height= 10, text="Enviar", 
                                                        command=self.enviar_prueba)
        self.boton_tag.grid(row=5, column=3, padx=5, pady=5,sticky="w")

        #------------------------------------------------ grafica space -----------------------------------------

        self.fig = ctk.CTkFrame(self,width=500, height=400, corner_radius=0 )
        self.fig.grid(row=1, column=1, sticky="w", rowspan=2, columnspan=2)
        self.fig_size = Figure(figsize=(500 / 100, 400 / 100), dpi=100)
        self.plot_area = self.fig_size.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig_size, master=self.fig)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        #------------------------------------------------ vista space --------------------------------------------
        self.vista_frame = ctk.CTkFrame(self,width=50, height=50, corner_radius=0 )
        self.vista_frame.grid(row=3, rowspan=1, column=1, sticky="sew")
        self.tag_vista_label = ctk.CTkLabel(self.vista_frame, text="Tag", font=("roboto",15))
        self.tag_vista_label.grid(row=0, column=0, padx=5, pady=10)
        self.tag_vista_list=ctk.CTkOptionMenu(self.vista_frame,width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.tag_vista_list.grid(row=0, column=1, padx=0, pady=10,sticky="w")

        self.boton_exportar = ctk.CTkButton(self.vista_frame,anchor="center", compound="left", width= 60, height= 10, text="Exportar", 
                                                        command=self.exportar_event)
        self.boton_exportar.grid(row=1, column=0, padx=5, pady=9,sticky="w")
        self.boton_importar = ctk.CTkButton(self.vista_frame,anchor="center", compound="left", width= 60, height= 10, text="Importar", 
                                                        command=self.sidebar_button_event)
        self.boton_importar.grid(row=2, column=0, padx=5, pady=5,sticky="w")
        self.boton_eliminar = ctk.CTkButton(self.vista_frame,anchor="center", compound="left", width= 60, height= 10, text="Eliminar", 
                                                        command=self.sidebar_button_event)
        self.boton_eliminar.grid(row=1,rowspan=1, column=1, padx=5, pady=5,sticky="nsew")
        #------------------------------------------------ info visualizacion space --------------------------------------------
        self.infovi_frame = ctk.CTkFrame(self,width=50, height=50, corner_radius=0 )
        self.infovi_frame.grid(row=2,rowspan=2, column=2, sticky="sew")

        self.texestado = ctk.CTkTextbox(self.infovi_frame,width= 300 , height=30)
        self.texestado.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky="w")

        #------------------------------------------------ visualizacion ------------------------------------------------------
        self.tag_visua_label = ctk.CTkLabel(self.infovi_frame, text="Tag", font=("roboto",15))
        self.tag_visua_label.grid(row=1, column=0, padx=5, pady=5,sticky="nsew")
        

        self.tag_visua_list=ctk.CTkOptionMenu(self.infovi_frame,width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.tag_visua_list.grid(row=1, column=1, padx=0, pady=0,sticky="w")

        self.plot_Z_label = ctk.CTkLabel(self.infovi_frame, text="Plot", font=("roboto",15))
        self.plot_Z_label.grid(row=1, column=2, padx=5, pady=5)

        self.plot_Z_list=ctk.CTkOptionMenu(self.infovi_frame,width= 60, height= 10,values=["Z/PH","Xc/Rc","I/V","Xc VS Rc"],
                                                     command=self.z_option)
        self.plot_Z_list.grid(row=1, column=3, padx=0, pady=0,sticky="w")
        
        self.plot_Z_boton = ctk.CTkButton(self.infovi_frame,anchor="center", compound="left", width= 60, height= 10, text="ver", 
                                                        command=self.ver_Resultados)
        self.plot_Z_boton.grid(row=1, column=4, padx=5, pady=5,sticky="nsew")

        self.tipo_label = ctk.CTkLabel(self.infovi_frame, text="Tipo", font=("roboto",15))
        self.tipo_label.grid(row=2, column=0, padx=5, pady=5)

        self.tipo_label=ctk.CTkOptionMenu(self.infovi_frame,width= 60, height= 10,values=["1","2","3","4"],command=self.menu)
        self.tipo_label.grid(row=2, column=1, padx=0, pady=0,sticky="w")

        self.ac = ctk.CTkCheckBox(self.infovi_frame, width= 20, height= 10, checkmark_color="white", text= "A.C")
        self.ac.grid (row=2, column=2, padx=5, pady=5,sticky="w")

        self.ac_boton = ctk.CTkButton(self.infovi_frame,anchor="center", compound="left", width= 60, height= 10, text="CLC", 
                                                        command=self.sidebar_button_event)
        self.ac_boton.grid(row=2, column=3, padx=5, pady=5,sticky="nsew")
        #ajuste dos
        #self.ajuste_two_frame= ctk.CTkFrame(self,width=140, corner_radius=0)
        #self.ajuste_two_frame.grid(row=2, column=0, sticky="nsew")

        #self.ajuste_ajuste_label = ctk.CTkLabel(self.tabview.tab("ajuste"), text="Ajuste", font=("roboto",15))
        #self.ajuste_ajuste_label.grid(row=0, column=2, padx=5, pady=5)
        #------------------------------------------------ plot 1------------------------------------------------------------

        #------------------------------------------------ plot 2------------------------------------------------------------

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def seleccion_puerto(self, event=None): #seleccion del puerto interaccion (revisado 10/04/2024)
            actualizar_puerto()
            self.puerto_seleccionado = self.lista_puertos.get()
            print("Se selecciono el puerto: ", self.puerto_seleccionado)
            return self.puerto_seleccionado

    def romper_event(self): # Romper puerto serial (revisado 10/04/2024)

        try:
            if self.status == True:
                puerto_seleccionado = self.seleccion_puerto()
                print("en romper puerto")
                #self.ser = sr.Serial(''.join(puerto_seleccionado), 115200)
                self.ser.close()
                plt.close('all')
                print("Puerto cerrado")
                self.texestado.delete(1.0, tkinter.END)
                info_serial = f"Se ha roto el puerto: {self.ser.port} \n "
                self.texestado.insert("0.0", str(info_serial))
                self.status = False
        except Exception as e:
            print("Error al cerrar el puerto:", str(e))
        # Cierra el puerto si sigue abierto
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Forzado a cerrar el puerto")
            self.status = False

    def conectar_puerto(self): #(revisado 10/04/2024)
        try:
            if self.status == False:
                self.ser = sr.Serial(self.puerto_seleccionado,
                                    baudrate=921600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    bytesize=8,
                                    timeout= None)
                print("Conectado al puerto:", self.puerto_seleccionado)
                self.texestado.delete(1.0, tkinter.END)
                info_serial = f"Puerto: {self.ser.port} Velocidad de transmisión: {self.ser.baudrate}\n Paridad:{self.ser.parity} Bitsrate:{self.ser.bytesize}"
                self.texestado.insert("0.0", str(info_serial))
                self.status = True

        except Exception as e:
            print("Error al abrir el puerto:", str(e))
    
    def freq_verif_event(self): # (revisado con modificaciones  10/04/2024)   EN PROCESO, DEPENDE DE LA LECTURA DE CHACON
        try:
            if self.status == True:
                frecuencia = self.frecuencia.get()
                #frecuencia_enviar = 'F' + frecuencia #chacon
                frecuencia_enviar =  frecuencia #chacon
                frecuencia_str = str(frecuencia)
                #print(f"Frecuencia enviada: {frecuencia}") 
                print(f"Frecuencia enviada: {frecuencia_enviar}") #chacon
                #data_to_send = f"{'ADC'}\n" #chacon
                #self.ser.write(data_to_send.encode('utf-8'))
                data_to_send = f"{frecuencia_enviar}\n" #chacon
                self.ser.write(data_to_send.encode('utf-8'))
                #time.sleep(3)
                #data_to_send = f"{'F50000'}\n" #chacon
                #Data_to_send = f"{'ADCOFF'}\n" #chacon
                #data_to_send = f"{frecuencia}\n" 
                #self.ser.write(data_to_send.encode('utf-8'))
                print(data_to_send.encode('utf-8'))
                #datos = self.ser.readline().decode().strip()
                #print("recibido...")
                #print(datos.encode('utf-8'))
                #print(datos)
                #verificar_dato = datos.encode('utf-8')
                #self.end_time = self.get_current_time() + self.plot_duration
                #if datos == 'b':
                   # print("en salida")
                    #self.romper_event()
                #self.schedule_plot_data()
        except Exception as e:
            print("Error:", str(e))
            self.romper_event()

#////////////////////////////////////////////////////////////////////////////////////////////////////////       
    def formulas(self): #///////////////////////////////   IMPORTANTE    ////////////////////////////////
#//////////////////////////////    IMPORTANTE    ////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////
#                           R = resistencia real
#                            Z = resistencia impedancia 

#////////////////   necesario que se realice en otro hilo para  /////////////////////////////////////////
#////////////////   poder ejecutar simultaneidad de datos       /////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////
        data = self.resultado_datos
        Rreal   =   []
        Rz      =   []
        #programa que divida las r de las z 
        for item in data:
            if item.endswith('R'):
                Rreal.append(item)
            elif item.endswith('Z'):
                Rz.append(item)

        Rreal_num = [int(item[1:]) for item in Rreal]
        Rz_num = [int(item[1:]) for item in Rz]

        plt.figure(figsize=(10, 6))
        plt.plot(Rreal_num, 'bo-', label='Rreal')
        plt.plot(Rz_num, 'ro-', label='Rz')
        plt.xlabel('muestras')
        plt.ylabel('Valores de R')
        plt.title('Rreal vz Rz')
        plt.legend()
        plt.grid(True)
        plt.show()
        

    def schedule_plot_data(self): # Programa para plotear los datos
    
        if self.get_current_time() < self.end_time:
            # Ejecutar plot_data y programar la próxima llamada
            self.plot_data()
            self.after(self.timer_interval, self.schedule_plot_data)
        else:
            # Si ha pasado el tiempo total, cerrar el puerto serial
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("verificacion terminada")
   
    def get_current_time(self):
        # Función de utilidad para obtener el tiempo actual
        return int(round(time.time() * 1000))

    def plot_data(self):
        if self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                #value = 'F' + line #PROGRAMA CHACON
                value = int(line)
                self.data = np.append(self.data, value)
                print(value)
                self.plot_area.clear()
                self.plot_area.plot(self.data)
                self.canvas.draw()
            except (ValueError, UnicodeDecodeError) as e:
                print("Error en plot_data:", str(e))

    def rangos_datos_event(self): #(revisado 10/04/2024)
        try:
            self.rango_minimo = int(self.rango_entry.get())
            self.rango_max = int(self.hz_config_entry.get())
            self.pas_val = int(self.paso_entry.get())
            self.muestreo_val = int(self.muestreo_entry.get())
            self.rgr_val = self.rgr_entry.get()
            self.rref_val = self.rgr_entry.get()
            self.ciclos_val = int(self.ciclos_entry.get())
            self.barrido_val = int(self.barrido_entry.get())
            tag = self.tag_entry.get()
            
            if not all(isinstance(valor, int) for valor in [self.rango_minimo, self.rango_max]) or \
            not (1 <= self.rango_minimo < self.rango_max <= 4000000) or \
            self.rango_max <= self.rango_minimo:
                raise ValueError("Los valores de rango_minimo y rango_max no cumplen con las restricciones.")
            # Restricciones para pas_val (número par)
            if not isinstance(self.pas_val, int) or self.pas_val % 2 != 0 or not (self.rango_minimo <= self.pas_val <= self.rango_max):
                raise ValueError("El valor de pas_val debe ser un número entero par dentro del rango especificado.")

            # Restricciones para muestreo_val, ciclos_val y barrido_val
            if not all(isinstance(valor, int) for valor in [self.muestreo_val, self.ciclos_val, self.barrido_val]) or \
            not (1 < self.muestreo_val < 10 and 1 < self.ciclos_val < 10 and (self.barrido_val == 1 or (1 < self.barrido_val < 10))):
                raise ValueError("Los valores de muestreo_val, ciclos_val y barrido_val no cumplen con las restricciones.")

            #self.validar_array=['FI'+ str(self.rango_minimo),'FM'+str(self.rango_max),'P'+ str(self.pas_val),'M'+ str(self.muestreo_val),'C'+ str(self.ciclos_val),'BA'+ str(self.barrido_val)]
            self.validar_array=[ str(self.rango_minimo),str(self.rango_max), str(self.pas_val),str(self.ciclos_val)] #modificado (16/08/2024) Falta DEBUG, LOGMODE Y UV --> DF
            print(f"datos a enviar: {self.validar_array}")
            self.texestado.delete(1.0, tkinter.END)
            info_validar = f"Se ha verificado correctamente los datos \n "
            self.validado = True
            self.texestado.insert("0.0", str(info_validar))

        except ValueError as e:
            self.validado = False
            # Mostrar el mensaje de error en la interfaz
            self.texestado.delete(1.0, tkinter.END)
            self.texestado.insert("0.0", str(e))

    def Enviar(self): #(revisado 07/05/2024)
        tag = self.tag_entry.get()
        print("Se ha almacenado:", tag)

        try:
            if self.status and self.validado == True:
                print(f"Datos a enviar por separado: {self.validar_array}")
                for dato in self.validar_array:
                    data_to_send = f"{dato}\n"
                    try:
                        self.ser.write(data_to_send.encode('utf-8'))
                        print(f"Dato enviado: {data_to_send.strip()}")
                        self.enviar_status = True
                    except Exception as e:
                        print(f"Error al enviar el dato: {e}")
                        self.enviar_status = False
                # self.end_time = self.get_current_time() + self.plot_duration
                # self.schedule_plot_data()
            else:
                self.texestado.delete(1.0, tkinter.END)
                send = "Puerto cerrado, no se puede enviar"
                self.texestado.insert("0.0", str(send))
                # parte de pruebas
                self.plot_area.clear()
                #self.plot_area.plot(data_example)
                self.canvas.draw()
#////////////////// esta sub rutina se debe hacer en otro hilo ////////////////
            #self.while_recibir() # realiza la lectura
        except KeyboardInterrupt:
            print("Programa interrumpido por el usuario.")
            self.enviar_status = False
        finally:
                print("en plot")
                #self.plot_area.clear()
                #self.plot_area.plot(datos_reb)
                #self.canvas.draw()
                self.romper_event()


    def ver_Resultados(self): #(revisado con problemas 10/04/2024)
        # Supongamos que tienes data_example para el voltaje
        self.v_data = self.data_example
        self.rref_val= 550.8
        self.current_data = [v / self.rref_val for v in self.v_data]
        self.impedancia_data = [self.rref_val * (3.3 / (3.3 - v)) for v in self.v_data]

        print("Voltajes:", self.v_data)
        print("Corriente:", self.current_data)
        print("Impedancia:", self.impedancia_data)

        data1= self.current_data
        data2= self.data_example
        data3= self.impedancia_data
        # Crear una única figura con tres subgráficas
        self.plot_area.clear()
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        fig.subplots_adjust(hspace=0.2)  # Ajuste del espacio entre subgráficas
        gs = gridspec.GridSpec(4, 1, figure=fig)

        ax1 = fig.add_subplot(gs[1])
        ax2 = fig.add_subplot(gs[2])
        ax3 = fig.add_subplot(gs[3])
        ax1.plot(self.current_data, label='Corriente', color='red', linewidth=0.65, markersize=8)
        ax1.set_title('Corriente')
        ax2.plot(self.v_data, label='Voltaje', color='blue', linewidth=0.75, markersize=10)
        ax2.set_title('Voltaje')
        ax3.plot(self.impedancia_data, label='Impedancia', color='black', linewidth=0.85, markersize=12)
        ax3.set_title('Impedancia')
        fig.tight_layout()
        self.canvas.figure = fig
        self.canvas.draw()

        fig = plt.figure(figsize=(12, 5))

        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(data1, label='Datos 1', color='red',linewidth=0.65, markersize=8)
        ax1.set_title('Corriente')

        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(data2, label='Datos 2', color='blue',linewidth=0.75, markersize=10)
        ax2.set_title('Voltaje')

        ax3 = plt.subplot(2, 1, 2)
        ax3.plot(data3, label='Datos 3', color='black',linewidth=0.85, markersize=12)
        ax3.set_title('Impedancia')


        plt.tight_layout()
        plt.show()

    def menu(self, puerto= str):
        print(puerto)
        global com
        com = puerto

    def enviar_prueba(self): #revisado 31/05/2024
        
        # Parte 1

        self.plot_area.clear()
        self.muestras = (((self.rango_max - self.rango_minimo) / self.pas_val) + 1)
        print("Cantidad muestras:", self.muestras)
        tag = self.tag_entry.get()
        print("Se ha almacenado:", tag)
        try:
            if self.status and self.validado:
                #self.validar_array= self.validar_array[0],self.validar_array[1],self.validar_array[2]
                print(self.validar_array)
                print(f"Datos a enviar por separado: {self.validar_array}")
                
                try: 

                    #data_to_send = f"self.validar_array\n"
                    data_to_send = '/'.join(self.validar_array)
                    data = f"{data_to_send}\n"
                    print(f"Dato enviado: {data.encode()}")
                    self.enviar_status = True 
                    #self.ser.write(self.validar_array.encode('utf-8'))
                    self.ser.write(data.encode())
                    #self.ser.write(data_to_send)
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
                    
                    # Parte 3  
                    self.resultado_datos = self.separar_array()

                    self.formulas()


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
            else:
                self.texestado.delete(1.0, tkinter.END)
                send = "Puerto cerrado, no se puede enviar"
                self.texestado.insert("0.0", str(send))
        except KeyboardInterrupt:
            print("Programa interrumpido por el usuario.")
            self.enviar_status = False
        return
    
    def separar_array(self):  
        sub_array = []
        resultados = []
        for elemento in self.datos_resp:
            if elemento.startswith('F:'):
                if sub_array:
                    resultados.append(sub_array)
                    sub_array = []
            sub_array.append(elemento)
        resultados.append(sub_array)
        print(resultados)
        return resultados
    
    def z_option(self, values= str): # problema de callback
        print(values)

        if values == "Z/PH":
            self.z_ph_graph()
            print("Z/PH")
        if values == "Xc/Rc":
           self.Xc_Rc()
           print("Xc/Rc")
        if values == "I/V":
            self.I_V()
            print("I/V")
        if values == "Xc VS Rc":
            self.Xc_VS_Rc()
            print("Xc VS Rc")

#//////////////// funcion es para graficar las distintas graficas seleccionadas ///////////////////////////////

    def z_ph_graph(self):
        pass

    def Xc_Rc(self):
        pass

    def I_V(self):
        pass

    def Xc_VS_Rc(self):
        pass

    def df_event(self,rgr,rref_val,Vrref):

        df_value= self.d_f.get()

        if df_value == 1:
            rgr="9900.0"
            rref_val="550.8"
            Vrgr= float(self.rgr)
            Vrref= float(self.rref)
            self.rgr_entry.configure(placeholder_text= rgr)
            self.rgr_entry.configure(state = "disabled")
            
            self.rref_entry.configure(placeholder_text= rref_val)
            self.rref_entry.configure(state = "disabled")
            
        else :
            Vrgr= 0
            Vrref= 0
            self.rgr_entry.configure(placeholder_text= "Float",state= "normal")
            self.rref_entry.configure(placeholder_text="Float",state= "normal")

    def exportar_and_name_archivo(self):

        global export
        global data
        global df
        global tag_name
        data=[1]
        colum1="datos"
        tag_name=self.tag_entry.get()

        export=[[tag_name],[data]]
        data_config_array=[ciclos_val,muestreo_val,barrido_val]

        self.texestado.insert("0.0"," ciclos: " + data_config_array[0] + " muestreo " + data_config_array[1] + "barrido: " + data_config_array[2])

        print(data_config_array)
        print(export)

        data_to_export={'File name':[tag_name],colum1:data,'Ciclos':[ciclos_val],'muestreo':[muestreo_val],'barrido':[barrido_val]}
        df=exp.DataFrame(data_to_export)
        print(df)
    
    def exportar_event(self):
        df.to_excel('datos_ejemplo//ejemplo.xlsx',sheet_name=tag_name, index=False)

    def sidebar_button_event(self):
        global ciclos
        global muestreo
        global barrido
        global tag_name
        global data

        ser = sr.Serial(''.join(puerto_seleccionado), 115200)
        print(sr.Serial())
        self.texestado.insert("0.0", sr.Serial.port)
        plt.close()
        plt.figure()
        plt.ion()
        plt.show()

        data = np.array([])
        global i
        i = 0

        try:
            while True:
                nuevo_ciclos = int(ciclos[0])
                nuevo_muestreo = int(muestreo[0])
                nuevo_barrido = int(barrido[0])
                nuevo_tag_name = int(tag_name[0])
                ciclos.append(nuevo_ciclos)
                muestreo.append(nuevo_muestreo)
                barrido.append(nuevo_barrido)
                tag_name.append(nuevo_tag_name)

                line = ser.readline()
                line.decode()
                b = float(line[0:4])
                data = np.append(data, b)
                plt.cla()
                plt.plot(data)
                plt.pause(0.01)     
                i = i + 1

        except KeyboardInterrupt:  
            pass
        finally:
            ser.close()

if __name__ == "__main__":

    port = actualizar_puerto()
    app_instance = app()
    app_instance.mainloop()