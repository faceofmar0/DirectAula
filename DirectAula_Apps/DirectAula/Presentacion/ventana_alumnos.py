# Caso de uso 2
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, 
    QPushButton, QMessageBox, QDialog, QFormLayout, QDialogButtonBox,
    QLabel, QTableWidgetItem, QHeaderView, QStyleFactory
)

from Logica.gestor_alumnos import GestorAlumnos

# ===============================================
# CLASE DE DIÁLOGO PARA AGREGAR/EDITAR ALUMNO
# ===============================================
# Nota: Esta clase no necesita cambios si ya funciona. Se mantiene igual.
class DialogoAlumno(QDialog):
    """Formulario reutilizable para Agregar (FA.1) o Editar (FA.2) Alumno."""
    def __init__(self, datos_alumno=None, parent=None):
        super().__init__(parent)
        self.datos_alumno = datos_alumno 
        self.setWindowTitle("Registrar Alumno" if not datos_alumno else "Editar Alumno")
        self._inicializar_ui(datos_alumno)
    
    def _inicializar_ui(self, datos_alumno):
        layout = QFormLayout()
        
        self.campo_matricula = QLineEdit()
        self.campo_nombre = QLineEdit()
        self.campo_contacto = QLineEdit()
        self.campo_email = QLineEdit() 
        
        # Si se están editando datos, precargarlos
        if datos_alumno:
            # datos_alumno = [matricula, nombre, contacto, email]
            self.campo_matricula.setText(datos_alumno[0])
            self.campo_matricula.setEnabled(False) # No se puede cambiar la matrícula
            self.campo_nombre.setText(datos_alumno[1])
            self.campo_contacto.setText(datos_alumno[2])
            self.campo_email.setText(datos_alumno[3]) # 
            
        layout.addRow("Matrícula ", self.campo_matricula)
        layout.addRow("Nombre Completo ", self.campo_nombre)
        layout.addRow("Datos de Contacto", self.campo_contacto)
        layout.addRow("Email", self.campo_email) 

        #  botones
        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)

        layout.addRow(self.botones)
        self.setLayout(layout)

    def get_data(self):
        """Retorna los 4 campos obligatorios y el email."""
        return (
            self.campo_matricula.text().strip(),
            self.campo_nombre.text().strip(),
            self.campo_contacto.text().strip(),
            self.campo_email.text().strip() 
        )


# ===============================================
# VENTANA PRINCIPAL UC-2 (CAPA DE PRESENTACIÓN)
# ===============================================

