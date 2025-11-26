from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
# Solo necesitamos GestorCalificaciones, ya no GestorGrupos
from Logica.gestor_alumnos import GestorCalificaciones 

class VentanaCalificacionFinal(QDialog):
    """
    Ventana para mostrar la Calificación Final Ponderada (BR.14) 
    y el Estado de Riesgo (BR.12) de los alumnos de un grupo específico.
    """
    def __init__(self, grupo_id, nombre_grupo, parent=None):
        super().__init__(parent)
        self._grupo_id = grupo_id
        self._nombre_grupo = nombre_grupo
        
        self.setWindowTitle(f"Calificación Final - {nombre_grupo} ")
        # Tamaño recomendado para que quepan las 5 columnas
        self.setGeometry(100, 100, 850, 600) 
        
        self._setup_ui()
        self._cargar_resultados() # Cargar los datos inmediatamente al iniciar

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)

        # Etiqueta de título que muestra el grupo actual
        lbl_titulo = QLabel(f"Resultados Finales del Grupo: {self._nombre_grupo}")
        lbl_titulo.setObjectName("titulo_principal")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        # 2. Tabla de Resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(5)
        self.tabla_resultados.setHorizontalHeaderLabels([
            "Matrícula", "Nombre Completo", "Promedio Final (BR.14)", "Asistencia (%)", "Estado de Riesgo (BR.12)"
        ])
        
        # Configuración para que las columnas se ajusten automáticamente
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        
        layout_principal.addWidget(self.tabla_resultados)
        
        # Botón opcional para la funcionalidad futura de Reporte Excel (CU6)
        btn_reporte = QPushButton("Generar Reporte Excel (CU6)")
        btn_reporte.setEnabled(False) # Deshabilitado hasta implementar la exportación
        layout_principal.addWidget(btn_reporte)


    def _cargar_resultados(self):
        """
        Llama al GestorCalificaciones para obtener y mostrar 
        los promedios y estados de riesgo del grupo actual.
        """
        try:
            # Usamos el grupo_id que ya recibimos en el constructor
            gestor_calif = GestorCalificaciones(self._grupo_id)
            
            # Llamada al método central de la lógica (CU6)
            resultados = gestor_calif.calcular_promedios_y_estado_final()
            
            self.tabla_resultados.setRowCount(len(resultados))
            
            for row, data in enumerate(resultados):
                matricula, nombre, promedio, asistencia, riesgo = data
                
                self.tabla_resultados.setItem(row, 0, QTableWidgetItem(matricula))
                self.tabla_resultados.setItem(row, 1, QTableWidgetItem(nombre))
                
                # Promedio Final (BR.17: Redondeo a 2 decimales)
                item_promedio = QTableWidgetItem(f"{promedio:.2f}")
                item_promedio.setTextAlignment(Qt.AlignCenter)
                self.tabla_resultados.setItem(row, 2, item_promedio)
                
                # Asistencia % (BR.17)
                item_asistencia = QTableWidgetItem(f"{asistencia:.2f}%")
                item_asistencia.setTextAlignment(Qt.AlignCenter)
                self.tabla_resultados.setItem(row, 3, item_asistencia)
                
                # Estado de Riesgo (BR.12)
                item_riesgo = QTableWidgetItem(riesgo)
                item_riesgo.setTextAlignment(Qt.AlignCenter)
                
                # Resaltado visual para el estado de riesgo
                if "Riesgo" in riesgo:
                    # Aplicar color rojo
                    item_riesgo.setForeground(Qt.red)
                elif riesgo == "Normal":
                    # Color verde para estado Normal
                    item_riesgo.setForeground(Qt.darkGreen) 
                    
                self.tabla_resultados.setItem(row, 4, item_riesgo)
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"Ocurrió un error al cargar los datos: {str(e)}")