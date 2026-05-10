"""
Interfaz de Gestión de Planeaciones
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBPlaneacion:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_planeacion(self, descripcion: str, generado_por_id: int, archivo: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                INSERT INTO planeacion (descripcion, generado_por, archivo_referencia) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (descripcion, generado_por_id, archivo))
            conn.commit()
            return True, "Planeación creada correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear planeación: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_planeacion(self, plan_id: int, descripcion: str, archivo: str) -> Tuple[bool, str]:
        """Actualiza una planeación existente"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE planeacion 
                SET descripcion = %s, archivo_referencia = %s
                WHERE id = %s
            """
            cursor.execute(sql, (descripcion, archivo, plan_id))
            conn.commit()
            return True, "Planeación actualizada correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar planeación: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_planeacion(self, plan_id: int) -> Tuple[bool, str]:
        """Elimina un registro de planeación"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM planeacion WHERE id = %s", (plan_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Planeación eliminada correctamente"
            else:
                return False, "Planeación no encontrada"
                
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al eliminar planeación: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_planeaciones(self) -> List[Dict[str, Any]]:
        """Lista todas las planeaciones, uniendo con el usuario que la generó"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    p.id, 
                    p.descripcion, 
                    p.fecha_generacion, 
                    p.archivo_referencia,
                    u.nombre, 
                    u.apellido_paterno
                FROM planeacion p
                LEFT JOIN usuario u ON p.generado_por = u.id
                ORDER BY p.fecha_generacion DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al listar planeaciones: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_planeacion_por_id(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Busca una planeación por su ID"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    p.id, 
                    p.descripcion, 
                    p.fecha_generacion, 
                    p.archivo_referencia,
                    u.nombre, 
                    u.apellido_paterno
                FROM planeacion p
                LEFT JOIN usuario u ON p.generado_por = u.id
                WHERE p.id = %s
            """
            cursor.execute(sql, (plan_id,))
            result = cursor.fetchone()
            return result if result else None # type: ignore
        except Error as e:
            print(f"Error al buscar planeación: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()