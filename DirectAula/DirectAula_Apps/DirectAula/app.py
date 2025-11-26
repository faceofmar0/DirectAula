#app.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QStyleFactory, QDialog, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
# Importaciones Modulares:
from Presentacion.ventana_grupos import VentanaGrupos 
from Presentacion.ventana_calificaciones_menu import VentanaCalificacionesMenu
from Presentacion.ventana_alumnos import VentanaAlumnos 
from Presentacion.ventana_asistencia import VentanaAsistencia
from Presentacion.seleccion_grupo import SeleccionGrupo
from Logica.gestor_exportacion import GestorExportaciones
from Presentacion.seleccion_grupo import SeleccionGrupo

# 1. IMPORTAR LA VENTANA DE LOGIN
from Presentacion.ventana_login import VentanaLogin 

class VentanaMenuPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DirectAula - Sistema de Gestión")
        self.resize(450, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        lbl_titulo = QLabel("DirectAula - Menú Principal")
        lbl_titulo.setObjectName("titulo_principal")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # 1. Botón CU1: Administrar Grupos (NUEVO)
        btn_grupos = QPushButton("Administrar Grupos")
        btn_grupos.clicked.connect(self.abrir_ventana_grupos)
        btn_grupos.setObjectName("btn_exportar") # Color azul
        layout.addWidget(btn_grupos)

        # 2. Botón CU2: Administrar Alumnos
        btn_alumnos = QPushButton("Administrar Alumnos")
        btn_alumnos.clicked.connect(self.abrir_ventana_alumnos)
        btn_alumnos.setObjectName("btn_exportar") 
        layout.addWidget(btn_alumnos)

        # 3. Botón CU4: Registrar Asistencia
        btn_asistencia = QPushButton("Registrar Asistencia")
        btn_asistencia.clicked.connect(self.abrir_ventana_asistencia)
        btn_asistencia.setObjectName("btn_exportar") 
        layout.addWidget(btn_asistencia)

        # 4. Botón CU3/CU5: Calificaciones
        btn_calificaciones = QPushButton("Registar Calificaciones")
        btn_calificaciones.clicked.connect(self.abrir_ventana_calificaciones)
        btn_calificaciones.setObjectName("btn_exportar") 
        layout.addWidget(btn_calificaciones)

        #5. Botón exportar
        btn_exportar = QPushButton("Exportar Datos")
        btn_exportar.setObjectName("btn_exportar")
        btn_exportar.clicked.connect(self.exportar_datos_excel)
        layout.addWidget(btn_exportar)

    def abrir_ventana_grupos(self):
        """Lanza la ventana del Caso de Uso 1."""
        self.ventana_grupos = VentanaGrupos() 
        self.ventana_grupos.show()
    

    def abrir_ventana_alumnos(self):
        """Lanza el diálogo de selección y luego la ventana de Alumnos (CU2)."""
        dialogo = SeleccionGrupo("Administrar Alumnos", self)
        if dialogo.exec_() == QDialog.Accepted:
            grupo_id = dialogo.get_grupo_id()
            nombre_grupo = dialogo.combo_grupos.currentText()
            self.ventana_alumnos = VentanaAlumnos(grupo_id=grupo_id, nombre_grupo=nombre_grupo) 
            self.ventana_alumnos.show()
        
    def abrir_ventana_asistencia(self):
        """Lanza el diálogo de selección y luego la ventana de Asistencia (CU4)."""
        dialogo = SeleccionGrupo("Registrar Asistencia", self)
        if dialogo.exec_() == QDialog.Accepted:
            grupo_id = dialogo.get_grupo_id()
            nombre_grupo = dialogo.combo_grupos.currentText()
            self.ventana_asistencia = VentanaAsistencia(grupo_id=grupo_id, nombre_grupo=nombre_grupo) 
            self.ventana_asistencia.show()
    
    def abrir_ventana_calificaciones(self):
        """Lanza el diálogo de selección y luego la ventana del menú de Calificaciones."""
        dialogo = SeleccionGrupo("Gestión de Calificaciones", self)
        if dialogo.exec_() == QDialog.Accepted:
            grupo_id = dialogo.get_grupo_id()
            nombre_grupo = dialogo.combo_grupos.currentText()
            self.ventana_calificaciones = VentanaCalificacionesMenu(grupo_id=grupo_id, nombre_grupo=nombre_grupo)
            self.ventana_calificaciones.show()
    
    def exportar_datos_excel(self):
        """Exporta datos de un grupo completo a Excel."""
        dialogo = SeleccionGrupo("Exportar Datos a Excel", self)
        if dialogo.exec_() == QDialog.Accepted:
            grupo_id = dialogo.get_grupo_id()
            nombre_grupo = dialogo.combo_grupos.currentText()
            
            directorio = QFileDialog.getExistingDirectory(
                self, 
                "Seleccionar carpeta para guardar el archivo Excel",
                "",
                QFileDialog.ShowDirsOnly
            )
            
            if not directorio:
                return
            
            QMessageBox.information(self, "Exportando", 
                                   "Exportando todos los datos a Excel. Esto puede tomar unos segundos...")
            
            gestor_export = GestorExportaciones()
            exito, mensaje, ruta_archivo = gestor_export.exportar_grupo_completo(
                grupo_id, 
                nombre_grupo,
                directorio
            )
            
            if exito:
                QMessageBox.information(self, "Exportación Exitosa", 
                                      f"{mensaje}\n\nArchivo guardado en:\n{ruta_archivo}")
            else:
                QMessageBox.critical(self, "Error en Exportación", mensaje)

if __name__ == '__main__':
    QApplication.setStyle(QStyleFactory.create('Fusion')) 
    app = QApplication(sys.argv)
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_css = os.path.join(directorio_actual, 'style.css')
    
    try:
        with open(ruta_css, 'r') as f: 
            app.setStyleSheet(f.read())
        print(f"Éxito: style.css cargado desde: {ruta_css}")
    except FileNotFoundError:
        print(f"Advertencia: El archivo style.css no fue encontrado en la ruta: {ruta_css}")
        
    ventana_login = VentanaLogin()
    ventana_login.show()
    # ventana_principal = VentanaMenuPrincipal()
    # ventana_principal.show()
    sys.exit(app.exec_())