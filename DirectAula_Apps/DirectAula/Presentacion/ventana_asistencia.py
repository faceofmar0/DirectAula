
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QPushButton, QMessageBox, QTableWidgetItem, QHeaderView, QDateEdit, 
    QComboBox, QLabel, QGroupBox, QGridLayout 
)
from PyQt5.QtCore import QDate, Qt
# 💡 IMPORTACIÓN CORREGIDA: Asumiendo que GestorAsistencia está en logica/bll.py
from Logica.gestor_alumnos import GestorAsistencia 
from datetime import date

class VentanaAsistencia(QWidget):
    """Ventana para el Caso de Uso 4: Registrar Asistencia."""

    def __init__(self, grupo_id, nombre_grupo): 
        super().__init__()
        self._grupo_id = grupo_id # Usar el ID real
        self._nombre_grupo = nombre_grupo # Guardar el nombre
        self.setWindowTitle(f"DirectAula - Asistencia {nombre_grupo}")
        self.resize(800, 600)
        
        # El gestor ahora solo necesita el grupo_id al ser instanciado
        self.gestor = GestorAsistencia(self._grupo_id) 
        self._inicializar_ui(nombre_grupo)

    def _inicializar_ui(self, nombre_grupo):
        main_layout = QVBoxLayout()
        
        lbl_titulo = QLabel(f"Registro de Asistencia: {nombre_grupo}")
        lbl_titulo.setObjectName("titulo_principal")
        main_layout.addWidget(lbl_titulo)
        
        # ----------------------------------------------------
        # SECCIÓN: CONTROL DE FECHA Y REGISTRO MASIVO
        # ----------------------------------------------------
        control_fecha_box = QGroupBox("Control de Asistencia")
        control_layout = QGridLayout(control_fecha_box)

        # 1. Selector de Fecha (QDateEdit)
        lbl_fecha = QLabel("Seleccionar Fecha:")
        self.fecha_asistencia = QDateEdit()
        self.fecha_asistencia.setCalendarPopup(True) # Muestra el calendario al hacer clic
        self.fecha_asistencia.setDate(QDate.currentDate()) # Fecha de hoy por defecto
        # 💡 Conexión: Cuando la fecha cambia, recargar los datos
        self.fecha_asistencia.dateChanged.connect(self._cargar_datos) 
        
        control_layout.addWidget(lbl_fecha, 0, 0)
        control_layout.addWidget(self.fecha_asistencia, 0, 1)

        # 2. Botón de Registro Masivo
        self.btn_masivo = QPushButton("Poner Asistencia a todos")
        self.btn_masivo.setObjectName("btn_agregar")
        self.btn_masivo.clicked.connect(self._registrar_asistencia_masiva)
        
        control_layout.addWidget(self.btn_masivo, 1, 0, 1, 2) # Ocupa 2 columnas
        main_layout.addWidget(control_fecha_box)
        
        # ----------------------------------------------------
        # TABLA DE ASISTENCIA
        # ----------------------------------------------------
        self.tabla_asistencia = QTableWidget()
        self.tabla_asistencia.setColumnCount(3)
        self.tabla_asistencia.setHorizontalHeaderLabels(["Matrícula", "Nombre Completo", "Estado"])
        self.tabla_asistencia.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.tabla_asistencia)

        self.setLayout(main_layout)
        self._cargar_datos() # Carga los datos al iniciar con la fecha de hoy
        
    def _cargar_datos(self):
        """Muestra los datos de asistencia del grupo para la fecha seleccionada."""
        # 1. Obtener la fecha seleccionada
        fecha = self.fecha_asistencia.date().toString("yyyy-MM-dd") 
        
        # 2. Obtener los datos del gestor
        # Retorna: [(matricula, nombre, estado), ...]
        datos = self.gestor.obtener_asistencia_para_ui(fecha)
        
        # 3. Configurar la tabla
        self.tabla_asistencia.setRowCount(len(datos))
        
        # 4. Iterar y llenar la tabla (AQUÍ ESTÁ LA LÓGICA DE RELLENADO)
        for fila_indice, alumno_data in enumerate(datos):
            
            # Columna 0: Matrícula (Solo Lectura)
            item_matricula = QTableWidgetItem(alumno_data[0])
            item_matricula.setFlags(item_matricula.flags() & ~Qt.ItemIsEditable) # Desactivar edición
            self.tabla_asistencia.setItem(fila_indice, 0, item_matricula)
            
            # Columna 1: Nombre Completo (Solo Lectura)
            item_nombre = QTableWidgetItem(alumno_data[1])
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable) # Desactivar edición
            self.tabla_asistencia.setItem(fila_indice, 1, item_nombre)
            
            # Columna 2: Estado (QComboBox para interactividad)
            estado_combo = QComboBox()
            estados = ["Presente", "Ausente", "Retardo", "Justificado"]
            estado_combo.addItems(estados)
            
            # Seleccionar el estado actual (devuelto por el DAO: 'Presente', 'Ausente', etc.)
            estado_combo.setCurrentText(alumno_data[2])
            
            # Conexión crucial: Llama a la función de guardado individual al cambiar el estado
            # Usamos una lambda para capturar los valores específicos de esta fila (matrícula y fecha)
            estado_combo.currentIndexChanged.connect(
                lambda index, m=alumno_data[0], d=fecha, combo=estado_combo: 
                    self._actualizar_asistencia_individual(m, d, combo.currentText())
            )
            
            self.tabla_asistencia.setCellWidget(fila_indice, 2, estado_combo)


    def _registrar_asistencia_masiva(self):
        """Llama al BLL para marcar a todos como Presente y recarga la tabla."""
        fecha = self.fecha_asistencia.date().toString("yyyy-MM-dd")
        
        confirmacion = QMessageBox.question(self, "Confirmar Registro",
            f"¿Desea marcar a TODOS los alumnos como 'Asistencia' para la fecha {fecha}?",
            QMessageBox.Yes | QMessageBox.No)

        if confirmacion == QMessageBox.Yes:
            resultado_mensaje = self.gestor.registrar_asistencia_masiva(fecha)
            
            if "Error" in resultado_mensaje:
                QMessageBox.critical(self, "Error", resultado_mensaje)
            else:
                QMessageBox.information(self, "Operación Exitosa", resultado_mensaje)
                self._cargar_datos() # ¡Recargar para ver los cambios reflejados!

    def _actualizar_asistencia_individual(self, matricula, fecha, nuevo_estado):
        """Guarda el estado de un alumno individualmente (Activado por el ComboBox)."""
        resultado_mensaje = self.gestor.actualizar_estado_asistencia(matricula, fecha, nuevo_estado)
        
        if "Error" in resultado_mensaje:
            QMessageBox.critical(self, "Error de Guardado", resultado_mensaje)
        # No se necesita recargar, el ComboBox ya muestra el cambio.