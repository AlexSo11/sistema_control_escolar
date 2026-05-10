"""
Interfaz de Gestión de Salones
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBSalon:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_salon(self, numero: str, capacidad: int, ubicacion: str) -> Tuple[bool, str]:
        """Crea un nuevo salón en la base de datos"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO salon (numero, capacidad, ubicacion) VALUES (%s, %s, %s)"
            cursor.execute(sql, (numero, capacidad, ubicacion))
            conn.commit()
            return True, "Salón creado correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear salón: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_salon(self, salon_id: int, numero: str, capacidad: int, ubicacion: str) -> Tuple[bool, str]:
        """Actualiza un salón existente"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE salon 
                SET numero = %s, capacidad = %s, ubicacion = %s
                WHERE id = %s
            """
            cursor.execute(sql, (numero, capacidad, ubicacion, salon_id))
            conn.commit()
            return True, "Salón actualizado correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar salón: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_salon(self, salon_id: int) -> Tuple[bool, str]:
        """Elimina un salón"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM salon WHERE id = %s", (salon_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Salón eliminado correctamente"
            else:
                return False, "Salón no encontrado"
                
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1451: # Error de llave foránea
                return False, "Error: No se puede eliminar el salón, está asignado a un grupo."
            return False, f"Error al eliminar salón: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_salones(self) -> List[Dict[str, Any]]:
        """Lista todos los salones"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, numero, capacidad, ubicacion FROM salon ORDER BY numero")
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al listar salones: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_salon_por_numero(self, numero: str) -> List[Dict[str, Any]]:
        """Busca salones por su número (usando LIKE)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, numero, capacidad, ubicacion FROM salon WHERE numero LIKE %s"
            cursor.execute(sql, (f"%{numero}%",))
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al buscar salón: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_numero_unico(self, numero: str, salon_id: Optional[int] = None) -> bool:
        """Verifica que el número del salón sea único"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        
        cursor = None
        try:
            cursor = conn.cursor()
            if salon_id: # Al actualizar
                cursor.execute("SELECT id FROM salon WHERE numero = %s AND id != %s", (numero, salon_id))
            else: # Al crear
                cursor.execute("SELECT id FROM salon WHERE numero = %s", (numero,))
            return cursor.fetchone() is None
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()