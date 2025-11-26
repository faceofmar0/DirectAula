from Datos.dao import AlumnoDAO, AsistenciaDAO, GrupoDAO, CategoriaEvaluacionDAO, CalificacionDAO
from model import Alumno, Asistencia, Grupo, CategoriaEvaluacion, Calificacion
from datetime import date 

# ====================================================
# 1. GESTOR GRUPOS (CU-1) - Sin cambios
# ====================================================

class GestorGrupos:
    """Gestiona el flujo y aplica las reglas de negocio para Grupos."""

    def __init__(self):
        self._grupo_dao = GrupoDAO()
        self._alumno_dao = AlumnoDAO() # Necesario para BR.2

    def obtener_lista_grupos(self):
        """Retorna la lista de grupos (R)."""
        return self._grupo_dao.obtener_grupos()

    def agregar_nuevo_grupo(self, nombre, ciclo_escolar):
        """Implementa la lógica de Crear Grupo, valida BR.1 y AC-1."""
        nombre = nombre.strip()
        ciclo_escolar = ciclo_escolar.strip()

        if not nombre or not ciclo_escolar:
            return "Error: Nombre y Ciclo Escolar son obligatorios (AC-1)."

        # BR.1: El nombre del grupo debe ser único para ese Ciclo Escolar.
        if self._grupo_dao.buscar_grupo_por_nombre_ciclo(nombre, ciclo_escolar):
            return "Error: Ya existe un grupo con ese nombre en este Ciclo Escolar (BR.1)."

        nuevo_grupo = Grupo(None, nombre, ciclo_escolar)
        if self._grupo_dao.crear_grupo(nuevo_grupo):
            return "Éxito: Grupo registrado correctamente."
        else:
            return "Error: No se pudo guardar el grupo en la base de datos."

    def actualizar_datos_grupo(self, grupo_id, nombre, ciclo_escolar):
        """Implementa la lógica de Editar Grupo, valida BR.1."""
        nombre = nombre.strip()
        ciclo_escolar = ciclo_escolar.strip()

        # BR.1 (Revisar si otro grupo ya tiene esa combinación nombre/ciclo)
        id_existente = self._grupo_dao.buscar_grupo_por_nombre_ciclo(nombre, ciclo_escolar)
        if id_existente and id_existente != grupo_id:
            return "Error: Otro grupo ya usa ese nombre y ciclo escolar (BR.1)."

        grupo_a_actualizar = Grupo(grupo_id, nombre, ciclo_escolar)
        if self._grupo_dao.actualizar_grupo(grupo_a_actualizar):
            return "Éxito: Grupo actualizado correctamente."
        else:
            return "Error: No se pudo actualizar el grupo."

    def eliminar_grupo(self, grupo_id):
        """Implementa la lógica para eliminar un grupo, valida BR.2."""
        # BR.2: Un grupo no puede ser eliminado si tiene alumnos registrados
        if self._alumno_dao.obtener_alumnos_por_grupo(grupo_id):
            return "Error: No se puede eliminar el grupo porque tiene alumnos registrados (BR.2)."
        
        if self._grupo_dao.eliminar_grupo(grupo_id):
            return "Éxito: Grupo eliminado."
        else:
            return "Error: No se pudo eliminar el grupo."

