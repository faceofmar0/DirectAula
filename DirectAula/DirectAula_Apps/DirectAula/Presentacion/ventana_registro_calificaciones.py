#presentacion/ventana_registro_calificaciones.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QComboBox, 
    QLabel, QPushButton, QMessageBox, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from Logica.gestor_alumnos import GestorCalificaciones 

class VentanaRegistroCalificaciones(QWidget):
    """Ventana para el Caso de Uso 5: Registrar Calificaciones."""

    def __init__(self, grupo_id, nombre_grupo, parent=None):
        super().__init__(parent)
        self._grupo_id = grupo_id
        self._nombre_grupo = nombre_grupo
        # Asegúrate de usar la importación correcta de GestorCalificaciones
        self.gestor = GestorCalificaciones(grupo_id) 
        self.setWindowTitle(f"Registro de Calificaciones - {nombre_grupo}")
        self.resize(800, 600)
        
        # Llama a _obtener_nombres_categorias antes de _inicializar_ui
        self._categorias_activas = self._obtener_nombres_categorias() 
        
        self._inicializar_ui()
    
    def _obtener_nombres_categorias(self):
        """Obtiene dinámicamente los nombres de las categorías definidas en la ponderación."""
        categorias = self.gestor.obtener_categorias_evaluacion()
        nombres = [c.get_nombre_categoria() for c in categorias]
        
        # El gestor de calificaciones debe retornar los objetos *actualizados* # con la ponderación definida por el maestro.
        return nombres
        
    def _inicializar_ui(self):
        main_layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel(f"Registrar Calificaciones: {self._nombre_grupo}")
        lbl_titulo.setObjectName("titulo_principal")
        main_layout.addWidget(lbl_titulo)

        # 1. Selector de Categoría
        selector_layout = QVBoxLayout()
        lbl_categoria = QLabel("Seleccionar Categoría:")
        self.combo_categoria = QComboBox()
        
        if not self._categorias_activas:
            self.combo_categoria.addItem("No hay categorías definidas")
            QMessageBox.warning(self, "Advertencia", "No hay categorías de evaluación definidas para este grupo. Vaya a Administrar Ponderación (CU3).")
            self.btn_guardar = QPushButton("Guardar y Recalcular Promedios") 
            self.btn_guardar.setEnabled(False) 
        else:
            self.combo_categoria.addItems(self._categorias_activas)
            self.combo_categoria.setCurrentText(self._categorias_activas[0])
            self.btn_guardar = QPushButton("Guardar y Recalcular Promedios") 
        
        # Conexión: Al cambiar categoría, recargar la tabla
        self.combo_categoria.currentIndexChanged.connect(self._cargar_datos)
        
        selector_layout.addWidget(lbl_categoria)
        selector_layout.addWidget(self.combo_categoria)
        main_layout.addLayout(selector_layout) 

        # 2. Tabla de Calificaciones
        self.tabla_calificaciones = QTableWidget()
        self.tabla_calificaciones.setColumnCount(3)
        self.tabla_calificaciones.setHorizontalHeaderLabels(["Matrícula", "Nombre Completo", "Calificación (0-10)"])
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Conexión principal: Al editar una celda, guardar automáticamente (FA.1)
        self.tabla_calificaciones.cellChanged.connect(self._guardar_calificacion_celda) 
        main_layout.addWidget(self.tabla_calificaciones)
        
        # 4. Botón Guardar 
        self.btn_guardar.setObjectName("btn_agregar")
        self.btn_guardar.clicked.connect(self._guardar_todo_manual) 
        main_layout.addWidget(self.btn_guardar)
        self.setLayout(main_layout)
        
        # Llama a _cargar_datos después de que todos los widgets están definidos
        if self._categorias_activas:
            self._cargar_datos() 

    def _cargar_datos(self):
        """Muestra la lista de estudiantes con notas existentes para la categoría seleccionada."""
        # Verificar que el combo_categoria no esté vacío antes de llamar currentText
        categoria_seleccionada = self.combo_categoria.currentText()
        if not categoria_seleccionada or categoria_seleccionada == "No hay categorías definidas":
            self.tabla_calificaciones.setRowCount(0)
            return
        
        datos = self.gestor.obtener_alumnos_con_calificaciones(categoria_seleccionada)
        self.tabla_calificaciones.setRowCount(len(datos))
        self.tabla_calificaciones.blockSignals(True) # Bloquear para evitar guardado al cargar
        
        for fila_indice, alumno_data in enumerate(datos):
            matricula, nombre, valor_db = alumno_data
            
            # Columna 0 y 1: Datos del alumno (Solo Lectura)
            item_matricula = QTableWidgetItem(matricula)
            item_matricula.setFlags(item_matricula.flags() & ~Qt.ItemIsEditable) 
            self.tabla_calificaciones.setItem(fila_indice, 0, item_matricula)
            
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFlags(item_nombre.flags() & ~Qt.ItemIsEditable) 
            self.tabla_calificaciones.setItem(fila_indice, 1, item_nombre)
            
            # Columna 2: Calificación 
            valor_str = str(valor_db) if valor_db is not None else ""
            self.tabla_calificaciones.setItem(fila_indice, 2, QTableWidgetItem(valor_str))
            
        self.tabla_calificaciones.blockSignals(False) 

    def _guardar_calificacion_celda(self, row, column):
        """Guarda la calificación en la BLL y recalcula el promedio al cambiar una celda."""
        if column != 2 or not self._categorias_activas:
            return

        matricula = self.tabla_calificaciones.item(row, 0).text()
        categoria = self.combo_categoria.currentText()
        
        self.tabla_calificaciones.blockSignals(True) # Evitar recursión
        
        try:
            nuevo_valor_str = self.tabla_calificaciones.item(row, 2).text().strip()
            
            if not nuevo_valor_str:
                print("Campo vacío. No se registra la calificación.")
                self.tabla_calificaciones.blockSignals(False)
                return

            # Llama al gestor (que ya tiene inicializado _ponderacion_dao)
            resultado_mensaje = self.gestor.registrar_calificacion(matricula, categoria, nuevo_valor_str)
            
            if "Error" in resultado_mensaje:
                QMessageBox.critical(self, "Error de Validación", resultado_mensaje)
                # Opcional: Recargar la celda para mostrar el valor anterior
                # self._cargar_datos() 
            else:
                print(resultado_mensaje)
                
        except Exception as e:
            QMessageBox.critical(self, "Error de Entrada", f"Error inesperado al guardar la nota: {e}")
            
        finally:
            self.tabla_calificaciones.blockSignals(False)

    def _guardar_todo_manual(self):
        """
        Función para el botón 'Guardar.
        """
        if self._categorias_activas:
            try:
                self.gestor.recalcular_promedios_grupo() 
                QMessageBox.information(self, "Éxito", "Notas guardadas. El registro es automático por celda y los promedios fueron recalculados.")
            except AttributeError:
                QMessageBox.critical(self, "Error", "El método 'recalcular_promedios_grupo()' no está implementado en el gestor.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al recalcular promedios: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", "No se puede guardar, no hay categorías definidas.")