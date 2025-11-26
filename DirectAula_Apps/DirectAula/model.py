
# model.py
from datetime import date
class Alumno:
    """Representa un estudiante dentro de un grupo."""
    
    def __init__(self, matricula, nombre_completo, datos_contacto, email):
        self._matricula = matricula
        self._nombre_completo = nombre_completo
        self._datos_contacto = datos_contacto
        self._email = email 
        self._grupo_id = None #Referencia al grupo al que pertenece

    def get_matricula(self):
        return self._matricula

    def get_nombre_completo(self): 
        return self._nombre_completo 

    def get_datos_contacto(self):
        return self._datos_contacto
        
    def get_email(self):
        return self._email
    # Setters
    def set_nombre_completo(self, nombre_completo):
        self._nombre_completo = nombre_completo
        
    def set_datos_contacto(self, contacto):
        self._datos_contacto = contacto

    def set_email(self, email):
        self._email = email

    # Método para validación interna (BR.4)
    def es_valido(self):
        return bool(self._matricula) and bool(self._nombre_completo)
    
class Asistencia:
    """Representa el registro de asistencia para un alumno en una fecha dada."""
    def __init__(self, matricula, fecha, estado="Presente"):
        self._matricula = matricula
        self._fecha = fecha
        self._estado = estado
        
    def get_matricula(self):
        return self._matricula

    def get_fecha(self):
        return self._fecha

    def get_estado(self):
        return self._estado
    
    def set_estado(self, estado):
        self._estado = estado

class Grupo:
    """Representa un Grupo (o curso) académico."""
    # Nota: Usaremos el id como clave primaria interna, y el nombre/ciclo para BR.1
    def __init__(self, grupo_id, nombre, ciclo_escolar):
        self._grupo_id = grupo_id # Usado internamente para referencias
        self._nombre = nombre
        self._ciclo_escolar = ciclo_escolar

    def get_id(self):
        return self._grupo_id

    def get_nombre(self):
        return self._nombre
    
    def get_ciclo(self):
        return self._ciclo_escolar

class CategoriaEvaluacion:
    """Representa una categoría de evaluación (ponderación) dentro de un grupo."""
    def __init__(self, grupo_id, nombre_categoria, peso_porcentual, max_items=1):
        self._grupo_id = grupo_id
        self._nombre_categoria = nombre_categoria
        self._peso_porcentual = peso_porcentual  # Ej: 30.0 (30%)
        self._max_items = max_items  # BR.9 (No visible pero importante si lo implementas)

    # Getters (para el DAO)
    def get_grupo_id(self):
        return self._grupo_id

    def get_nombre_categoria(self):
        return self._nombre_categoria

    def get_peso_porcentual(self):
        return self._peso_porcentual

    def get_max_items(self):
        return self._max_items

    # Setters (para modificaciones en la UI)
    def set_peso_porcentual(self, peso):
        self._peso_porcentual = peso

class Calificacion:
    """Representa una calificación individual de un alumno en una categoría en una fecha."""
    def __init__(self, matricula, categoria, valor, fecha=None):
        self._matricula = matricula
        self._categoria = categoria
        self._valor = valor
        # Si no se proporciona fecha, usa la de hoy (ISO 8601: YYYY-MM-DD)
        self._fecha = fecha if fecha is not None else date.today().isoformat()

    # Getters
    def get_matricula(self):
        return self._matricula

    def get_categoria(self):
        return self._categoria

    def get_valor(self):
        return self._valor

    def get_fecha(self):
        return self._fecha

    # Métodos para tuplas de BD
    def to_tuple(self):
        return (self._matricula, self._categoria, self._fecha, self._valor)