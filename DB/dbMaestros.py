"""
Módulo de Gestión de Maestros - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error
import hashlib 

def hash_password(password: str) -> str:
    """Genera un hash SHA256 de la contraseña"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DBMaestro:
    """Clase para manejar operaciones CRUD de maestros en la base de datos"""
    
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_maestro_completo(self, email: str, password: str, nombre: str,
                               apellido_paterno: str, apellido_materno: str,
                               telefono: str, numero_empleado: str, 
                               especialidad: str) -> Tuple[bool, str]:
        """
        Crea un registro en 'usuario' y 'maestro' dentro de una transacción.
        """
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            
            pw_hash = hash_password(password) 
            sql_usuario = """
                INSERT INTO usuario (email, password_hash, rol, nombre, 
                                     apellido_paterno, apellido_materno, telefono) 
                VALUES (%s, %s, 'MAESTRO', %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (email, pw_hash, nombre, 
                                          apellido_paterno, apellido_materno, telefono))
            
            # Obtener el ID del usuario recién creado
            usuario_id = cursor.lastrowid
            if not usuario_id:
                raise Exception("No se pudo obtener el ID del usuario creado")

            # Crear el maestro
            sql_maestro = """
                INSERT INTO maestro (id, numero_empleado, especialidad) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql_maestro, (usuario_id, numero_empleado, especialidad))
            
            conn.commit()
            return True, "Maestro creado correctamente"
            
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1062: # Error de entrada duplicada
                if 'email' in e.msg:
                    return False, "Error: El email ya está registrado."
                if 'numero_empleado' in e.msg:
                    return False, "Error: El número de empleado ya está registrado."
            return False, f"Error al crear maestro: {e}"
        except Exception as ex:
             if conn: conn.rollback()
             return False, f"Error inesperado: {ex}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_maestros(self) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    m.id, m.numero_empleado, 
                    m.especialidad,
                    u.email, 
                    u.nombre, 
                    u.apellido_paterno,
                    u.apellido_materno, 
                    u.telefono
                FROM maestro m
                INNER JOIN usuario u ON m.id = u.id
                ORDER BY u.nombre, u.apellido_paterno
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else []
            
        except Error as e:
            print(f"Error al listar maestros: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_maestro_por_id(self, maestro_id: int) -> Optional[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    m.id, 
                    m.numero_empleado, 
                    m.especialidad,
                    u.email, 
                    u.nombre, 
                    u.apellido_paterno,
                    u.apellido_materno, 
                    u.telefono
                FROM maestro m
                INNER JOIN usuario u ON m.id = u.id
                WHERE m.id = %s
            """
            cursor.execute(sql, (maestro_id,))
            result = cursor.fetchone()
            return result if result else None
            
        except Error as e:
            print(f"Error al buscar maestro: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_maestro(self, maestro_id: int, numero_empleado: str, 
                             especialidad: str, nombre: str, apellido_paterno: str,
                             apellido_materno: str, telefono: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction() # Iniciar transacción
            
            # Actualizar tabla maestro
            sql_maestro = """
                UPDATE maestro 
                SET numero_empleado=%s, especialidad=%s
                WHERE id=%s
            """
            cursor.execute(sql_maestro, (numero_empleado, especialidad, maestro_id))
            
            # Actualizar tabla usuario
            sql_usuario = """
                UPDATE usuario 
                SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s
                WHERE id=%s
            """
            cursor.execute(sql_usuario, (nombre, apellido_paterno, apellido_materno, 
                                          telefono, maestro_id))
            
            conn.commit() # Confirmar transacción
            return True, "Maestro actualizado correctamente"
            
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Error al actualizar: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar_maestro(self, maestro_id: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario WHERE id=%s AND rol='MAESTRO'", (maestro_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Maestro eliminado correctamente"
            else:
                return False, "Maestro no encontrado"
                
        except Error as e:
            if conn:
                conn.rollback()
            if e.errno == 1451:
                return False, "Error: No se puede eliminar, el maestro está asignado a un grupo."
            return False, f"Error al eliminar: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_materias_por_carrera(self, carrera_id: int) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id, codigo, nombre, creditos
                FROM materia
                WHERE carrera_id = %s
                ORDER BY nombre
            """
            cursor.execute(sql, (carrera_id,))
            rows = cursor.fetchall()
            return list(rows) if rows else []
            
        except Error as e:
            print(f"Error al obtener materias: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def validar_numero_empleado(self, numero_empleado: str, maestro_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False

        cursor = None
        try:
            cursor = conn.cursor()
            if maestro_id:
                sql = "SELECT COUNT(*) FROM maestro WHERE numero_empleado = %s AND id != %s"
                cursor.execute(sql, (numero_empleado, maestro_id))
            else:
                sql = "SELECT COUNT(*) FROM maestro WHERE numero_empleado = %s"
                cursor.execute(sql, (numero_empleado,))

            count = cursor.fetchone()
            return count is not None and count[0] == 0
        except Exception:
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_carreras(self) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, nombre FROM carrera ORDER BY nombre"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else []
            
        except Error as e:
            print(f"Error al obtener carreras: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()