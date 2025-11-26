# presentacion/dialogo_seleccion_grupo.py (NUEVO ARCHIVO)

from PyQt5.QtWidgets import (
    QDialog, QComboBox, QVBoxLayout, QLabel, 
    QDialogButtonBox, QMessageBox
)
# Importación del Gestor de Grupos que ya existe en la lógica
from Logica.gestor_alumnos import GestorGrupos 

class SeleccionGrupo(QDialog):
    """Obliga al usuario a seleccionar un Grupo antes de continuar."""
    
    def __init__(self, titulo_accion, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Seleccionar Grupo - {titulo_accion}")
        self.resize(300, 150)
        self._gestor_grupos = GestorGrupos()
        self._grupo_seleccionado_id = None
        self._grupos_disponibles = {} # Diccionario: {nombre_completo: id}
        
        self._inicializar_ui(titulo_accion)
        self._cargar_grupos()

    def _inicializar_ui(self, titulo_accion):
        layout = QVBoxLayout(self)
        
        lbl_instruccion = QLabel(f"Por favor, seleccione el grupo para {titulo_accion} :")
        lbl_instruccion.setObjectName("subtitulo")
        layout.addWidget(lbl_instruccion)
        
        self.combo_grupos = QComboBox()
        layout.addWidget(self.combo_grupos)

        self.botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.botones.accepted.connect(self._aceptar_seleccion)
        self.botones.rejected.connect(self.reject)
        layout.addWidget(self.botones)

    def _cargar_grupos(self):
        """Carga los grupos disponibles desde la BLL en el ComboBox."""
        grupos = self._gestor_grupos.obtener_lista_grupos() # Retorna: [id, nombre, ciclo]
        
        if not grupos:
            QMessageBox.warning(self, "Advertencia", 
                "No hay grupos registrados. Debe crear uno primero en el CU1."
            )
            self.botones.button(QDialogButtonBox.Ok).setEnabled(False)
            return
            
        self.combo_grupos.clear()
        
        for grupo_id, nombre, ciclo in grupos:
            # Creamos un nombre amigable para mostrar en la interfaz
            nombre_display = f"{nombre} ({ciclo})"
            self.combo_grupos.addItem(nombre_display)
            self._grupos_disponibles[nombre_display] = grupo_id

    def _aceptar_seleccion(self):
        """Valida la selección y guarda el ID."""
        nombre_seleccionado = self.combo_grupos.currentText()
        if nombre_seleccionado in self._grupos_disponibles:
            self._grupo_seleccionado_id = self._grupos_disponibles[nombre_seleccionado]
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Debe seleccionar un grupo válido.")

    def get_grupo_id(self):
        """Retorna el ID del grupo seleccionado."""
        return self._grupo_seleccionado_id