class VentanaAlumnos(QWidget):
    def __init__(self, grupo_id, nombre_grupo): 
        super().__init__()
        
        self._grupo_id = grupo_id
        self._nombre_grupo = nombre_grupo # Guardamos el nombre del grupo
        
        self.setWindowTitle(f"DirectAula - Alumnos del grupo: {self._nombre_grupo}") 
        self.resize(750, 500)
        self.gestor = GestorAlumnos(self._grupo_id) 
        
        # 💡 CORRECCIÓN: Pasar el argumento self._nombre_grupo
        self._inicializar_ui(self._nombre_grupo) 
        self._cargar_datos()

    def _inicializar_ui(self, nombre_grupo): 
        main_layout = QVBoxLayout()
        
        # Usar el nombre en la etiqueta principal
        lbl_titulo = QLabel(f"Gestión de Alumnos: {nombre_grupo}") 
        lbl_titulo.setObjectName("titulo_principal")
        
        main_layout.addWidget(lbl_titulo)
        
        # --- SECCIÓN BÚSQUEDA Y ACCIONES ---
        
        # 💡 SUBTÍTULO: "Búsqueda y acciones rápidas"
        self.lbl_subtitulo_acciones = QLabel("Búsqueda y acciones rápidas")
        self.lbl_subtitulo_acciones.setProperty("class", "subtitulo") # Aplica el estilo #003366, negritas, 16px
        main_layout.addWidget(self.lbl_subtitulo_acciones)
        
        top_bar_layout = QHBoxLayout()
        
        # 1. Campo de Búsqueda (AC-2)
        self.campo_busqueda = QLineEdit()
        self.campo_busqueda.setPlaceholderText("Buscar por nombre o matrícula ")
        self.campo_busqueda.textChanged.connect(self._cargar_datos) 
        top_bar_layout.addWidget(self.campo_busqueda, 1)

        # 2. Botones CRUD y Exportar
        # ... (Botones btn_agregar, btn_editar, btn_eliminar, btn_exportar permanecen iguales) ...
        # [Asegúrate de que tus botones mantienen los objectName para el CSS: btn_agregar, btn_editar, etc.]
        self.btn_agregar = QPushButton("➕ Agregar")
        self.btn_agregar.setObjectName("btn_agregar")
        self.btn_agregar.clicked.connect(lambda: self._mostrar_formulario(None))
        
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setObjectName("btn_editar")
        self.btn_editar.clicked.connect(self._mostrar_formulario_editar)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setObjectName("btn_eliminar")
        self.btn_eliminar.clicked.connect(self._eliminar_alumno_seleccionado)
        
        self.btn_exportar = QPushButton("📊 Exportar")
        self.btn_exportar.setObjectName("btn_exportar")
        self.btn_exportar.clicked.connect(lambda: QMessageBox.information(self, "Exportar", "Funcionalidad de exportar a Excel (UC-6) pendiente."))

        top_bar_layout.addWidget(self.btn_agregar, 0)
        top_bar_layout.addWidget(self.btn_editar, 0)
        top_bar_layout.addWidget(self.btn_eliminar, 0)
        top_bar_layout.addWidget(self.btn_exportar, 0)

        main_layout.addLayout(top_bar_layout)
        
        # --- SECCIÓN LISTA DE ALUMNOS ---
        
        # 💡 SUBTÍTULO: "Lista de alumnos"
        self.lbl_subtitulo_lista = QLabel("Lista de alumnos")
        self.lbl_subtitulo_lista.setProperty("class", "subtitulo") # Aplica el estilo #003366, negritas, 16px
        main_layout.addWidget(self.lbl_subtitulo_lista)
        
        # 3. Tabla de alumnos (R)
        self.tabla_alumnos = QTableWidget() 
        self.tabla_alumnos.setColumnCount(4) 
        self.tabla_alumnos.setHorizontalHeaderLabels(["Matrícula", "Nombre Completo", "Contacto", "Email"])
        self.tabla_alumnos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        main_layout.addWidget(self.tabla_alumnos)

        self.setLayout(main_layout)

    def _cargar_datos(self):
        """Muestra los datos obtenidos de la BLL en la tabla y aplica filtrado (AC-2)."""
        datos = self.gestor.obtener_lista_alumnos()
        
        self.tabla_alumnos.setRowCount(0) 
        busqueda_texto = self.campo_busqueda.text().lower()
        
        fila_indice = 0
        for alumno_data in datos:
            # alumno_data es: [matricula, nombre, contacto, email, grupo_id]
            
            # Filtrado rápido por matrícula o nombre (AC-2)
            if busqueda_texto in alumno_data[0].lower() or busqueda_texto in alumno_data[1].lower():
                
                self.tabla_alumnos.insertRow(fila_indice)
                
                # Insertamos los 4 campos (Matrícula, Nombre, Contacto, Email)
                for columna, valor in enumerate(alumno_data[:4]): 
                    # Aseguramos que los valores nulos o None sean tratados como cadena vacía
                    display_valor = str(valor) if valor is not None else "" 
                    item = QTableWidgetItem(display_valor)
                    self.tabla_alumnos.setItem(fila_indice, columna, item)
                
                fila_indice += 1
    
    # 💡 FUNCIÓN AUXILIAR CRUCIAL PARA CORREGIR EL ERROR DEL BOTÓN EDITAR
    def _get_cell_text_safe(self, row, col):
        """Extrae el texto de una celda de la tabla de forma segura, manejando celdas vacías."""
        item = self.tabla_alumnos.item(row, col)
        # Si la celda es None (está vacía), retorna una cadena vacía en lugar de fallar al llamar .text()
        return item.text() if item is not None else ""

    def _mostrar_formulario(self, datos_alumno=None):
        """Función unificada para agregar o editar."""
        dialogo = DialogoAlumno(datos_alumno, self)
        
        if dialogo.exec_() == QDialog.Accepted:
            
            #DEBE DESEMPAQUETAR 4 VALORES
            matricula, nombre, contacto, email = dialogo.get_data() 
            
            if datos_alumno is None:
                # Lógica Agregar
                # 💡 LLAMAR CON 4 ARGUMENTOS
                resultado_mensaje = self.gestor.agregar_nuevo_alumno(matricula, nombre, contacto, email)
            else:
                # Lógica Editar (la matrícula ya está definida en el diálogo)
                # 💡 LLAMAR CON 4 ARGUMENTOS
                resultado_mensaje = self.gestor.actualizar_datos_alumno(matricula, nombre, contacto, email)
            if "Error" in resultado_mensaje:
                QMessageBox.critical(self, "Error", resultado_mensaje)
            else:
                QMessageBox.information(self, "Operación Exitosa", resultado_mensaje)
                self._cargar_datos()

    def _mostrar_formulario_editar(self):
        """CORREGIDO: Prepara los datos de la fila seleccionada (U) manejando errores."""
        fila_seleccionada = self.tabla_alumnos.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un alumno para editar.")
            return

       
        datos_seleccionados = [
            self._get_cell_text_safe(fila_seleccionada, 0), # Matrícula
            self._get_cell_text_safe(fila_seleccionada, 1), # Nombre
            self._get_cell_text_safe(fila_seleccionada, 2), # Contacto
            self._get_cell_text_safe(fila_seleccionada, 3)  # Email
        ]
        
        self._mostrar_formulario(datos_seleccionados)
        
    def _eliminar_alumno_seleccionado(self):
        # ... (código de eliminación: no requiere cambios) ...
        fila_seleccionada = self.tabla_alumnos.currentRow()
        if fila_seleccionada < 0:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un alumno para eliminar.")
            return
        matricula = self.tabla_alumnos.item(fila_seleccionada, 0).text()
        
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar permanentemente al alumno con Matrícula {matricula}? (BR.6)",
            QMessageBox.Yes | QMessageBox.No)

        if confirmacion == QMessageBox.Yes:
            resultado_mensaje = self.gestor.eliminar_alumno(matricula)
            
            if "Error" in resultado_mensaje:
                QMessageBox.critical(self, "Error de Eliminación", resultado_mensaje)
            else:
                QMessageBox.information(self, "Operación Exitosa", resultado_mensaje)
                self._cargar_datos()


# ===============================================
# PUNTO DE ARRANQUE FINAL
# ===============================================

if __name__ == '__main__':
    QApplication.setStyle(QStyleFactory.create('Fusion')) 
    app = QApplication(sys.argv)
    
    try:
        with open('style.css', 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Advertencia: El archivo style.css no fue encontrado.")

    ventana = VentanaAlumnos(grupo_id=1) 
    ventana.show()
    sys.exit(app.exec_())