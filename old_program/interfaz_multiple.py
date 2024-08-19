#   Diego Alejandro Ospina Ceron 
#   Programa de base para la interfaz de la plataforma IEESC 
#   utilizando python
import serial.tools.list_ports as p
import pandas as exp
import serial as sr
from tkinter import *
import tkinter
from tkinter import filedialog 
import PIL 
from PIL import Image
import os
import customtkinter as ctk
from customtkinter import CTkFrame, CTkLabel, CTkTabview, CTkImage
import serial , time
import tkinter.messagebox
import numpy as np
import matplotlib.pyplot as plt

#dispositivo_conectado = serial.Serial('COM3',115200)
#time.sleep(2)
#dispositivo_conectado.close()

ctk.set_appearance_mode("ligh") # set del color de fondo
ctk.set_default_color_theme("dark-blue") # color de iconos
def actualizar_puerto():
    ports=p.comports()
    global port
    port=[]
    for i in ports:
        port.append(i.device)
    print(port)
    return port

class app(tkinter.Tk):

    def __init__(self):
        super().__init__()

        self.title("Programa atenuador")
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
        self.tabview.tab("conexion").grid_columnconfigure(0, weight=1) # configure grid of individual tabs
        self.tabview.tab("conexion").grid_rowconfigure(0, weight=1) # configure grid of individual tabs
        self.tabview.add("ajuste")
        self.tabview.tab("ajuste").grid_columnconfigure(0, weight=1)
        self.tabview.tab("ajuste").grid_rowconfigure(0, weight=1)

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
        self.lista_puertos=ctk.CTkOptionMenu(self.tabview.tab("conexion"),width= 60, height= 10,values=actualizar_puerto(),command=self.seleccion_puerto)
        self.lista_puertos.grid(row=1, column=2, padx=5, pady=5)
        #boto para conectar
        self.boton_conectar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="conectar", 
                                                        command=self.sidebar_button_event)
        self.boton_conectar.grid(row=1, column=3, padx=5, pady=5)
        self.frecuencia = ctk.CTkEntry(self.tabview.tab("conexion"), width= 60, height= 10, placeholder_text= "Freq") # entrada 1 
        self.frecuencia.grid(row=2, column=0, padx=5, pady=5)  
        self.puertos_label = ctk.CTkLabel(self.tabview.tab("conexion"), text="Hz", font=("roboto",15))
        self.puertos_label.grid(row=2, column=1, padx=5, pady=5)
        self.boton_conectar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="verificar", 
                                                        command=self.freq_verif_event)
        self.boton_conectar.grid(row=2, column=2, padx=5, pady=5)
        self.boton_conectar = ctk.CTkButton(self.tabview.tab("conexion"),anchor="center", compound="left", width= 60, height= 10, text="romper", 
                                                        command=self.romper_event)
        self.boton_conectar.grid(row=2, column=3, padx=5, pady=5)
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
        self.boton_validar = ctk.CTkButton(self.ajuste_frame,anchor="center", compound="left", width= 60, height= 10, text="Validar", command=self.validar)
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
        self.rgr_entry = ctk.CTkEntry(self.ajuste_frame, width= 60, height= 10,placeholder_text= "Float") # entrada 1 
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

        self.boton_tag = ctk.CTkButton(self.ajuste_frame,anchor="center", compound="left", width= 60, height= 10, text="Validar", 
                                                        command=self.exportar_and_name_archivo)
        self.boton_tag.grid(row=5, column=3, padx=5, pady=5,sticky="w")

        #------------------------------------------------ vista space --------------------------------------------
        self.vista_frame = ctk.CTkFrame(self,width=50, height=50, corner_radius=0 )
        self.vista_frame.grid(row=2, rowspan=1, column=1, sticky="sew")
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
                                                        command=self.sidebar_button_event)
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


    def menu(self, puerto= str):
        print(puerto)
        global com
        com = puerto
        

    def z_option(self, values= str): # problema de callback
        print(values)

        if values == "Z/PH":
            print("Z/PH")
        if values == "Xc/Rc":
           print("Xc/Rc")
        if values == "I/V":
            print("I/V")
        if values == "Xc VS Rc":
            print("Xc VS Rc")

    def df_event(self):
        global Vrgr
        global Vrref

        df_value= self.d_f.get()

        if df_value == 1:
            rgr="9900.0"
            rref="550.8"
            Vrgr= float(rgr)
            Vrref= float(rref)
            self.rgr_entry.configure(placeholder_text= rgr)
            self.rgr_entry.configure(state = "disabled")
            
            self.rref_entry.configure(placeholder_text= rref)
            self.rref_entry.configure(state = "disabled")
            
        else :
            Vrgr= 0
            Vrref= 0
            self.rgr_entry.configure(placeholder_text= "Float",state= "normal")
            self.rref_entry.configure(placeholder_text="Float",state= "normal")
            
    def romper_event(self):
        i=100
        print("en rompet")
        ser= sr.Serial(''.join(com), 115200)
        ser.close()
        plt.close('all')
        print("close port and plot")

    def exportar_and_name_archivo(self):

        global export
        global data
        global ciclos
        global muestreo
        global barrido
        global df
        global tag_name
        data=[1]
        colum1="datos"

        ciclos=self.ciclos_entry.get()
        muestreo=self.muestreo_entry.get()
        barrido= self.barrido_entry.get()
        tag_name=self.tag_entry.get()

        export=[[tag_name],[data]]
        data_config_array=[ciclos,muestreo,barrido]

        self.texestado.insert("0.0"," ciclos: " + data_config_array[0] + " muestreo " + data_config_array[1] + "barrido: " + data_config_array[2])

        print(data_config_array)
        print(export)

        data_to_export={'File name':[tag_name],colum1:data,'Ciclos':[ciclos],'muestreo':[muestreo],'barrido':[barrido]}
        df=exp.DataFrame(data_to_export)
        print(df)
    
    def exportar_event(self):
        df.to_excel('datos_ejemplo//ejemplo.xlsx',sheet_name=tag_name, index=False)
    
    def freq_verif_event(self):
        
        frecuencia=self.frecuencia.get()
        print(frecuencia)
        self.texestado.insert("0.0",  frecuencia )


    
    def validar(self):
        
        paso=self.paso_entry.get()
        rango=self.rango_entry.get()
        hz=self.hz_config_entry.get()
        

        rango_freq=[rango,hz] # datos para el tiva o micro
        validar_array=[rango,hz,paso]
        print(validar_array)
        self.texestado.insert("0.0"," rango: " + validar_array[0] + " -- " + validar_array[1] + "paso: " + validar_array[2] )
    
    def update_ports(self, *args):
        ports=p.comports()
        port=[]
        for i in ports:
            port.append(i.device)
        print(port)

    def seleccion_puerto(self,  *args):
        ports=p.comports()
        port=[]
        for i in ports:
             port.append(i.device)
        print(port)
        self.lista_puertos._values=port
        global puerto_seleccionado
        puerto_seleccionado = self.lista_puertos.get()

        print("Se seleccionó el puerto: ", puerto_seleccionado)
    
    def sidebar_button_event(self):
        global ciclos
        global muestreo
        global barrido
        global tag_name
        global data
        
        #print("sidebar_button click")
        ser= sr.Serial(''.join(puerto_seleccionado), 115200)
        #print ("The port %s is available") %ser
        print(sr.Serial())
        self.texestado.insert("0.0",  sr.Serial.port )
        plt.close()
        plt.figure()
        plt.ion()
        plt.show()

        data = np.array([])
        global i
        longitud = len(data)
        i=0 
        while i<100:

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
            b= float (line[0:4])
            data = np.append(data,b)
            plt.cla()
            plt.plot(data)
            plt.pause(0.01)
            i=i+1
            
        ser.close()

if __name__ == "__main__":
    app = app()
    app.mainloop()

