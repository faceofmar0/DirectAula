# ventana_registro_profesor.py

from email.mime import application
import sys
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QLineEdit, 
    QPushButton, QLabel, QMessageBox, QFrame, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Logica.gestor_autenticacion import GestorAutenticacion

class VentanaRegistroProfesor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DirectAula - Registro de Profesor")
        self.setFixedSize(400, 550)
        
        self.gestor = GestorAutenticacion()
        self._usuario_registrado = "" # Almacena el nombre de usuario creado
        
        self._inicializar_ui()
        
    def _inicializar_ui(self):
        # Estilos de la ventana de registro
        self.setStyleSheet("""
            QDialog {
                background-color: #F7FAFC; /* Gris muy claro */
            }
            QFrame {
                background-color: white;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            QLineEdit {
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3182CE; /* Azul */
            }
            QPushButton#btnGuardar {
                background-color: #3182CE;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                height: 45px;
            }
            QPushButton#btnGuardar:hover {
                background-color: #2C5282;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        main_frame = QFrame()
        main_frame.setFixedSize(350, 500)
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setAlignment(Qt.AlignTop)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        lbl_titulo = QLabel("Nuevo Profesor")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #2D3748; margin-bottom: 20px;")
        frame_layout.addWidget(lbl_titulo)

        # Campos de formulario
        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Nombre Completo")
        self.campo_nombre.setFixedHeight(40)
        frame_layout.addWidget(self.campo_nombre)
        
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("Correo Electrónico (Opcional)")
        self.campo_email.setFixedHeight(40)
        frame_layout.addWidget(self.campo_email)

        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Nombre de Usuario (Único)")
        self.campo_usuario.setFixedHeight(40)
        frame_layout.addWidget(self.campo_usuario)

        self.campo_password = QLineEdit()
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setEchoMode(QLineEdit.Password)
        self.campo_password.setFixedHeight(40)
        frame_layout.addWidget(self.campo_password)

        self.campo_confirmar_password = QLineEdit()
        self.campo_confirmar_password.setPlaceholderText("Confirmar Contraseña")
        self.campo_confirmar_password.setEchoMode(QLineEdit.Password)
        self.campo_confirmar_password.setFixedHeight(40)
        frame_layout.addWidget(self.campo_confirmar_password)

        frame_layout.addStretch(1)

        # Botón Guardar
        btn_guardar = QPushButton("Registrar Profesor")
        btn_guardar.setObjectName("btnGuardar")
        btn_guardar.clicked.connect(self._registrar_profesor)
        frame_layout.addWidget(btn_guardar)
        
        # Botón Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("border: none; color: #718096; font-size: 13px; margin-top: 5px;")
        btn_cancelar.clicked.connect(self.reject)
        frame_layout.addWidget(btn_cancelar)

        main_layout.addWidget(main_frame)
        
        # Conectar eventos de teclado
        self.campo_confirmar_password.returnPressed.connect(btn_guardar.click)


    def _registrar_profesor(self):
        """Intenta registrar un nuevo profesor en la base de datos."""
        nombre = self.campo_nombre.text().strip()
        email = self.campo_email.text().strip()
        usuario = self.campo_usuario.text().strip()
        password = self.campo_password.text()
        confirm_password = self.campo_confirmar_password.text()
        
        # 1. Validación de campos obligatorios
        if not nombre or not usuario or not password or not confirm_password:
            QMessageBox.warning(self, "Error de Validación", "Todos los campos con (*) son obligatorios.")
            return

        # 2. Validación de contraseñas
        if password != confirm_password:
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            self.campo_password.setText("")
            self.campo_confirmar_password.setText("")
            self.campo_password.setFocus()
            return

        # 3. Intentar el registro
        resultado = self.gestor.registrar_profesor(nombre, usuario, password, email)
        
        if resultado:
            # Si el registro fue exitoso:
            self._usuario_registrado = usuario
            QMessageBox.information(self, "Registro Exitoso", f"Profesor '{nombre}' registrado. Ahora puedes iniciar sesión.")
            # Indica a la ventana padre que la operación fue aceptada (QDialog.Accepted)
            self.accept() 
        else:
            QMessageBox.critical(self, "Error de Registro", "El nombre de usuario ya existe o hubo un error en la base de datos.")
            self.campo_usuario.selectAll()
            self.campo_usuario.setFocus()

    def get_usuario_registrado(self):
        """Método público para retornar el usuario registrado."""
        return self._usuario_registrado

if __name__ == "__main__":
    app = application([])
    # Ejemplo de uso (no debería ejecutarse directamente en el flujo principal)
    ventana = VentanaRegistroProfesor()
    if ventana.exec_() == QDialog.Accepted:
        print(f"Usuario creado: {ventana.get_usuario_registrado()}")
    else:
        print("Registro cancelado.")
    sys.exit(0)