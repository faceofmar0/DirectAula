# presentacion/ventana_login.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, 
    QPushButton, QLabel, QMessageBox, QFrame, QDialog, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Logica.gestor_autenticacion import GestorAutenticacion
from Presentacion.ventana_registro_profesor import VentanaRegistroProfesor 

class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        # Inicializa el gestor de autenticación
        self.gestor = GestorAutenticacion()
        self.ventana_principal = None
        self._inicializar_ui()

    def _inicializar_ui(self):
        self.setWindowTitle("DirectAula - Iniciar Sesión")
        self.setFixedSize(450, 450) 
        self.setStyleSheet("""
            VentanaLogin {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #EAF6FF,
                    stop:0.5 #F6FBFF,
                    stop:1 #EAFBF2);
            }
            QLineEdit {
                border: 1px solid #D6E9F8;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background: ##FF9999;
                color: #2B3A42;
            }
            QLineEdit:focus {
                border: 2px solid #7FB7FF;
                background: #FFFFFF;
            }
            QPushButton {
                background-color: #5AA6FF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3C8EE6;
            }
            QPushButton:disabled {
                background-color: #BFDFFF;
                color: #7A8B96;
            }
            QLabel {
                color: #334E5A;
            }
        """)
        # Estilo de fondo con degradado
        self.setStyleSheet("""
            VentanaLogin {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #DFF3FF,      /* azul pastel */
                    stop:0.5 #E8FFF5,    /* verde pastel */
                    stop:1 #FFE6E6);     /* rojo pastel suave */
            }

            QLineEdit {
                border: 1px solid #BBD7E4;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background: #F0F8FF;     /* azul muy suave */
                color: #2B3A42;
            }

            QLineEdit:focus {
                border: 2px solid #7FB7FF;
                background: #FFFFFF;
            }

            QPushButton {
                background-color: #7EC8E3;   /* azul claro suave */
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #68B3D1;   /* azul suave más oscuro */
            }

            QPushButton:disabled {
                background-color: #CFEAF5;
                color: #7A8B96;
            }

            QLabel {
                color: #334E5A;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Frame principal
        main_frame = QFrame()
        main_frame.setFixedSize(380, 480) 
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setAlignment(Qt.AlignTop)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        
        # --- Logo y Título ---
        
        # Logo/Icono
        lbl_icono = QLabel("🎓") 
        lbl_icono.setAlignment(Qt.AlignCenter)
        lbl_icono.setStyleSheet("font-size: 60px; color: #FF6B35;")
        lbl_icono.setFixedHeight(80)
        frame_layout.addWidget(lbl_icono)
        
        # Título
        lbl_titulo = QLabel("Bienvenido a DirectAula")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #2D3748; margin-bottom: 5px;")
        frame_layout.addWidget(lbl_titulo)

        # Subtítulo
        lbl_subtitulo = QLabel("Ingresa tus credenciales de Profesor")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        lbl_subtitulo.setFont(QFont("Arial", 10))
        lbl_subtitulo.setStyleSheet("color: #718096; margin-bottom: 20px;")
        frame_layout.addWidget(lbl_subtitulo)
        
        # --- Formulario de login ---
        
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Nombre de usuario")
        self.campo_usuario.setFixedHeight(45)
        frame_layout.addWidget(self.campo_usuario)
        
        self.campo_password = QLineEdit()
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setEchoMode(QLineEdit.Password)
        self.campo_password.setFixedHeight(45)
        frame_layout.addWidget(self.campo_password)
        
        frame_layout.addSpacing(15)
        
        # Botón de login
        btn_login = QPushButton("Iniciar Sesión")
        btn_login.setFixedHeight(45)
        btn_login.clicked.connect(self._autenticar_usuario)
        frame_layout.addWidget(btn_login)
        
        frame_layout.addSpacing(10)

        # Botón de registro
        btn_registro = QPushButton("Crear cuenta de Profesor")
        btn_registro.setStyleSheet("border: none; color: #4299E1; font-size: 13px; padding: 5px;")
        btn_registro.clicked.connect(self._abrir_registro)
        frame_layout.addWidget(btn_registro)
        
        # Espaciador para centrar verticalmente el contenido
        frame_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Texto informativo (demo)
        lbl_info = QLabel("")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setStyleSheet("""
            QLabel {
                color: #718096; font-size: 10px; font-style: italic;
                background-color: rgba(237, 242, 247, 0.8);
                padding: 6px 10px; border-radius: 5px;
            }
        """)
        lbl_info.setFixedHeight(30)
        frame_layout.addWidget(lbl_info)
        
        main_layout.addWidget(main_frame)
        
        # Conectar eventos de teclado (Enter)
        self.campo_password.returnPressed.connect(btn_login.click)
        self.campo_usuario.setFocus()
    # ======================================================
    # MÉTODOS DE LA LÓGICA DE LOGIN (CORREGIDOS Y AÑADIDOS)
    # ======================================================
    def _autenticar_usuario(self): 
        """
        [CORREGIDO] Autentica al usuario usando GestorAutenticacion.
        Este era el método faltante que causaba el AttributeError.
        """
        usuario = self.campo_usuario.text().strip()
        password = self.campo_password.text().strip()
        
        if not usuario or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            self.campo_usuario.setFocus()
            return
            
        # Deshabilitar interfaz durante autenticación
        self.setEnabled(False)
        QApplication.processEvents()
        
        try:
            resultado = self.gestor.autenticar_profesor(usuario, password)
            
            if resultado["autenticado"]:
                QMessageBox.information(self, "✅ Éxito", f"Bienvenido, {resultado['nombre']}!")
                self._abrir_ventana_principal()
            else:
                QMessageBox.critical(self, "Error de Autenticación", resultado["mensaje"])
                self.campo_password.selectAll()
                self.campo_password.setFocus()
        
        except Exception as e:
            # Captura errores de base de datos o lógica
            QMessageBox.critical(self, "Error del Sistema", f"Error al conectar con el sistema: {str(e)}")
            self.campo_usuario.setFocus()
        finally:
            self.setEnabled(True)

    def _abrir_ventana_principal(self):
        """
        [CORREGIDO] Cierra la ventana de login y abre la ventana principal.
        """
        try:
            # Importación local para evitar dependencia circular
            from app import VentanaMenuPrincipal 
            self.ventana_principal = VentanaMenuPrincipal()
            self.ventana_principal.show()
            self.close()
        except ImportError:
            QMessageBox.critical(self, "Error", "No se pudo cargar la Ventana Menu Principal. Verifique app.py.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana principal: {str(e)}")
            
    def _abrir_registro(self):
        """
        [CORREGIDO] Abre la ventana de registro de profesor como modal.
        """
        ventana_registro = VentanaRegistroProfesor(self)
        if ventana_registro.exec_() == QDialog.Accepted:
            # Si el registro fue exitoso, llenamos el campo de usuario
            self.campo_usuario.setText(ventana_registro.get_usuario_registrado())
            self.campo_password.setFocus()
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_login = VentanaLogin()
    ventana_login.show()
    sys.exit(app.exec_())