
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal,QEventLoop, QTimer
from threading import Thread
import threading
from queue import Queue
from time import sleep
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
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
        self.filename = self.filenameadd()
        self.updateConnStatus(False)
        self.ble.setUpdateHandler(self.updateConnStatus)
        self.refreschbotton.clicked.connect(self.refresh)
        self.guardar_usuario.clicked.connect(self.usuario)
        self.descargar_btn.clicked.connect(self.descargar)
        self.conectar_botton.clicked.connect(self.connect)
        self.desconectarbotton.clicked.connect(self.disconnect)
        self.enviar_botton.clicked.connect(self.enviar)
        self.show()


    def usuario(self) -> None:
        nombre      =   self.nombre_edit_line.text()
        apellido    =   self.apellido_input.text()
        numero      =   self.numero_input.text()
        altura      =   self.altura_input.text()
        peso        =   self.peso_input.text()
        edad        =   self.edad_input.text()
        Documento   =   self.documento_combo.currentText()
        print(nombre,apellido,Documento,numero,altura,peso,edad)
        self.filenameadd()

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
        
    def controlThread(self) -> None:
        while True:
            if not self.ble.isConnected():
                break
            if self.BLEOut is not None and self.BLEOut != self.BLEOut_old:
                self.ble.pushQueue(self.BLEOut)
                self.BLEOut_old = self.BLEOut
            sleep(0.01)                        

        
    def createThread(self, **kwargs) -> None:
        keys = list(kwargs.keys())
        
        if "target_func" in keys and "args" in keys:
            Thread(target = kwargs["target_func"], args = (kwargs["args"], )).start()
        elif "target_func" in keys:
            Thread(target = kwargs["target_func"], args=()).start()
        else:
            print("Wrong arguments")
        
    def setComboBox(self) -> None:
        self.devicecombobox.clear()
        self.devices = self.ble.getDeviceList()
        for ith, device in enumerate(self.devices):
             if device.name is not None:
                print(f"Device {ith + 1} : {device.name}")
                self.devicecombobox.addItem(device.name)
    def refresh(self) -> None:
        self.refreschbotton.setEnabled(False)
        self.createThread(target_func = self.ble.scanDevices)

        while not self.ble.isScanDone():
            QtWidgets.QApplication.processEvents()
        self.setComboBox()
        self.refreschbotton.setEnabled(True)
    
    def enviar(self) -> None:
        muestra = self.Sample_input_data.text()
        #self.createThread(target_func=self.ble.sample_data, args=(muestra))

        async def connect_async():
            await self.ble.sample_data(muestra)

        def run_async_loop():
            asyncio.run(connect_async())
        # Crear un hilo tradicional para ejecutar el bucle asyncio
        threading.Thread(target=run_async_loop).start()
        
    async def descargar(self) -> None:
        await self.ble.descarga

        pass
        
    def connect(self) -> None:
        target_device_name = self.devicecombobox.currentText()
        for device in self.devices:
            if device.name == target_device_name:
                self.target_device = device
                
        # Crear un hilo asincrónico
        async def connect_async():
            await self.ble.connectToDevice(self.target_device)

        # Llamar a connect_a sync usando asyncio.run() desde el nuevo hilo
        def run_async_loop():
            asyncio.run(connect_async())

        # Crear un hilo tradicional para ejecutar el bucle asyncio
        threading.Thread(target=run_async_loop).start()

        sleep(2)
        self.createThread(target_func=self.controlThread)

        """ self.createThread(target_func = self.ble.connectToDevice, args = self.target_device)
        sleep(2)
        self.createThread(target_func = self.controlThread) """

    def disconnect(self) -> None:
        self.ble.disconnectFromDevice()

    def crear_reporte(self)-> None:


        # Crear una instancia de la clase reporte
        nombre      =   self.nombre_edit_line.text()
        apellido    =   self.apellido_input.text()
        edad        =   self.edad_input.text()
        doc         =   self.documento_combo.currentText()
        numero      =   self.numero_input.text()
        peso        =   self.peso_input.text()
        directory = "imagenes_resultados"
        reportes_direc = "reportes"
        Gyro = os.path.join(directory, "gyro_graph.png")
        Acc = os.path.join(directory, "acc_graph.png")
        Absg = os.path.join(directory, "absolute_g.png")
        angD = os.path.join(directory, "agular_desviacion.png")
        
        # Verificar si la carpeta imágenes existe y crearla si no existe
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.filenameadd()
        report = Reporte(self)

        report.add_title("Informe de Resultados")
        informacion_paciente = f"Este informe esta compuesto por los resultados obtenidos dentro del analisis desarrollado al paciente {nombre} {apellido} con numero de indentificacion {doc} {numero} de edad {edad} y peso {peso} ."
        #report.add_text(informacion_paciente)
        #paragraph = Paragraph(informacion_paciente, justified_style)
        # Agrega el párrafo al contenido de tu informe
        report.add_text(informacion_paciente)
        #report.add_text(paragraph)
        report.add_text("""
        Un giroscopio es un dispositivo utilizado para medir o mantener la orientación angular de un objeto. Los resultados obtenidos de 
        un giroscopio suelen incluir mediciones de velocidad angular, aceleración angular y cambios en la orientación de un objeto en el 
        espacio tridimensional.

        - Velocidad Angular:
        Indica la velocidad a la que un objeto está rotando en torno a un eje específico. Estas mediciones son útiles para determinar 
        la rapidez con la que un objeto está girando y pueden ser cruciales en aplicaciones de navegación y control de movimiento.
        - Aceleración Angular:
        Mide la rapidez con la que cambia la velocidad angular de un objeto en el tiempo. Esta medida es esencial para comprender 
        cómo varía la velocidad de rotación de un objeto y puede ser fundamental en el diseño y control de sistemas dinámicos.
        - Orientación:
        Los giroscopios también proporcionan información sobre la orientación espacial de un objeto. Esto implica conocer 
        la dirección en la que apunta un objeto en un momento dado y cómo esta dirección cambia a lo largo del tiempo. 
        Estos datos son esenciales en aplicaciones de navegación, como en aeronaves, vehículos autónomos y dispositivos 
        de realidad virtual.En resumen, los resultados de un giroscopio proporcionan información crucial sobre la rotación y 
        orientación de un objeto en el espacio, lo que tiene aplicaciones en una amplia gama de campos, desde la navegación hasta 
        la ingeniería de control y la realidad virtual.
        """)
        report.add_graph("Gráfico del giroscopio", Gyro)

        report.add_text("""Un acelerómetro es un dispositivo utilizado para medir la aceleración 
        experimentada por un objeto en movimiento. Los resultados obtenidos de un acelerómetro 
        suelen incluir mediciones de la aceleración lineal en una o más direcciones, así como 
        información sobre la orientación y la vibración del objeto.
        Aceleración Lineal: El principal resultado de un acelerómetro es la medición de la 
        aceleración experimentada por un objeto en una dirección específica. Estas mediciones 
        son útiles para determinar la velocidad de movimiento, la fuerza g, y para detectar 
        cambios en la velocidad o la dirección del movimiento.
        Orientación: Algunos acelerómetros también pueden proporcionar información sobre la 
        orientación del objeto en el espacio. Esto implica conocer la posición relativa 
        del objeto en relación con la gravedad terrestre o con respecto a un sistema de referencia específico.
        Vibración: Los acelerómetros también pueden utilizarse para medir la vibración 
        experimentada por un objeto. Estas mediciones son útiles en una amplia gama de 
        aplicaciones, desde el monitoreo de la salud estructural de edificios e infraestructuras 
        hasta la detección de vibraciones en maquinaria y dispositivos electrónicos. """)  

        report.add_graph("Gráfico Acc(g)", Acc)

        report.add_text(""" La aceleración resultante $g_{\\text{absolute}}$ es la magnitud 
        total de la aceleración experimentada por un objeto en las tres dimensiones 
        del espacio. Esta aceleración se calcula combinando las aceleraciones en los ejes 
        x y z utilizando el teorema de Pitágoras en tres dimensiones. """)

        #formula_absg = r"$g_{\text{absolute}} = \sqrt{g_{\text{accx}}^2 + g_{\text{accy}}^2 + g_{\text{accz}}^2}$"
        formula_image_path = "imagenes\g abs.png"  
        formula_image = Image(formula_image_path, width=200, height=50) 
        #report.add_text(formula_absg)
        report.add_graph("Gráfico Absolute G", Absg)

        report.add_text(""" La desviación angular es una medida que indica el grado de diferencia 
        entre una orientación deseada y la orientación real de un objeto o sistema. La descripción 
        de la desviación angular podría incluir lo siguiente:
        La desviación angular, también conocida como error angular, se refiere al ángulo de desviación 
        entre la posición esperada o deseada y la posición real de un objeto o sistema. Es una medida 
        importante en una variedad de contextos, como la navegación, la ingeniería mecánica y la tecnología de sensores.
        Por ejemplo, en el contexto de la navegación, la desviación angular puede referirse a la diferencia entre la 
        dirección deseada de un vehículo y su dirección real. En aplicaciones de ingeniería mecánica, la desviación 
        angular puede indicar el grado de desalineación entre dos componentes o ejes que se supone que deben estar 
        perfectamente alineados.La desviación angular se expresa típicamente en grados, radianes u otras unidades angulares, 
        dependiendo del contexto específico. Es importante minimizar la desviación angular para garantizar la precisión y la 
        eficiencia de los sistemas y procesos. """)

        formula_desv_ang_x = r"$\text{girosc\_ang\_x} = \left( \frac{\text{ggyrx}}{131} \right) \cdot \frac{\text{dt}}{1000.0} + \text{girosc\_ang\_x\_prev}$"
        formula_desv_ang_y = r"$\text{girosc\_ang\_y} = \left( \frac{\text{ggyry}}{131} \right) \cdot \frac{\text{dt}}{1000.0} + \text{girosc\_ang\_y\_prev}$"
        report.add_text(formula_desv_ang_x)
        report.add_text(formula_desv_ang_y)
        report.add_graph("Gráfico Angular desviación en grados", angD)
        report.add_text("Estos son los resultados ")
        data = [
                ["Nombre", "Edad", "Género"],
                ["Juan", 25, "Masculino"],
                ["María", 30, "Femenino"],
                ["Luis", 28, "Masculino"]
                ]

                # Crea la tabla
        table = Table(data)

        # Estilo de la tabla
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        # Aplica el estilo a la tabla
        table.setStyle(style)

        # Define el contenido del documento
        content = [table]

        ruta_guardado = os.path.join(reportes_direc, f"{self.filename}")
        # Generar el PDF
        try:
            report.create_pdf(ruta_guardado)
        except Exception as e:
            print("Error al crear el PDF:", e)

    def filenameadd(self):
        
        nombre      =   self.nombre_edit_line.text()
        apellido    =   self.apellido_input.text()
        edad        =   self.edad_input.text()
        doc         =   self.documento_combo.currentText()
        numero      =   self.numero_input.text()
        doc_mapping = {
            "C.C": "C_C",
            "C.E": "C_E",
            "T.I": "T_I",
            "P.P": "P_P",
            # Añade más mapeos según sea necesario
        }
        if doc in doc_mapping:
            doc = doc_mapping[doc]
            
        self.filename = f"{nombre}_{apellido}_{edad}_{doc}_{numero}.pdf"
        print(self.filename)
        
        

