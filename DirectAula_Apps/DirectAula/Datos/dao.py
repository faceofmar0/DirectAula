from datetime import date
import sqlite3
# Asegúrate que las entidades del modelo estén importadas
from model import Alumno, Asistencia, Calificacion, CategoriaEvaluacion, Grupo 

# ====================================================
# BASE DAO (Manejo de Conexión y Creación de Tablas)
# ====================================================
class BaseDAO:
    def __init__(self):
        self._db_file = 'directaula.db'
        self._con = None
        self.inicializar_tablas() 
        
    def inicializar_tablas(self):
        """Asegura que todas las tablas necesarias existan."""
        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS grupos (
                grupo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ciclo_escolar TEXT NOT NULL
            );
        """)
        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS alumnos (
                matricula TEXT PRIMARY KEY,
                nombre_completo TEXT NOT NULL,
                datos_contacto TEXT,
                email TEXT,
                grupo_id INTEGER,
                FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id)
            );
        """)
        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS categorias_evaluacion (
                grupo_id INTEGER NOT NULL,
                nombre_categoria TEXT NOT NULL,
                peso_porcentual REAL NOT NULL,
                max_items INTEGER NOT NULL DEFAULT 1, 
                PRIMARY KEY (grupo_id, nombre_categoria),
                FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id) ON DELETE CASCADE
            );
        """)
        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS asistencia (
                matricula TEXT NOT NULL,
                fecha TEXT NOT NULL,
                estado TEXT NOT NULL,
                PRIMARY KEY (matricula, fecha),
                FOREIGN KEY (matricula) REFERENCES alumnos(matricula) ON DELETE CASCADE
            );
        """)
        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS calificaciones (
                matricula TEXT NOT NULL,
                categoria TEXT NOT NULL,
                fecha TEXT NOT NULL,
                valor REAL NOT NULL,
                PRIMARY KEY (matricula, categoria, fecha),
                FOREIGN KEY (matricula) REFERENCES alumnos(matricula) ON DELETE CASCADE
            );
        """)

        self.ejecutar_query("""
            CREATE TABLE IF NOT EXISTS profesores (
    profesor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL, -- El usuario debe ser único
    password TEXT NOT NULL,
    email TEXT
            );
        """)
        
    def _conectar(self):
        self._con = sqlite3.connect(self._db_file)
        self._con.execute("PRAGMA foreign_keys = ON;") 
        self.cursor = self._con.cursor()
        return self._con

    def _desconectar(self, conn=None):
        connection = conn or self._con
        if connection:
            connection.close()
            if conn is None:
                self._con = None

    def ejecutar_query(self, query, params=()):
        try:
            conn = self._conectar()
            self.cursor.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                return self.cursor.fetchall()
            return True
        except sqlite3.Error as e:
            print(f"Error al ejecutar consulta: {e}") 
            return False
        finally:
            self._desconectar(conn)
            
    def ejecutar_queries_multiples(self, query: str, params_list: list[tuple]):
        """Ejecuta una sola query varias veces con diferentes parámetros en una transacción."""
        try:
            conn = self._conectar()
            self.cursor.executemany(query, params_list)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al ejecutar múltiples queries: {e}")
            conn.rollback()
            return False
        finally:
            self._desconectar(conn)

# ====================================================
# 1. GRUPO DAO (CASO DE USO 1) 
# ====================================================
class GrupoDAO(BaseDAO):
    """Maneja las operaciones CRUD para la entidad Grupo."""
    # (MÉTODOS OMITIDOS POR BREVEDAD, ASUMIMOS QUE ESTÁN CORRECTOS)

    def crear_grupo(self, grupo: Grupo):
        query = "INSERT INTO grupos (nombre, ciclo_escolar) VALUES (?, ?)"
        params = (grupo.get_nombre(), grupo.get_ciclo())
        return self.ejecutar_query(query, params)

    def obtener_grupos(self):
        query = "SELECT grupo_id, nombre, ciclo_escolar FROM grupos ORDER BY ciclo_escolar, nombre"
        return self.ejecutar_query(query)

    def buscar_grupo_por_nombre_ciclo(self, nombre, ciclo_escolar):
        query = "SELECT grupo_id FROM grupos WHERE nombre = ? AND ciclo_escolar = ?"
        resultado = self.ejecutar_query(query, (nombre, ciclo_escolar))
        return resultado[0][0] if resultado else None

    def actualizar_grupo(self, grupo: Grupo):
        query = "UPDATE grupos SET nombre = ?, ciclo_escolar = ? WHERE grupo_id = ?"
        params = (grupo.get_nombre(), grupo.get_ciclo(), grupo.get_id())
        return self.ejecutar_query(query, params)

    def eliminar_grupo(self, grupo_id):
        query = "DELETE FROM grupos WHERE grupo_id = ?"
        return self.ejecutar_query(query, (grupo_id,))


# ====================================================
# 2. ALUMNO DAO (CASO DE USO 2)
# ====================================================
class AlumnoDAO(BaseDAO):
    """Maneja las operaciones CRUD para la entidad Alumno."""
    # (MÉTODOS OMITIDOS POR BREVEDAD, ASUMIMOS QUE ESTÁN CORRECTOS)
    
    def crear_alumno(self, alumno: Alumno, grupo_id):
        query = "INSERT INTO alumnos (matricula, nombre_completo, datos_contacto, email, grupo_id) VALUES (?, ?, ?, ?, ?)"
        params = (alumno.get_matricula(), alumno.get_nombre_completo(), alumno.get_datos_contacto(), alumno.get_email(), grupo_id)
        return self.ejecutar_query(query, params)

    def obtener_alumnos_por_grupo(self, grupo_id):
        query = "SELECT matricula, nombre_completo, datos_contacto, email FROM alumnos WHERE grupo_id = ? ORDER BY nombre_completo"
        return self.ejecutar_query(query, (grupo_id,))

    def actualizar_alumno(self, alumno: Alumno):
        query = "UPDATE alumnos SET nombre_completo = ?, datos_contacto = ?, email = ? WHERE matricula = ?"
        params = (alumno.get_nombre_completo(), alumno.get_datos_contacto(), alumno.get_email(), alumno.get_matricula())
        return self.ejecutar_query(query, params)

    def eliminar_alumno(self, matricula):
        query = "DELETE FROM alumnos WHERE matricula = ?"
        return self.ejecutar_query(query, (matricula,))


# ====================================================
# 3. ASISTENCIA DAO (CASO DE USO 4 y 6)
# ====================================================
class AsistenciaDAO(BaseDAO):
    """Maneja las operaciones CRUD para el registro de Asistencia."""

    def registrar_asistencia(self, asistencia_obj: Asistencia):
        fecha = asistencia_obj.get_fecha() or date.today().isoformat()
        estado = asistencia_obj.get_estado() or "Presente"
        query = "REPLACE INTO asistencia (matricula, fecha, estado) VALUES (?, ?, ?)"
        params = (asistencia_obj.get_matricula(), fecha, estado)
        return self.ejecutar_query(query, params)
        
    def obtener_asistencia_del_dia(self, fecha, grupo_id):
        query = """
            SELECT 
                A.matricula, 
                A.nombre_completo, 
                COALESCE(S.estado, 'Ausente') 
            FROM alumnos A
            LEFT JOIN asistencia S 
            ON A.matricula = S.matricula AND S.fecha = ?
            WHERE A.grupo_id = ?
            ORDER BY A.nombre_completo;
        """
        return self.ejecutar_query(query, (fecha, grupo_id))

    def obtener_porcentaje_asistencia_por_alumno(self, matricula: str) -> float:
        """
        ✅ MÉTODO AGREGADO para CU6. 
        Calcula el porcentaje de asistencia (Asistencia + Justificado) / Total de días registrados.
        """
        query = """
        SELECT 
            CAST(SUM(CASE WHEN estado IN ('Asistencia', 'Justificado') THEN 1 ELSE 0 END) AS REAL) AS asistencias_contables,
            COUNT(fecha) AS total_dias_registrados
        FROM asistencia
        WHERE matricula = ?;
        """
        resultado = self.ejecutar_query(query, (matricula,))
        
        if resultado and resultado[0]:
            asistencias, total_dias = resultado[0]
            if total_dias > 0:
                porcentaje = (asistencias / total_dias) * 100
                return round(porcentaje, 2) # BR.17
        
        return 100.0


# ====================================================
# 4. CATEGORIAEVALUACION DAO (Ponderación flexible - CU3)
# ====================================================
class CategoriaEvaluacionDAO(BaseDAO):
    """Maneja las operaciones CRUD para las Ponderaciones (Categorias de Evaluación)."""

    def crear_ponderacion_inicial(self, grupo_id: int) -> bool:
        """Crea un conjunto inicial de categorías si no existen (BR.3)."""
        try:
            conn = self._conectar()
            query_check = "SELECT COUNT(*) FROM categorias_evaluacion WHERE grupo_id = ?"
            self.cursor.execute(query_check, (grupo_id,))
            count = self.cursor.fetchone()[0]

            if count == 0:
                default_categories = [
                    (grupo_id, 'Examen Final', 50.0, 1),
                    (grupo_id, 'Tareas', 30.0, 1),
                    (grupo_id, 'Participación', 20.0, 1),
                ]
                query_insert = """
                INSERT INTO categorias_evaluacion (grupo_id, nombre_categoria, peso_porcentual, max_items) 
                VALUES (?, ?, ?, ?)
                """
                self.cursor.executemany(query_insert, default_categories)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al crear ponderaciones iniciales: {e}")
            conn.rollback()
            return False
        finally:
            self._desconectar(conn)
            
    def obtener_categorias_por_grupo(self, grupo_id):
        """Retorna todas las categorías de evaluación para un grupo (objetos CategoriaEvaluacion)."""
        query = """
        SELECT grupo_id, nombre_categoria, peso_porcentual, max_items
        FROM categorias_evaluacion 
        WHERE grupo_id = ?
        ORDER BY nombre_categoria
        """
        resultados = self.ejecutar_query(query, (grupo_id,))
        
        categorias = [
            CategoriaEvaluacion(r[0], r[1], r[2], r[3]) for r in resultados
        ]
        return categorias

    def guardar_ponderaciones(self, categorias: list[CategoriaEvaluacion], grupo_id: int):
        """
        ✅ MÉTODO CORREGIDO: Soluciona el error 'type list is not supported'.
        Reemplaza TODAS las categorías de un grupo en una transacción.
        """
        try:
            conn = self._conectar()
            
            # 1. Eliminar las categorías existentes para ese grupo
            self.cursor.execute("DELETE FROM categorias_evaluacion WHERE grupo_id = ?", (grupo_id,))
            
            # 2. Insertar las nuevas categorías
            if categorias:
                query = """
                INSERT INTO categorias_evaluacion (grupo_id, nombre_categoria, peso_porcentual, max_items) 
                VALUES (?, ?, ?, ?)
                """
                # 🔴 SOLUCIÓN: Convertir lista de objetos a lista de tuplas
                params_list = []
                for c in categorias:
                    # Asumimos que CategoriaEvaluacion tiene los métodos get_x() correctos.
                    params_list.append((
                        grupo_id, 
                        c.get_nombre_categoria(), 
                        c.get_peso_porcentual(), 
                        c.get_max_items()
                    ))
                    
                self.cursor.executemany(query, params_list)
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al guardar ponderaciones: {e}")
            conn.rollback()
            return False
        finally:
            self._desconectar(conn)
            
# ====================================================
# 5. CALIFICACION DAO (CASO DE USO 5)
# ====================================================

class CalificacionDAO(BaseDAO):
    """Maneja las operaciones CRUD para las Calificaciones (CU5)."""

    def registrar_calificacion(self, calificacion: Calificacion):
        """Inserta o actualiza (REPLACE INTO) una calificación individual."""
        # Se asume que Calificacion tiene un método to_tuple() que retorna (matricula, categoria, fecha, valor)
        query = """
        REPLACE INTO calificaciones (matricula, categoria, fecha, valor) 
        VALUES (?, ?, ?, ?)
        """
        # La lógica para obtener los parámetros debe estar en el modelo Calificacion
        params = (calificacion.get_matricula(), calificacion.get_categoria(), calificacion.get_fecha() or date.today().isoformat(), calificacion.get_valor())
        return self.ejecutar_query(query, params)

    def obtener_calificaciones_por_categoria(self, grupo_id, categoria):
        """Retorna matricula, nombre y calificación más reciente para una categoría."""
        query = """
        SELECT 
            A.matricula,
            A.nombre_completo,
            T1.valor
        FROM alumnos A
        LEFT JOIN calificaciones T1 
        ON A.matricula = T1.matricula AND T1.categoria = ?
        WHERE A.grupo_id = ?
        ORDER BY A.nombre_completo;
        """
        # Nota: Esta consulta puede retornar múltiples filas si hay muchas notas por alumno. 
        # La lógica de "nota más reciente" debe estar en el Gestor o en la consulta SQL.
        # Por simplicidad, se retorna la unión y el Gestor filtra.
        return self.ejecutar_query(query, (categoria, grupo_id))
        
    def obtener_calificaciones_por_alumno_y_categoria(self, matricula: str):
        """
        Retorna todas las notas registradas para un alumno.
        Útil para el cálculo de promedio final.
        """
        query = """
        SELECT categoria, valor, fecha
        FROM calificaciones 
        WHERE matricula = ?
        ORDER BY categoria, fecha DESC;
        """
        return self.ejecutar_query(query, (matricula,))

# Datos/dao.py (Agregar al final del archivo)

# ====================================================
# 6. PROFESOR DAO (Autenticación)
# ====================================================
class ProfesorDAO(BaseDAO):
    """Maneja las operaciones CRUD para la entidad Profesor."""
    
    def crear_profesor(self, nombre, usuario, password, email=""):
        """Inserta un nuevo registro de profesor."""
        query = "INSERT INTO profesores (nombre_completo, usuario, password, email) VALUES (?, ?, ?, ?)"
        params = (nombre, usuario, password, email)
        # ejecutar_query retorna True/False para INSERTs
        return self.ejecutar_query(query, params)
    
    def buscar_profesor_por_usuario(self, usuario):
        """Busca un profesor por su nombre de usuario."""
        query = "SELECT profesor_id, nombre_completo, password, email FROM profesores WHERE usuario = ?"
        resultado = self.ejecutar_query(query, (usuario,))
        # ejecutar_query retorna una lista de tuplas (fetchall),
        # por lo que tomamos el primer elemento si existe.
        return resultado[0] if resultado else None