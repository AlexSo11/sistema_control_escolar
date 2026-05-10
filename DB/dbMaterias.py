"""
Módulo de Gestión de Materias - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBMateria:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def get_carreras(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de carreras para el combobox"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM carrera ORDER BY nombre")
            carreras = cursor.fetchall()
            return list(carreras) if carreras else [] # type: ignore
        except Error as e:
            print(f"Error al obtener carreras: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def crear_materia(self, codigo: str, nombre: str, creditos: int, carrera_id: Optional[int]) -> Tuple[bool, str]:
        """Crea una nueva materia en la base de datos"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO materia (codigo, nombre, creditos, carrera_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (codigo, nombre, creditos, carrera_id))
            conn.commit()
            return True, "Materia creada correctamente"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear materia: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_materia(self, materia_id: int, codigo: str, nombre: str, creditos: int, carrera_id: Optional[int]) -> Tuple[bool, str]:
        """Actualiza una materia existente"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE materia 
                SET codigo = %s, nombre = %s, creditos = %s, carrera_id = %s
                WHERE id = %s
            """
            cursor.execute(sql, (codigo, nombre, creditos, carrera_id, materia_id))
            conn.commit()
            return True, "Materia actualizada correctamente"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar materia: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_materia(self, materia_id: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materia WHERE id = %s", (materia_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Materia eliminada correctamente"
            else:
                return False, "Materia no encontrada"
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1451:
                return False, "Error: No se puede eliminar la materia porque ya está asignada."
            return False, f"Error al eliminar materia: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_materias(self) -> List[Dict[str, Any]]:
        """Lista todas las materias, uniendo con carrera"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT m.id, m.codigo, m.nombre, m.creditos, c.nombre as carrera_nombre
                FROM materia m
                LEFT JOIN carrera c ON m.carrera_id = c.id
                ORDER BY m.nombre
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else [] # type: ignore
        except Error as e:
            print(f"Error al listar materias: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_materia_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca una materia por su código, uniendo con carrera"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT m.id, m.codigo, m.nombre, m.creditos, m.carrera_id, c.nombre as carrera_nombre
                FROM materia m
                LEFT JOIN carrera c ON m.carrera_id = c.id
                WHERE m.codigo = %s
            """
            cursor.execute(sql, (codigo,))
            result = cursor.fetchone()
            return result if result else None # type: ignore
        except Error as e:
            print(f"Error al buscar materia: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_codigo_unico(self, codigo: str, materia_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if materia_id:
                cursor.execute("SELECT id FROM materia WHERE codigo = %s AND id != %s", (codigo, materia_id))
            else:
                cursor.execute("SELECT id FROM materia WHERE codigo = %s", (codigo,))
            return cursor.fetchone() is None
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()