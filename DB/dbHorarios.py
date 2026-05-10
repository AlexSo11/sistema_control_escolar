"""
Interfaz de Gestión de Horarios
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBHorario:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_horario(self, dia: str, hora_inicio: str, hora_fin: str, turno: str) -> Tuple[bool, str]:
        """Crea un nuevo horario en la base de datos"""
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO horario (dia_semana, hora_inicio, hora_fin, turno) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (dia.upper(), hora_inicio, hora_fin, turno))
            conn.commit()
            return True, "Horario creado correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear horario: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_horario(self, horario_id: int, dia: str, hora_inicio: str, hora_fin: str, turno: str) -> Tuple[bool, str]:
        """Actualiza un horario existente"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            sql = """
                UPDATE horario 
                SET dia_semana = %s, hora_inicio = %s, hora_fin = %s, turno = %s
                WHERE id = %s
            """
            cursor.execute(sql, (dia.upper(), hora_inicio, hora_fin, turno, horario_id))
            conn.commit()
            return True, "Horario actualizado correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar horario: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_horario(self, horario_id: int) -> Tuple[bool, str]:
        """Elimina un horario"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM horario WHERE id = %s", (horario_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Horario eliminado correctamente"
            else:
                return False, "Horario no encontrado"
                
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1451: 
                return False, "Error: No se puede eliminar el horario, está asignado a un grupo."
            return False, f"Error al eliminar horario: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_horarios(self) -> List[Dict[str, Any]]:
        """Lista todos los horarios"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, dia_semana, hora_inicio, hora_fin, turno FROM horario ORDER BY turno, dia_semana, hora_inicio")
            rows = cursor.fetchall()
            return list(rows) if rows else [] 
        except Error as e:
            print(f"Error al listar horarios: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_horario_por_id(self, horario_id: int) -> Optional[Dict[str, Any]]:
        """Busca un horario por su ID (la búsqueda por código no aplica aquí)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM horario WHERE id = %s", (horario_id,))
            result = cursor.fetchone()
            return result if result else None # type: ignore
        except Error as e:
            print(f"Error al buscar horario: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_horario_unico(self, dia: str, hora_inicio: str, hora_fin: str, horario_id: Optional[int] = None) -> bool:
        """Verifica que la combinación de día, hora inicio y hora fin sea única"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            sql = "SELECT id FROM horario WHERE dia_semana = %s AND hora_inicio = %s AND hora_fin = %s"
            params = [dia, hora_inicio, hora_fin]
            
            if horario_id:
                sql += " AND id != %s"
                params.append(horario_id)
                
            cursor.execute(sql, tuple(params))
            return cursor.fetchone() is None
        except Error as e:
            print(f"Error al validar horario único: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    def validar_horario_sin_traslape(self, dia, hora_inicio, hora_fin, horario_id=None):
        """Valida que no haya traslape con otros horarios del mismo día"""
        query = """
            SELECT id FROM horarios 
            WHERE dia_semana = %s 
            AND id != COALESCE(%s, 0)
            AND (
                (hora_inicio < %s AND hora_fin > %s) OR  -- Envuelve completamente
                (hora_inicio >= %s AND hora_inicio < %s) OR  -- Inicia durante
                (hora_fin > %s AND hora_fin <= %s)  -- Termina durante
            )
        """
        cursor = self.con.cursor()
        cursor.execute(query, (dia, horario_id, hora_fin, hora_inicio, 
                            hora_inicio, hora_fin, hora_inicio, hora_fin))
        result = cursor.fetchone()
        cursor.close()
        return result is None