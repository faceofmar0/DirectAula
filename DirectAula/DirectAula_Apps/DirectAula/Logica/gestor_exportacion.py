#logica/gestor_expotacion.py
import pandas as pd
import sqlite3
from datetime import datetime
import os

class GestorExportaciones:
    """Gestiona la exportación de datos a Excel para todos los módulos."""
    
    def __init__(self, db_file='directaula.db'):
        self._db_file = db_file
    
    def exportar_grupo_completo(self, grupo_id, nombre_grupo, directorio_destino=None):
        """
        Exporta todos los datos de un grupo a un archivo Excel con múltiples hojas.
        Retorna: (éxito, mensaje, ruta_archivo)
        """
        try:
            # Crear nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"DirectAula_{nombre_grupo.replace(' ', '_')}_{timestamp}.xlsx"
            
            if directorio_destino:
                ruta_completa = os.path.join(directorio_destino, nombre_archivo)
            else:
                ruta_completa = nombre_archivo
            
            # Crear ExcelWriter
            with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
                # 1. Hoja: Información del Grupo
                self._exportar_info_grupo(writer, grupo_id, nombre_grupo)
                
                # 2. Hoja: Lista de Alumnos
                self._exportar_alumnos(writer, grupo_id)
                
                # 3. Hoja: Asistencia Resumen
                self._exportar_asistencia_resumen(writer, grupo_id)
                
                # 4. Hoja: Calificaciones por Categoría
                self._exportar_calificaciones_categorias(writer, grupo_id)
                
                # 5. Hoja: Resultados Finales
                self._exportar_resultados_finales(writer, grupo_id)
                
                # 6. Hoja: Asistencia Detallada
                self._exportar_asistencia_detallada(writer, grupo_id)
                
                # 7. Hoja: Calificaciones Detalladas
                self._exportar_calificaciones_detalladas(writer, grupo_id)
            
            return True, f"Archivo exportado exitosamente: {nombre_archivo}", ruta_completa
            
        except Exception as e:
            return False, f"Error al exportar: {str(e)}", None
    
    def _exportar_info_grupo(self, writer, grupo_id, nombre_grupo):
        """Exporta información básica del grupo."""
        try:
            conn = sqlite3.connect(self._db_file)
            
            # Obtener información del grupo
            query_grupo = "SELECT nombre, ciclo_escolar FROM grupos WHERE grupo_id = ?"
            grupo_data = pd.read_sql_query(query_grupo, conn, params=(grupo_id,))
            
            # Contar alumnos
            query_alumnos = "SELECT COUNT(*) as total FROM alumnos WHERE grupo_id = ?"
            total_alumnos = pd.read_sql_query(query_alumnos, conn, params=(grupo_id,)).iloc[0]['total']
            
            # Crear DataFrame con información
            info_data = {
                'Campo': ['Nombre del Grupo', 'Ciclo Escolar', 'Fecha de Exportación', 'Total de Alumnos'],
                'Valor': [
                    nombre_grupo,
                    grupo_data.iloc[0]['ciclo_escolar'] if not grupo_data.empty else 'N/A',
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    total_alumnos
                ]
            }
            
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='Información del Grupo', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Información del Grupo']
            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 30
            
        except Exception as e:
            print(f"Error en info grupo: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_alumnos(self, writer, grupo_id):
        """Exporta la lista completa de alumnos."""
        try:
            conn = sqlite3.connect(self._db_file)
            query = """
            SELECT matricula, nombre_completo, datos_contacto, email 
            FROM alumnos 
            WHERE grupo_id = ? 
            ORDER BY nombre_completo
            """
            df_alumnos = pd.read_sql_query(query, conn, params=(grupo_id,))
            
            if not df_alumnos.empty:
                df_alumnos.to_excel(writer, sheet_name='Lista de Alumnos', index=False)
                
                # Ajustar formatos
                worksheet = writer.sheets['Lista de Alumnos']
                worksheet.column_dimensions['A'].width = 15  # Matrícula
                worksheet.column_dimensions['B'].width = 30  # Nombre
                worksheet.column_dimensions['C'].width = 20  # Contacto
                worksheet.column_dimensions['D'].width = 25  # Email
                
        except Exception as e:
            print(f"Error en alumnos: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_asistencia_resumen(self, writer, grupo_id):
        """Exporta resumen de asistencia por alumno."""
        try:
            conn = sqlite3.connect(self._db_file)
            query = """
            SELECT 
                a.matricula,
                a.nombre_completo,
                COUNT(CASE WHEN s.estado IN ('Presente', 'Asistencia', 'Justificado') THEN 1 END) as dias_asistidos,
                COUNT(CASE WHEN s.estado = 'Ausente' THEN 1 END) as dias_ausente,
                COUNT(CASE WHEN s.estado = 'Retardo' THEN 1 END) as dias_retardo,
                COUNT(CASE WHEN s.estado = 'Justificado' THEN 1 END) as dias_justificado,
                COUNT(s.estado) as total_registros,
                ROUND(
                    (COUNT(CASE WHEN s.estado IN ('Presente', 'Asistencia', 'Justificado') THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(s.estado), 0)), 2
                ) as porcentaje_asistencia
            FROM alumnos a
            LEFT JOIN asistencia s ON a.matricula = s.matricula
            WHERE a.grupo_id = ?
            GROUP BY a.matricula, a.nombre_completo
            ORDER BY a.nombre_completo
            """
            df_asistencia = pd.read_sql_query(query, conn, params=(grupo_id,))
            
            if not df_asistencia.empty:
                df_asistencia.to_excel(writer, sheet_name='Asistencia Resumen', index=False)
                
                worksheet = writer.sheets['Asistencia Resumen']
                columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                widths = [15, 30, 12, 12, 12, 12, 12, 15]
                
                for col, width in zip(columns, widths):
                    worksheet.column_dimensions[col].width = width
                
        except Exception as e:
            print(f"Error en asistencia resumen: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_calificaciones_categorias(self, writer, grupo_id):
        """Exporta calificaciones organizadas por categoría."""
        try:
            conn = sqlite3.connect(self._db_file)
            
            # Obtener categorías del grupo
            query_categorias = """
            SELECT DISTINCT nombre_categoria 
            FROM categorias_evaluacion 
            WHERE grupo_id = ?
            """
            categorias_df = pd.read_sql_query(query_categorias, conn, params=(grupo_id,))
            
            if categorias_df.empty:
                # Si no hay categorías, crear una hoja vacía
                empty_df = pd.DataFrame({'Mensaje': ['No hay categorías de evaluación definidas para este grupo']})
                empty_df.to_excel(writer, sheet_name='Calificaciones', index=False)
                return
            
            # Para cada categoría, obtener calificaciones
            for _, cat_row in categorias_df.iterrows():
                categoria = cat_row['nombre_categoria']
                query_calificaciones = """
                SELECT 
                    a.matricula,
                    a.nombre_completo,
                    c.valor as calificacion,
                    c.fecha
                FROM alumnos a
                LEFT JOIN calificaciones c ON a.matricula = c.matricula AND c.categoria = ?
                WHERE a.grupo_id = ?
                ORDER BY a.nombre_completo, c.fecha DESC
                """
                df_calif = pd.read_sql_query(query_calificaciones, conn, params=(categoria, grupo_id))
                
                if not df_calif.empty:
                    # Tomar solo la calificación más reciente por alumno
                    df_calif_reciente = df_calif.drop_duplicates(subset=['matricula'], keep='first')
                    df_calif_reciente = df_calif_reciente[['matricula', 'nombre_completo', 'calificacion']]
                    df_calif_reciente.rename(columns={'calificacion': f'Calificación {categoria}'}, inplace=True)
                    
                    # Nombre de hoja limitado a 31 caracteres
                    sheet_name = categoria[:31]
                    df_calif_reciente.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    worksheet = writer.sheets[sheet_name]
                    worksheet.column_dimensions['A'].width = 15
                    worksheet.column_dimensions['B'].width = 30
                    worksheet.column_dimensions['C'].width = 15
                
        except Exception as e:
            print(f"Error en calificaciones categorías: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_resultados_finales(self, writer, grupo_id):
        """Exporta resultados finales con promedios y estados de riesgo."""
        try:
            conn = sqlite3.connect(self._db_file)
            
            # Obtener alumnos del grupo
            query_alumnos = """
            SELECT matricula, nombre_completo 
            FROM alumnos 
            WHERE grupo_id = ? 
            ORDER BY nombre_completo
            """
            alumnos_df = pd.read_sql_query(query_alumnos, conn, params=(grupo_id,))
            
            if alumnos_df.empty:
                empty_df = pd.DataFrame({'Mensaje': ['No hay alumnos en este grupo']})
                empty_df.to_excel(writer, sheet_name='Resultados Finales', index=False)
                return
            
            # Obtener porcentaje de asistencia por alumno
            query_asistencia = """
            SELECT 
                a.matricula,
                ROUND(
                    (COUNT(CASE WHEN s.estado IN ('Presente', 'Asistencia', 'Justificado') THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(s.estado), 0)), 2
                ) as porcentaje_asistencia
            FROM alumnos a
            LEFT JOIN asistencia s ON a.matricula = s.matricula
            WHERE a.grupo_id = ?
            GROUP BY a.matricula
            """
            asistencia_df = pd.read_sql_query(query_asistencia, conn, params=(grupo_id,))
            
            # Obtener promedio de calificaciones por alumno
            query_promedios = """
            SELECT 
                a.matricula,
                ROUND(AVG(c.valor), 2) as promedio_final
            FROM alumnos a
            LEFT JOIN calificaciones c ON a.matricula = c.matricula
            WHERE a.grupo_id = ?
            GROUP BY a.matricula
            """
            promedios_df = pd.read_sql_query(query_promedios, conn, params=(grupo_id,))
            
            # Combinar todos los datos
            resultados_df = alumnos_df.merge(asistencia_df, on='matricula', how='left')
            resultados_df = resultados_df.merge(promedios_df, on='matricula', how='left')
            
            # Calcular estado de riesgo
            def calcular_estado_riesgo(row):
                promedio = row['promedio_final'] if pd.notna(row['promedio_final']) else 0
                asistencia = row['porcentaje_asistencia'] if pd.notna(row['porcentaje_asistencia']) else 0
                
                if promedio < 7.0 and asistencia < 80:
                    return 'Riesgo Académico y Asistencia'
                elif promedio < 7.0:
                    return 'Riesgo Académico'
                elif asistencia < 80:
                    return 'Riesgo Asistencia'
                else:
                    return 'Normal'
            
            resultados_df['estado_riesgo'] = resultados_df.apply(calcular_estado_riesgo, axis=1)
            resultados_df['promedio_final'] = resultados_df['promedio_final'].fillna(0)
            resultados_df['porcentaje_asistencia'] = resultados_df['porcentaje_asistencia'].fillna(0)
            
            # Renombrar columnas para mejor presentación
            resultados_df.columns = ['Matrícula', 'Nombre Completo', 'Asistencia (%)', 'Promedio Final', 'Estado de Riesgo']
            
            resultados_df.to_excel(writer, sheet_name='Resultados Finales', index=False)
            
            worksheet = writer.sheets['Resultados Finales']
            columns = ['A', 'B', 'C', 'D', 'E']
            widths = [15, 30, 15, 15, 25]
            
            for col, width in zip(columns, widths):
                worksheet.column_dimensions[col].width = width
                
        except Exception as e:
            print(f"Error en resultados finales: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_asistencia_detallada(self, writer, grupo_id):
        """Exporta el registro detallado de asistencia."""
        try:
            conn = sqlite3.connect(self._db_file)
            query = """
            SELECT 
                a.matricula,
                a.nombre_completo,
                s.fecha,
                s.estado
            FROM alumnos a
            JOIN asistencia s ON a.matricula = s.matricula
            WHERE a.grupo_id = ?
            ORDER BY s.fecha DESC, a.nombre_completo
            """
            df_detalle = pd.read_sql_query(query, conn, params=(grupo_id,))
            
            if not df_detalle.empty:
                df_detalle.to_excel(writer, sheet_name='Asistencia Detallada', index=False)
                
                worksheet = writer.sheets['Asistencia Detallada']
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 12
                worksheet.column_dimensions['D'].width = 12
                
        except Exception as e:
            print(f"Error en asistencia detallada: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _exportar_calificaciones_detalladas(self, writer, grupo_id):
        """Exporta todas las calificaciones detalladas."""
        try:
            conn = sqlite3.connect(self._db_file)
            query = """
            SELECT 
                a.matricula,
                a.nombre_completo,
                c.categoria,
                c.valor as calificacion,
                c.fecha
            FROM alumnos a
            JOIN calificaciones c ON a.matricula = c.matricula
            WHERE a.grupo_id = ?
            ORDER BY a.nombre_completo, c.categoria, c.fecha DESC
            """
            df_calif_detalle = pd.read_sql_query(query, conn, params=(grupo_id,))
            
            if not df_calif_detalle.empty:
                df_calif_detalle.to_excel(writer, sheet_name='Calificaciones Detalladas', index=False)
                
                worksheet = writer.sheets['Calificaciones Detalladas']
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 20
                worksheet.column_dimensions['D'].width = 12
                worksheet.column_dimensions['E'].width = 12
                
        except Exception as e:
            print(f"Error en calificaciones detalladas: {e}")
        finally:
            if 'conn' in locals():
                conn.close()