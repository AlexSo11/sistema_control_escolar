"""
Interfaz de Gestión de Carreras
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBCarrera:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_carrera(self, nombre: str, descripcion: str) -> Tuple[bool, str]:
        """Crea una nueva carrera en la base de datos"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO carrera (nombre, descripcion) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, descripcion))
            conn.commit()
            return True, "Carrera creada correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear carrera: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_carrera(self, carrera_id: int, nombre: str, descripcion: str) -> Tuple[bool, str]:
        """Actualiza una carrera existente"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE carrera 
                SET nombre = %s, descripcion = %s
                WHERE id = %s
            """
            cursor.execute(sql, (nombre, descripcion, carrera_id))
            conn.commit()
            return True, "Carrera actualizada correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar carrera: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_carrera(self, carrera_id: int) -> Tuple[bool, str]:
        """Elimina una carrera"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrera WHERE id = %s", (carrera_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Carrera eliminada correctamente"
            else:
                return False, "Carrera no encontrada"
                
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1451: # Error de llave foránea
                return False, "Error: No se puede eliminar la carrera, está asignada a materias o alumnos."
            return False, f"Error al eliminar carrera: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_carreras(self) -> List[Dict[str, Any]]:
        """Lista todas las carreras"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, descripcion FROM carrera ORDER BY nombre")
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al listar carreras: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_carrera_por_nombre(self, nombre: str) -> List[Dict[str, Any]]:
        """Busca carreras por su nombre (usando LIKE)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            # Usamos LIKE para que la búsqueda sea flexible
            sql = "SELECT id, nombre, descripcion FROM carrera WHERE nombre LIKE %s"
            cursor.execute(sql, (f"%{nombre}%",))
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al buscar carrera: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_nombre_unico(self, nombre: str, carrera_id: Optional[int] = None) -> bool:
        """Verifica que el nombre de la carrera sea único"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        
        cursor = None
        try:
            cursor = conn.cursor()
            if carrera_id: # Al actualizar
                cursor.execute("SELECT id FROM carrera WHERE nombre = %s AND id != %s", (nombre, carrera_id))
            else: # Al crear
                cursor.execute("SELECT id FROM carrera WHERE nombre = %s", (nombre,))
            return cursor.fetchone() is None
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()