"""
Módulo de Gestión de Usuarios - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import hashlib
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

def hash_password(password: str) -> str:
    """
    Genera un hash SHA256 de la contraseña
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash SHA256 de la contraseña
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DBUsuario:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_usuario(self, email: str, password: str, rol: str, nombre: str, 
                     apellido_paterno: str = '', apellido_materno: str = '', 
                     telefono: str = '', datos_adicionales: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            pw_hash = hash_password(password)
            cursor = conn.cursor()
            
            # Insertar usuario base
            sql_usuario = """
                INSERT INTO usuario (email, password_hash, rol, nombre, 
                                   apellido_paterno, apellido_materno, telefono) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (email, pw_hash, rol.upper(), nombre, 
                                        apellido_paterno, apellido_materno, telefono))
            
            usuario_id = cursor.lastrowid
            
            # Si es ALUMNO o MAESTRO, insertar datos adicionales
            if datos_adicionales:
                if rol.upper() == 'ALUMNO' and 'matricula' in datos_adicionales:
                    sql_alumno = """
                        INSERT INTO alumno (id, matricula, carrera_id, fecha_nacimiento) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_alumno, (
                        usuario_id,
                        datos_adicionales.get('matricula'),
                        datos_adicionales.get('carrera_id'),
                        datos_adicionales.get('fecha_nacimiento')
                    ))
                    
                elif rol.upper() == 'MAESTRO' and 'numero_empleado' in datos_adicionales:
                    sql_maestro = """
                        INSERT INTO maestro (id, numero_empleado, especialidad) 
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_maestro, (
                        usuario_id,
                        datos_adicionales.get('numero_empleado'),
                        datos_adicionales.get('especialidad')
                    ))
            
            conn.commit()
            return True, f"Usuario {rol} creado correctamente"
            
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Error al crear usuario: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def autenticar(self, email: str, password: str) -> Tuple[bool, Dict[str, Any] | str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la BD"
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE email = %s"
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Usuario no encontrado"
            
            # Verificar que row sea un diccionario
            if not isinstance(row, dict):
                return False, "Error al obtener datos del usuario"
                
            if row.get('password_hash') == hash_password(password):
                # No devolver el hash de contraseña
                user: Dict[str, Any] = {k: v for k, v in row.items() if k != 'password_hash'}
                
                # Obtener datos adicionales según el rol
                if user.get('rol') == 'ALUMNO':
                    cursor.execute("SELECT * FROM alumno WHERE id = %s", (user['id'],))
                    alumno_data = cursor.fetchone()
                    if alumno_data and isinstance(alumno_data, dict):
                        user.update(alumno_data)
                        
                elif user.get('rol') == 'MAESTRO':
                    cursor.execute("SELECT * FROM maestro WHERE id = %s", (user['id'],))
                    maestro_data = cursor.fetchone()
                    if maestro_data and isinstance(maestro_data, dict):
                        user.update(maestro_data)
                
                return True, user
            else:
                return False, "Contraseña incorrecta"
                
        except Error as e:
            return False, f"Error en autenticación: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def listar_usuarios(self, rol: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            
            if rol:
                sql = """
                    SELECT u.id, u.email, u.rol, u.nombre, u.apellido_paterno, 
                           u.apellido_materno, u.telefono, u.fecha_creacion
                    FROM usuario u
                    WHERE u.rol = %s
                    ORDER BY u.fecha_creacion DESC
                """
                cursor.execute(sql, (rol.upper(),))
            else:
                sql = """
                    SELECT u.id, u.email, u.rol, u.nombre, u.apellido_paterno, 
                           u.apellido_materno, u.telefono, u.fecha_creacion
                    FROM usuario u
                    ORDER BY u.rol, u.fecha_creacion DESC
                """
                cursor.execute(sql)
                
            rows = cursor.fetchall()
            # Asegurar que siempre retornamos una lista
            if rows is None:
                return []
            return list(rows) if rows else [] # type: ignore
            
        except Error as e:
            print(f"Error al listar usuarios: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def buscar_usuario_por_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT u.id, u.email, u.rol, u.nombre, u.apellido_paterno, 
                       u.apellido_materno, u.telefono, u.fecha_creacion
                FROM usuario u
                WHERE u.id = %s
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result if result else None # type: ignore
            
        except Error as e:
            print(f"Error al buscar usuario: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def buscar_usuario_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT u.id, u.email, u.rol, u.nombre, u.apellido_paterno, 
                       u.apellido_materno, u.telefono, u.fecha_creacion
                FROM usuario u
                WHERE u.email = %s
            """
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return result if result else None # type: ignore
            
        except Error as e:
            print(f"Error al buscar usuario: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def actualizar_usuario(self, user_id: int, nombre: str, apellido_paterno: str, 
                          apellido_materno: str, telefono: str, 
                          rol: Optional[str] = None) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            
            if rol:
                sql = """
                    UPDATE usuario 
                    SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, 
                        telefono=%s, rol=%s 
                    WHERE id=%s
                """
                cursor.execute(sql, (nombre, apellido_paterno, apellido_materno, 
                                   telefono, rol.upper(), user_id))
            else:
                sql = """
                    UPDATE usuario 
                    SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s 
                    WHERE id=%s
                """
                cursor.execute(sql, (nombre, apellido_paterno, apellido_materno, 
                                   telefono, user_id))
            
            conn.commit()
            return True, "Usuario actualizado correctamente"
            
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Error al actualizar: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def actualizar_contrasena(self, user_id: int, nueva_password: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        
        cursor = None
        try:
            pw_hash = hash_password(nueva_password)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuario SET password_hash=%s WHERE id=%s", 
                         (pw_hash, user_id))
            conn.commit()
            return True, "Contraseña actualizada correctamente"
            
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Error al actualizar contraseña: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar_usuario(self, user_id: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            # Por CASCADE, también se eliminará de alumno/maestro si existe
            cursor.execute("DELETE FROM usuario WHERE id=%s", (user_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Usuario eliminado correctamente"
            else:
                return False, "Usuario no encontrado"
                
        except Error as e:
            if conn:
                conn.rollback()
            return False, f"Error al eliminar: {e}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def validar_email_unico(self, email: str, user_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False
        
        cursor = None
        try:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT id FROM usuario WHERE email=%s AND id!=%s", 
                             (email, user_id))
            else:
                cursor.execute("SELECT id FROM usuario WHERE email=%s", (email,))
                
            return cursor.fetchone() is None
            
        except Error:
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