class canvas_grafica(FigureCanvas):

    def __init__(self, parent=None, ui=None):
        self.ui = ui
        self.acc_canvas = None
        self.fig, self.ax = plt.subplots(dpi=100, figsize=(5, 5), sharey=True, facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)

    def absolute_g(self):

        try:
            datos_procesados = []
            with open('LoggedData_CalInertialAndMag.csv', 'r') as archivo:
                for i, fila in enumerate(archivo, start=1):
                    if i % 2 != 0:
                        datos = self.procesar_fila(fila)
                        if datos is not None:
                            datos_procesados.append(datos)
                        else:
                            print(f"Error en la fila {i}: formato incorrecto")
        
            x = np.array([float(dato[0]) for dato in datos_procesados]) 

            # el sensor entrega los datos en mg se necesitan en G. 
            gaccx = np.array([float(dato[4]) for dato in datos_procesados]) /   1000 
            gaccy = np.array([float(dato[5]) for dato in datos_procesados]) /   1000 
            gaccz = np.array([float(dato[6]) for dato in datos_procesados]) /   1000  

            #calculamos la acceleración absoluta:
            g_absolute = np.sqrt(np.power(gaccx, 2) + np.power(gaccy, 2) + np.power(gaccz, 2))

            self.ax.clear()
            self.ax.plot(x, g_absolute, label='G abs', linewidth=0.8, color= 'g')
            # Establecer los límites del eje x
            self.ax.set_xlim(x.min(), x.max())
            # Calcular los valores máximos y mínimos 
            ymin = g_absolute.min()
            ymax = g_absolute.max()


            self.ax.set_ylim(ymin, ymax)
            self.ax.legend()
            self.fig.suptitle('Gráfica Acceleracion Abosulta', size=9)

            # Actualizar el lienzo del gráfico
            self.draw()
            directory = "imagenes_resultados"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename    =   os.path.join(directory, "absolute_g.png")
            #filename   =   "acc_graph.png"
            self.print_png(filename)

            # Actualizar el widget de la interfaz con el nuevo lienzo del gráfico
            self.ui.grafica_acceleracion_g.addWidget( self)
            self.ui.grafica_acceleracion_g.update()

        except FileNotFoundError:
            print(f"El archivo LoggedData_CalInertialAndMag no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")

    def acc_graph(self):

        try:
            datos_procesados = []
            with open('LoggedData_CalInertialAndMag.csv', 'r') as archivo:
                for i, fila in enumerate(archivo, start=1):
            # Procesar solo las filas con índices impares
                    if i % 2 != 0:
                        datos = self.procesar_fila(fila)
                        if datos is not None:
                            datos_procesados.append(datos)
                        else:
                            print(f"Error en la fila {i}: formato incorrecto")
        
            x = np.array([float(dato[0]) for dato in datos_procesados])  # Extraer datos de la lista
            gaccx = np.array([float(dato[4]) for dato in datos_procesados]) /   1000 # Extraer datos de la lista
            gaccy = np.array([float(dato[5]) for dato in datos_procesados]) /   1000 # Extraer datos de la lista
            gaccz = np.array([float(dato[6]) for dato in datos_procesados]) /   1000  # Extraer datos de la lista

            
            # Limpiar la gráfica existente antes de agregar los nuevos datos
            
            self.ax.clear()
            self.ax.plot(x, gaccx, label='accx', linewidth=0.8, color= 'r')
            self.ax.plot(x, gaccy, label='accy', linewidth=0.8, color= 'b')
            self.ax.plot(x, gaccz, label='accz', linewidth=0.8, color= 'g')
            self.ax.set_ylabel('g')
            # Establecer los límites del eje x
            self.ax.set_xlim(x.min(), x.max())

            # Calcular los valores máximos y mínimos de los datos de accx, accy y accz
            ymin = min(gaccx.min(), gaccy.min(), gaccz.min())
            ymax = max(gaccx.max(), gaccy.max(), gaccz.max())

            # Establecer los límites del eje y
            self.ax.set_ylim(ymin, ymax)

            self.ax.legend()
            self.fig.suptitle('Gráfica Acceleracion', size=9)

            # Actualizar el lienzo del gráfico
            self.draw()
            directory = "imagenes_resultados"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename    =   os.path.join(directory, "acc_graph.png")
            #filename   =   "acc_graph.png"
            self.print_png(filename)

            # Actualizar el widget de la interfaz con el nuevo lienzo del gráfico
            self.ui.grafica_acceleracion_g.addWidget( self)
            self.ui.grafica_acceleracion_g.update()

        except FileNotFoundError:
            print(f"El archivo LoggedData_CalInertialAndMag no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")

    def gyro_graph(self):
        
        try:
            datos_procesados = []
            with open('LoggedData_CalInertialAndMag.csv', 'r') as archivo:
                for i, fila in enumerate(archivo, start=1):
            # Procesar solo las filas con índices impares
                    if i % 2 != 0:
                        datos = self.procesar_fila(fila)
                        if datos is not None:
                            datos_procesados.append(datos)
                        else:
                            print(f"Error en la fila {i}: formato incorrecto")
        
            x = np.array([float(dato[0]) for dato in datos_procesados])  # Extraer datos de la lista
            ggyrx = np.array([float(dato[1]) for dato in datos_procesados])  # Extraer datos de la lista
            ggyry = np.array([float(dato[2]) for dato in datos_procesados])  # Extraer datos de la lista
            ggyrz = np.array([float(dato[3]) for dato in datos_procesados])  # Extraer datos de la lista

            
            # Limpiar la gráfica existente antes de agregar los nuevos datos
            self.ax.clear()
            self.ax.plot(x, ggyrx, label='GYRx', linewidth=.8)
            self.ax.plot(x, ggyry, label='GYRy', linewidth=.8)
            self.ax.plot(x, ggyrz, label='GYRz', linewidth=.8)
            self.ax.set_xlabel('Sample')
            self.ax.set_ylabel('Dps')
            # Establecer los límites del eje x
            self.ax.set_xlim(x.min(), x.max())

            # Calcular los valores máximos y mínimos de los datos de accx, accy y accz
            ymin = min(ggyrx.min(), ggyry.min(), ggyrz.min())
            ymax = max(ggyrx.max(), ggyry.max(), ggyrz.max())

            # Establecer los límites del eje y
            self.ax.set_ylim(ymin, ymax)

            self.ax.legend()
            self.fig.suptitle('Gráfica Giroscopio', size=9)

            # Actualizar el lienzo del gráfico
            self.draw()
            directory = "imagenes_resultados"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename    =   os.path.join(directory, "gyro_graph.png")
            #filename   =   "acc_graph.png"
            self.print_png(filename)
            # Actualizar el widget de la interfaz con el nuevo lienzo del gráfico
            self.ui.grafica_acceleracion_g.addWidget(self)
            self.ui.grafica_acceleracion_g.update()

        except FileNotFoundError:
            print(f"El archivo LoggedData_CalInertialAndMag no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")

    def angular_desviacion(self):
        try:
            datos_procesados = []
            with open('LoggedData_CalInertialAndMag.csv', 'r') as archivo:
                for i, fila in enumerate(archivo, start=1):
            # Procesar solo las filas con índices impares
                    if i % 2 != 0:
                        datos = self.procesar_fila(fila)
                        if datos is not None:
                            datos_procesados.append(datos)
                        else:
                            print(f"Error en la fila {i}: formato incorrecto")
            girosc_ang_x_prev   =   0
            girosc_ang_y_prev   =   0

            x       = np.array([float(dato[0]) for dato in datos_procesados])  
            ggyrx   = np.array([float(dato[1]) for dato in datos_procesados])   
            ggyry   = np.array([float(dato[2]) for dato in datos_procesados])  
            
            sample_rate = 10  # Hz
            dt = 1 / sample_rate  

            # Aplicando la fórmula de integración
            girosc_ang_x = (ggyrx / 131) * dt / 1000.0 + girosc_ang_x_prev
            girosc_ang_y = (ggyry / 131) * dt / 1000.0 + girosc_ang_y_prev
            #girosc_ang_x = (ggyrx / 131) * dt   + girosc_ang_x_prev
            #girosc_ang_y = (ggyry / 131) * dt   + girosc_ang_y_prev

            girosc_ang_x_prev = girosc_ang_x
            girosc_ang_y_prev = girosc_ang_y

            # Limpiar la gráfica existente antes de agregar los nuevos datos
            self.ax.clear()
            self.ax.plot(x, girosc_ang_x, label='Angulo X', linewidth= .8)
            self.ax.plot(x, girosc_ang_y, label='Angulo Y', linewidth= .8)
            self.ax.set_xlabel('Sample')
            self.ax.set_ylabel('Desviacion Angular')
            
            # Establecer los límites del eje x
            self.ax.set_xlim(x.min(), x.max())

            # Calcular los valores máximos y mínimos de los datos de accx, accy y accz
            ymin = min(girosc_ang_x.min(), girosc_ang_y.min())
            ymax = max(girosc_ang_x.max(), girosc_ang_y.max())

            # Establecer los límites del eje y
            self.ax.set_ylim(ymin, ymax)
            self.ax.legend()
            self.fig.suptitle('Angular Desviación', size=9)

            # Actualizar el lienzo del gráfico
            self.draw()
            directory = "imagenes_resultados"
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename    =   os.path.join(directory, "agular_desviacion.png")
            self.print_png(filename)

        except FileNotFoundError:
            print(f"El archivo LoggedData_CalInertialAndMag no fue encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al leer el archivo: {e}")

    def procesar_fila(self,fila):
    
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
            return None  

class Reporte():
    def __init__(self, ui):
        self.story = []
        self.ui = ui
        self.filename = self.ui.filenameadd()
    def create_pdf(self,ruta_guardado):
        
            doc = SimpleDocTemplate(ruta_guardado, pagesize=letter)
            doc.build(self.story)


    def add_title(self, title):
        styles = getSampleStyleSheet()
        title_style = styles["Title"]
        title_para = Paragraph(title, title_style)
        self.story.append(title_para)
        self.story.append(Spacer(1, 12))

    def add_graph(self, graph_title, graph_file):

        styles = getSampleStyleSheet()
        heading_style = styles["Heading1"]
        heading_style.alignment = TA_CENTER
        heading_para = Paragraph(graph_title, heading_style)
        self.story.append(heading_para)
        self.story.append(Spacer(1, 12))

        # Agregar la imagen del gráfico al informe
        self.story.append(Image(graph_file, width=500, height=300))
        self.story.append(Spacer(1, 12))

    def add_text(self, text):
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_para = Paragraph(text, normal_style)
        self.story.append(normal_para)
        self.story.append(Spacer(1, 12))