# ====================================================
# 2. GESTOR ALUMNOS (CU-2) - Sin cambios
# ====================================================
class GestorAlumnos:
    """Gestiona el flujo y aplica las reglas de negocio para Alumnos."""

    def __init__(self, grupo_actual_id):
        self._alumno_dao = AlumnoDAO() 
        self._grupo_actual_id = grupo_actual_id

    def _existe_matricula_en_grupo(self, matricula):
        """Verifica si la matrícula existe en el grupo (FE.2)."""
        alumnos_grupo = self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
        # Esto es eficiente, ya que la validación se hace en la base de datos (dao.py)
        # Aquí solo filtramos si la matrícula existe en el resultado.
        return any(a[0] == matricula for a in alumnos_grupo)

    def agregar_nuevo_alumno(self, matricula, nombre, contacto, email):
        """Implementa la lógica del FA.1: Agregar nuevo alumno."""
        
        if not matricula or not nombre:
            return "Error: Matrícula y Nombre son obligatorios (BR.4 - FE.1)."
        
        if self._existe_matricula_en_grupo(matricula):
            return f"Error: La matrícula {matricula} ya existe en este grupo (FE.2)."

        nuevo_alumno = Alumno(matricula, nombre, contacto, email) 

        if self._alumno_dao.crear_alumno(nuevo_alumno, self._grupo_actual_id):
            return "Éxito: Alumno registrado correctamente."
        else:
            return "Error: No se pudo guardar en la base de datos."

    def obtener_lista_alumnos(self):
        """Retorna la lista de alumnos del grupo (R)."""
        return self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
    
    def actualizar_datos_alumno(self, matricula, nombre, contacto, email):
        """Implementa la lógica del FA.2: Modificar datos de un alumno."""
        
        if not matricula or not nombre:
            return "Error: Nombre es obligatorio para la actualización (BR.4 - FE.1)."
        
        alumno_a_actualizar = Alumno(matricula, nombre, contacto, email)
        
        if self._alumno_dao.actualizar_alumno(alumno_a_actualizar):
            return "Éxito: Datos del alumno actualizados correctamente."
        else:
            return "Error: No se pudo actualizar el alumno."

    def eliminar_alumno(self, matricula):
        """Implementa la lógica para eliminar un alumno (BR.6)."""
        # BR.6 implica la eliminación, asumiendo que las referencias a asistencia/calificaciones
        # también se eliminarán o se manejarán con integridad referencial.
        if self._alumno_dao.eliminar_alumno(matricula):
            return "Éxito: Alumno eliminado permanentemente (BR.6)."
        else:
            return "Error: No se pudo eliminar el alumno."

# ====================================================
# 3. GESTOR ASISTENCIA (CU-4) - Sin cambios relevantes
# ====================================================
class GestorAsistencia:
    """Gestiona el flujo de registro de asistencia."""

    def __init__(self, grupo_actual_id):
        self._asistencia_dao = AsistenciaDAO()
        self._alumno_dao = AlumnoDAO() 
        self._grupo_actual_id = grupo_actual_id

    def registrar_asistencia_masiva(self, fecha=date.today().strftime("%Y-%m-%d")):
        """Implementa la lógica de 'poner asistencia a todos'."""
        alumnos_data = self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
        matriculas = [a[0] for a in alumnos_data] 
        registros_exitosos = 0
        
        for matricula in matriculas:
            # BR.11: La asistencia se registra como Asistencia por defecto
            asistencia = Asistencia(matricula, fecha, "Asistencia") 
            if self._asistencia_dao.registrar_asistencia(asistencia):
                registros_exitosos += 1
                
        if len(matriculas) == 0:
            return "Advertencia: No hay alumnos en este grupo."
        elif registros_exitosos > 0:
            return "Éxito: Asistencia masiva registrada."
        else:
            return "Error: No se pudo registrar la asistencia."

    def actualizar_estado_asistencia(self, matricula, fecha, nuevo_estado):
        """Actualiza el estado de un solo alumno (para cambiar a Ausente/Retardo)."""
        # BR.11: Estado debe ser uno de los posibles valores
        if nuevo_estado not in ["Asistencia", "Ausente", "Retardo", "Justificado"]:
            return "Error: Estado de asistencia inválido."
        
        asistencia = Asistencia(matricula, fecha, nuevo_estado)
        if self._asistencia_dao.registrar_asistencia(asistencia):
            return "Éxito: Estado de asistencia actualizado."
        else:
            return "Error: No se pudo actualizar el estado en la base de datos."

    def obtener_asistencia_para_ui(self, fecha=date.today().strftime("%Y-%m-%d")):
        """Retorna la lista de asistencia del día para la UI (R)."""
        return self._asistencia_dao.obtener_asistencia_del_dia(fecha, self._grupo_actual_id)

