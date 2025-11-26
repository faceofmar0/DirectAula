from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QHBoxLayout, 
    QLabel, QPushButton, QMessageBox, QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt
from Logica.gestor_alumnos import GestorCalificaciones 

class VentanaPonderacion(QWidget):
    """Ventana para el Caso de Uso 3: Administrar Ponderación (Flexible)."""

    def __init__(self, grupo_id, nombre_grupo, parent=None):
        super().__init__(parent)
        self._grupo_id = grupo_id
        self._nombre_grupo = nombre_grupo
        self.gestor = GestorCalificaciones(grupo_id)
        self.setWindowTitle(f"Ponderación - {nombre_grupo}")
        self.resize(600, 500)
        self._inicializar_ui()
        self._cargar_datos()

    def _inicializar_ui(self):
        main_layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel(f"Definir Categorías y Ponderación: {self._nombre_grupo}")
        lbl_titulo.setObjectName("titulo_principal")
        main_layout.addWidget(lbl_titulo)
        
        # Tabla para categorías dinámicas
        self.tabla_ponderacion = QTableWidget()
        self.tabla_ponderacion.setColumnCount(3)
        self.tabla_ponderacion.setHorizontalHeaderLabels([
            "Categoría (Nombre único)", 
            "Peso (%)", 
            "Max Items (Tareas/Participaciones)"
        ])
        # Ajustar ancho de las columnas
        self.tabla_ponderacion.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_ponderacion.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_ponderacion.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # Conexión para actualizar la suma visualmente al cambiar cualquier celda de peso
        self.tabla_ponderacion.cellChanged.connect(self._actualizar_suma) 
        main_layout.addWidget(self.tabla_ponderacion)
        
        # Indicador visual de la suma actual (FE.1)
        self.lbl_suma = QLabel("Suma Actual: 0.0%")
        self.lbl_suma.setObjectName("subtitulo")
        main_layout.addWidget(self.lbl_suma)

        # Botones de acción
        btn_layout = QHBoxLayout()
        
        btn_agregar = QPushButton("Añadir Categoría")
        btn_agregar.clicked.connect(self._agregar_fila)
        btn_layout.addWidget(btn_agregar)
        
        btn_eliminar = QPushButton("Eliminar Categoría Seleccionada")
        btn_eliminar.setObjectName("btn_eliminar")
        btn_eliminar.clicked.connect(self._eliminar_fila)
        btn_layout.addWidget(btn_eliminar)
        
        btn_guardar = QPushButton("Guardar Estructura")
        btn_guardar.setObjectName("btn_agregar")
        btn_guardar.clicked.connect(self._guardar_ponderacion)
        btn_layout.addWidget(btn_guardar)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def _cargar_datos(self):
        """Carga las categorías existentes desde la BLL."""
        categorias = self.gestor.obtener_categorias_evaluacion()
        self.tabla_ponderacion.setRowCount(len(categorias))
        
        self.tabla_ponderacion.blockSignals(True)
        for fila_indice, cat in enumerate(categorias):
            # Col 0: Nombre
            self.tabla_ponderacion.setItem(fila_indice, 0, QTableWidgetItem(cat.get_nombre_categoria()))
            # Col 1: Peso
            self.tabla_ponderacion.setItem(fila_indice, 1, QTableWidgetItem(str(cat.get_peso_porcentual())))
            # Col 2: Max Items
            self.tabla_ponderacion.setItem(fila_indice, 2, QTableWidgetItem(str(cat.get_max_items())))
            
        self.tabla_ponderacion.blockSignals(False)
        self._actualizar_suma()

    def _agregar_fila(self):
        """Añade una fila vacía para una nueva categoría."""
        row_count = self.tabla_ponderacion.rowCount()
        self.tabla_ponderacion.insertRow(row_count)
        self.tabla_ponderacion.setItem(row_count, 1, QTableWidgetItem("0.0"))
        self.tabla_ponderacion.setItem(row_count, 2, QTableWidgetItem("1"))

    def _eliminar_fila(self):
        """Elimina la fila seleccionada."""
        fila_seleccionada = self.tabla_ponderacion.currentRow()
        if fila_seleccionada >= 0:
            self.tabla_ponderacion.removeRow(fila_seleccionada)
            self._actualizar_suma()

    def _actualizar_suma(self):
        """Calcula y muestra la suma total de los pesos."""
        suma = 0.0
        try:
            for i in range(self.tabla_ponderacion.rowCount()):
                item = self.tabla_ponderacion.item(i, 1)
                if item and item.text():
                    suma += float(item.text())
            
            self.lbl_suma.setText(f"Suma Actual: {suma:.1f}%")
            if round(suma) != 100:
                self.lbl_suma.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.lbl_suma.setStyleSheet("color: green; font-weight: bold;")
        except ValueError:
            self.lbl_suma.setText("Suma Actual: Inválida (Valores no numéricos en Peso)")
            self.lbl_suma.setStyleSheet("color: red; font-weight: bold;")

    def _obtener_datos_tabla(self):
        """Extrae los datos de la tabla para enviar a la BLL."""
        datos = []
        for i in range(self.tabla_ponderacion.rowCount()):
            nombre_item = self.tabla_ponderacion.item(i, 0)
            peso_item = self.tabla_ponderacion.item(i, 1)
            max_item = self.tabla_ponderacion.item(i, 2)
            
            if not (nombre_item and peso_item and max_item and nombre_item.text().strip()):
                QMessageBox.critical(self, "Error de Datos", f"La fila {i+1} tiene campos vacíos o la Categoría no tiene nombre.")
                return None
            
            try:
                nombre = nombre_item.text().strip()
                peso = float(peso_item.text())
                max_items = int(max_item.text())
                datos.append((nombre, peso, max_items))
            except ValueError:
                QMessageBox.critical(self, "Error de Datos", f"Asegúrese de que el Peso y Max Items de la fila {i+1} son números válidos.")
                return None
        return datos

    def _guardar_ponderacion(self):
        """Valida y guarda la estructura de ponderación."""
        datos_a_guardar = self._obtener_datos_tabla()
        if datos_a_guardar is None:
            return

        # FE.2: Modificación con promedios ya calculados
        alerta = QMessageBox.question(self, "Recálculo de Promedios (FE.2)",
            "Guardar esta nueva estructura ELIMINARÁ la anterior y forzará el recálculo de todos los promedios. ¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.Cancel
        )
        
        if alerta == QMessageBox.Cancel:
            return
            
        # 6. Guardar en BLL
        resultado = self.gestor.guardar_categorias_evaluacion(datos_a_guardar)
        
        if "Error" in resultado:
            QMessageBox.critical(self, "Error al Guardar", resultado)
        else:
            QMessageBox.information(self, "Éxito", resultado)
            self.close()