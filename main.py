#  Diego Alejandro Ospina Ceron 
#   Programa principal para interfaz EIS
#   utilizando python
from eis import Ui
import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":    
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