# ====================================================
# 4. GESTOR CALIFICACIONES (CASO DE USO 3, 5 y 6)
# ====================================================
class GestorCalificaciones:
    def __init__(self, grupo_id):
        self._grupo_actual_id = grupo_id
        self._categoria_dao = CategoriaEvaluacionDAO() 
        self._calificacion_dao = CalificacionDAO()
        # 💡 AGREGADOS para CU6: Promedio Final y Riesgo (BR.12)
        self._alumno_dao = AlumnoDAO()
        self._asistencia_dao = AsistenciaDAO()
        
        # Aseguramos la ponderación inicial (BR.3)
        self._categoria_dao.crear_ponderacion_inicial(grupo_id)

    # --- CU3: Ponderación Flexible ---
    
    def obtener_categorias_evaluacion(self):
        """Obtiene la lista de objetos CategoriaEvaluacion para el grupo actual."""
        return self._categoria_dao.obtener_categorias_por_grupo(self._grupo_actual_id)
        
    def guardar_categorias_evaluacion(self, categorias_data: list[tuple]):
        """
        Recibe una lista de tuplas: [(nombre, peso, max_items), ...]
        y valida que la suma sea 100%. (BR.10)
        """
        # Validar la suma de pesos (FE.1)
        try:
            total_peso = sum([float(peso) for _, peso, _ in categorias_data])
        except (TypeError, ValueError):
            return "Error: Los pesos porcentuales deben ser numéricos."
            
        if round(total_peso) != 100:
            return f"Error: La suma de las ponderaciones debe ser 100%, la suma actual es {total_peso:.1f}%."
        
        # Crear objetos del modelo
        lista_modelos = []
        for nombre, peso, max_items in categorias_data:
            lista_modelos.append(
                CategoriaEvaluacion(self._grupo_actual_id, nombre, float(peso), int(max_items))
            )
        
        # Guardar en la base de datos (Usa el método corregido del DAO)
        try:
            # ✅ CORRECCIÓN: Llamada directa al método guardando el orden (lista_modelos, grupo_id)
            if self._categoria_dao.guardar_ponderaciones(lista_modelos, self._grupo_actual_id):
                # 6. Guarda la estructura y recalcula todos los promedios (BR.14)
                self._recalcular_promedios()
                return "Éxito: Estructura de evaluación guardada y promedios recalculados exitosamente."
            else:
                return "Error: El DAO retornó un fallo al guardar la estructura de evaluación."
        except Exception as e:
            # Este error puede ser por fallo de DB o fallo en el DAO que no se capturó
            return f"Error crítico al intentar guardar ponderaciones: {e}"

    # --- Lógica de Recálculo y Promedio (CU6) ---

    def _recalcular_promedios(self):
        """Calcula el promedio final de CADA alumno en el grupo usando la ponderación dinámica."""
        alumnos_data = self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
        categorias = self.obtener_categorias_evaluacion()
        
        for matricula, _, _, _ in alumnos_data: 
            # Recalcula el promedio de cada alumno. Aunque no lo guardemos, asegura la lógica.
            self._calcular_promedio_alumno_ponderado(matricula, categorias) 
            
        print(f"Recalculo de promedios finalizado para grupo {self._grupo_actual_id}.")
        return True

    def _calcular_promedio_alumno_ponderado(self, matricula, ponderaciones):
        """Calcula el promedio ponderado de un alumno dado usando las ponderaciones actuales (BR.14)."""
        # Obtener todas las calificaciones del alumno (categoría, valor, fecha)
        calificaciones_alumno = self._calificacion_dao.obtener_calificaciones_por_alumno_y_categoria(matricula)
        
        # Reestructurar calificaciones por categoría para fácil acceso
        notas_por_categoria = {}
        for categoria, valor, _ in calificaciones_alumno:
            if categoria not in notas_por_categoria:
                notas_por_categoria[categoria] = []
            notas_por_categoria[categoria].append(valor)

        suma_ponderada = 0.0
        peso_total_valido = 0.0
        
        for categoria in ponderaciones:
            nombre_cat = categoria.get_nombre_categoria()
            peso_cat = categoria.get_peso_porcentual()
            max_items = categoria.get_max_items()
            
            notas_categoria = notas_por_categoria.get(nombre_cat)
            
            if notas_categoria:
                # Tomar solo las mejores 'max_items' calificaciones
                notas_categoria.sort(reverse=True)
                notas_seleccionadas = notas_categoria[:max_items]
                
                # BR.14: Calcular promedio de la categoría
                promedio_categoria = sum(notas_seleccionadas) / len(notas_seleccionadas)
                
                suma_ponderada += promedio_categoria * (peso_cat / 100.0)
                peso_total_valido += peso_cat # Suma el peso solo si hay al menos una nota registrada en la categoría
                
        if peso_total_valido == 0:
            return 0.0
        
        # Normalizar el promedio por la suma de los pesos que realmente se utilizaron (BR.14)
        return suma_ponderada / (peso_total_valido / 100.0)
        
    def calcular_promedios_y_estado_final(self):
        """
        Calcula el promedio final ponderado (BR.14) y el estado de riesgo (BR.12)
        para todos los alumnos del grupo (CU6).
        Retorna: [(matricula, nombre, promedio, asistencia, estado_riesgo), ...]
        """
        alumnos = self._alumno_dao.obtener_alumnos_por_grupo(self._grupo_actual_id)
        ponderaciones = self._categoria_dao.obtener_categorias_por_grupo(self._grupo_actual_id)
        
        resultados_finales = []
        
        for matricula, nombre, _, _ in alumnos:
            # 1. Calcular promedio ponderado (BR.14)
            promedio = self._calcular_promedio_alumno_ponderado(matricula, ponderaciones) 
            
            # 2. Obtener porcentaje de asistencia
            porcentaje_asistencia = self._asistencia_dao.obtener_porcentaje_asistencia_por_alumno(matricula)
            
            # 3. Determinar estado de riesgo (BR.12) y redondear (BR.17)
            # BR.17: Redondeo a 2 decimales
            promedio_redondeado = round(promedio, 2)
            porcentaje_asistencia_redondeado = round(porcentaje_asistencia, 2)
            
            estado_riesgo = "Normal"
            
            # BR.12: Riesgo Académico < 7.0
            if promedio_redondeado < 7.0:
                estado_riesgo = "Riesgo Académico"
            
            # BR.12: Riesgo Asistencia < 80.0
            if porcentaje_asistencia_redondeado < 80.0:
                if estado_riesgo == "Riesgo Académico":
                    estado_riesgo = "Riesgo Académico y Asistencia"
                else:
                    estado_riesgo = "Riesgo Asistencia"
                    
            resultados_finales.append((
                matricula, 
                nombre, 
                promedio_redondeado, 
                porcentaje_asistencia_redondeado, 
                estado_riesgo
            ))
            
        return resultados_finales

    # --- CU5: Registro de Calificaciones ---
    
    def obtener_alumnos_con_calificaciones(self, categoria):
        """Retorna alumnos con su calificación más reciente para una categoría."""
        # Retorna: [(matricula, nombre, valor), ...]
        return self._calificacion_dao.obtener_calificaciones_por_categoria(self._grupo_actual_id, categoria)

    def registrar_calificacion(self, matricula, categoria, valor):
        # FE.1: Validación de rangos (BR.13)
        try:
            valor_num = float(valor)
        except (TypeError, ValueError):
            return "Error: La calificación debe ser un valor numérico."
        
        if not (0.0 <= valor_num <= 10.0):
            return "Error: La calificación debe estar entre 0 y 10 (BR.13)."

        # Construir el modelo de calificación
        nueva_calificacion = Calificacion(matricula, categoria, valor_num)

        # ✅ CORRECCIÓN: Llamada directa al método único del DAO
        try:
            saved = self._calificacion_dao.registrar_calificacion(nueva_calificacion)
        except Exception as e:
            print(f"Error al registrar calificación: {e}")
            saved = False

        if saved:
            # Recalcular promedios para actualizar estado de riesgo (BR.15)
            try:
                self._recalcular_promedios()
            except Exception as e:
                # Silenciar errores de recálculo para no bloquear el guardado, pero se loggea
                print(f"Advertencia: Fallo en el recálculo de promedios post-guardado: {e}")
                pass
            return "Éxito: Calificación registrada."
        else:
            return "Error: No se pudo registrar la calificación."