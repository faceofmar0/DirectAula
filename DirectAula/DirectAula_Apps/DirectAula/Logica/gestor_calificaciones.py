#Logica/gestor_calificaciones.py
from Datos.dao import AsistenciaDAO, CategoriaEvaluacionDAO, CalificacionDAO, AlumnoDAO # Asegúrate de importar AlumnoDAO si está en dao.py
from model import Calificacion, CategoriaEvaluacion # Asegúrate de importar los modelos
from datetime import date

class GestorCalificaciones:
    """Gestiona el flujo de administración de categorías (CU3) y calificaciones (CU5)."""

    def __init__(self, grupo_id :int):
        self._grupo_actual_id = grupo_id
        self._calificacion_dao = CalificacionDAO() 
        self._ponderacion_dao = CategoriaEvaluacionDAO() 
        self._alumno_dao = AlumnoDAO() # Necesario para obtener alumnos y sus matrículas
        self._asistencia_dao = AsistenciaDAO()
        self._ponderacion_dao.crear_ponderacion_inicial(grupo_id) # Asegura ponderación inicial
    # ===============================================
    # LÓGICA CU3: ADMINISTRAR PONDERACIONES
    # ===============================================
    def obtener_categorias(self):
        """Recupera la lista de categorías del grupo actual."""
        return self._ponderacion_dao.obtener_categorias_por_grupo(self._grupo_actual_id)

    def guardar_ponderaciones(self, categorias: list[CategoriaEvaluacion]):
        """
        Guarda las categorías tras validar las Reglas de Negocio.
        Implementa BR.4 (Suma 100%) y BR.5 (Al menos una categoría).
        """
        # BR.5: Debe haber al menos una categoría
        if not categorias:
            return "Error: Debe definir al menos una categoría de evaluación (BR.5)."

        # BR.4: La suma de los pesos debe ser 100.0 (con un pequeño margen de tolerancia)
        suma_pesos = sum(c.get_peso_porcentual() for c in categorias)
        if abs(suma_pesos - 100.0) > 0.01:
            return f"Error: La suma de los pesos porcentuales debe ser 100%. Suma actual: {suma_pesos:.2f}% ."
        for categoria in categorias:
            pass 

        if self._ponderacion_dao.guardar_ponderaciones(self._grupo_actual_id, categorias):
            return "Éxito: Ponderaciones guardadas correctamente."
        else:
            return "Error: No se pudieron guardar las ponderaciones en la base de datos."
    # ===============================================
    # LÓGICA CU5: REGISTRAR CALIFICACIONES
    # ===============================================
    def obtener_calificaciones_por_categoria(self, categoria_nombre):
        """Prepara los datos para la VentanaCalificaciones."""
        return self._calificacion_dao.obtener_calificaciones_por_categoria(
            self._grupo_actual_id, categoria_nombre
        )

    def registrar_calificacion(self, matricula, categoria, valor, fecha=None):
        """
        Registra una calificación individual.
        Implementa BR.13 (Valor entre 0-10).
        """
        try:
            valor = float(valor)
        except ValueError:
            return "Error: La calificación debe ser un valor numérico."

        # BR.13: Todas las calificaciones deben ser numéricas y estar dentro de la escala (0-10)
        if not (0.0 <= valor <= 10.0):
            return "Error: La calificación debe estar entre 0.0 y 10.0 (BR.13)."

        # Usar la fecha de hoy si no se proporciona
        fecha_registro = fecha if fecha is not None else date.today().isoformat()

        nueva_calificacion = Calificacion(matricula, categoria, valor, fecha_registro)

        if self._calificacion_dao.registrar_calificacion(nueva_calificacion):
            # self._recalcular_promedios() # Si la UI necesita el promedio al instante
            return "Éxito: Calificación registrada."
        else:
            return "Error: No se pudo registrar la calificación."
    # ===============================================
    # LÓGICA BR.14/BR.15: CÁLCULO DE PROMEDIOS
    # ===============================================
    def calcular_promedio_final(self, matricula):
        """
        Calcula el promedio final de un alumno utilizando la ponderación actual (BR.14).
        Retorna el promedio ponderado o -1.0 si no hay datos.
        """
        categorias = self.obtener_categorias()
        if not categorias:
            return 0.0 
        # 1. Obtener todas las calificaciones del alumno para cada categoría
        promedio_ponderado = 0.0
        peso_total_valido = 0.0
        for categoria in categorias:
            # Obtener todas las calificaciones del alumno en esta categoría
            # Idealmente, necesitas un método en DAO para obtener TODAS las notas de un alumno/categoría
            # para calcular el promedio simple de esa categoría y luego el ponderado.
            
            # **NOTA DE IMPLEMENTACIÓN:** El DAO anterior no soporta esto directamente.
            # Se asume que en el modelo actual, cada categoría solo tiene UNA nota (la más reciente)
            # Si usas la tabla de calificaciones, la lógica es:
            
            # 1. Obtener todas las notas del alumno para esta categoría.
            # 2. Calcular el promedio simple de la categoría.
            # 3. Aplicar el peso ponderado.
            
            # Por simplicidad, y basándome en el diseño de tu tabla, si se ingresa
            # una nota individual, se puede asumir que es la nota final para esa categoría.
            
            # --- Lógica simple (Asumiendo 1 nota final por Categoría) ---
            
            # **Necesitarías una función en CalificacionDAO:**
            # def obtener_nota_final_por_categoria(self, matricula, categoria) -> float:
            #     # Query que obtenga la nota más reciente/final.
            #     pass 
            
            # **Alternativa (solo para demostración de cálculo):**
            # Simulamos obtener la nota (ej. 8.5)
            # Esto debe ser implementado con la BD correctamente.
            
            # Simulación: Si la nota está en la BD, se usa. Si no, es 0.
            # nota_categoria = self._calificacion_dao.obtener_nota_final_por_categoria(matricula, categoria.get_nombre_categoria())
            
            # Como no tengo el método completo, asumo que solo se usa la nota
            # si el alumno tiene un registro para esa categoría.

            # EJEMPLO DE CÓMO SE VERÍA LA LÓGICA DE CÁLCULO BR.14:
            nota_categoria = 0.0 # Asume que 0 es la nota por defecto si no hay registro
            # Llama a un método DAO para obtener la nota final
            # nota_final = self._calificacion_dao.obtener_nota_final(matricula, categoria.get_nombre_categoria())
            # if nota_final is not None:
            #     nota_categoria = nota_final
            
            # if nota_categoria > 0.0: # Si hay una nota registrada para esta categoría
            promedio_ponderado += (nota_categoria * categoria.get_peso_porcentual())
            peso_total_valido += categoria.get_peso_porcentual()
        
        # El promedio es la suma de los productos (Nota * Peso) / 100.
        # Esto es si la suma total de los pesos es 100 (BR.4).
        # Para el cálculo, no es necesario dividir por 100 si la suma es 100.
        
        return promedio_ponderado / 100.0 # BR.17: Redondeo a 2 decimales se hace en la UI o al exportar.

    # --- Función que junta todo para el reporte/vista final ---
    
    def obtener_resumen_calificaciones_grupo(self):
        """
        Obtiene un resumen completo de calificaciones de todos los alumnos 
        con su promedio final para el grupo actual.
        """
        alumnos = self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
        categorias = self.obtener_categorias()
        
        datos_grupo = []
        for alumno in alumnos:
            matricula = alumno.get_matricula()
            nombre = alumno.get_nombre_completo()
            
            registro = {
                'matricula': matricula,
                'nombre_completo': nombre,
                # Promedio final (BR.14)
                'promedio_final': self.calcular_promedio_final(matricula) 
            }
            
            # Agregar la nota individual por cada categoría
            for categoria in categorias:
                # registro[categoria.get_nombre_categoria()] = self._calificacion_dao.obtener_nota_final(matricula, categoria.get_nombre_categoria())
                pass 
                
            datos_grupo.append(registro)
            
        return datos_grupo, categorias