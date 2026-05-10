"""
Interfaz de Gestión de Alumnos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import hashlib
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DBAlumno:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    # --- Funciones de Perfil de Alumno (CRUD) ---
    # (crear_alumno, actualizar_alumno, listar_alumnos, etc.

    def get_carreras(self) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM carrera ORDER BY nombre")
            carreras = cursor.fetchall()
            return list(carreras) if carreras else []
        except Error as e:
            print(f"Error al obtener carreras: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_alumnos(self, estado_filtro: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    u.id, u.email, u.nombre, u.apellido_paterno, u.apellido_materno,
                    a.matricula, a.fecha_nacimiento, a.estado,
                    c.id as carrera_id, c.nombre as carrera_nombre
                FROM usuario u
                JOIN alumno a ON u.id = a.id
                LEFT JOIN carrera c ON a.carrera_id = c.id
                WHERE u.rol = 'ALUMNO'
            """
            params = []
            if estado_filtro and estado_filtro != "TODOS":
                sql += " AND a.estado = %s"
                params.append(estado_filtro)
            sql += " ORDER BY u.apellido_paterno, u.apellido_materno"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar alumnos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _buscar_alumno_por(self, campo: str, valor: Any) -> Optional[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    u.id, u.email, u.nombre, u.apellido_paterno, u.apellido_materno,
                    a.matricula, a.fecha_nacimiento, a.carrera_id, a.estado,
                    c.nombre as carrera_nombre
                FROM usuario u
                JOIN alumno a ON u.id = a.id
                LEFT JOIN carrera c ON a.carrera_id = c.id
                WHERE u.rol = 'ALUMNO' AND {campo} = %s
            """.format(campo=campo)
            cursor.execute(sql, (valor,))
            result = cursor.fetchone()
            return result if result else None
        except Error as e:
            print(f"Error al buscar alumno: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_alumno_por_matricula(self, matricula: str) -> Optional[Dict[str, Any]]:
        return self._buscar_alumno_por("a.matricula", matricula)
    
    def buscar_alumno_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._buscar_alumno_por("u.email", email)
    
    def buscar_alumno_por_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self._buscar_alumno_por("u.id", user_id)

    def crear_alumno(self, email: str, password: str, nombre: str, 
                       apellido_paterno: str, apellido_materno: str,
                       matricula: str, fecha_nacimiento: Optional[str], 
                       carrera_id: Optional[int], estado: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            pw_hash = hash_password(password)
            sql_usuario = """
                INSERT INTO usuario (email, password_hash, rol, nombre, 
                                     apellido_paterno, apellido_materno, telefono) 
                VALUES (%s, %s, 'ALUMNO', %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (email, pw_hash, nombre, apellido_paterno, apellido_materno, ''))
            usuario_id = cursor.lastrowid
            if not usuario_id:
                raise Exception("No se pudo obtener el ID del usuario creado")
            sql_alumno = """
                INSERT INTO alumno (id, matricula, carrera_id, fecha_nacimiento, estado) 
                VALUES (%s, %s, %s, %s, %s)
            """
            fecha_nac_db = fecha_nacimiento if fecha_nacimiento else None
            cursor.execute(sql_alumno, (usuario_id, matricula, carrera_id, fecha_nac_db, estado))
            conn.commit()
            return True, "Alumno creado correctamente"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al crear alumno: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_alumno(self, user_id: int, nombre: str, apellido_paterno: str, 
                          apellido_materno: str, matricula: str, 
                          fecha_nacimiento: Optional[str], 
                          carrera_id: Optional[int], estado: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            sql_usuario = "UPDATE usuario SET nombre=%s, apellido_paterno=%s, apellido_materno=%s WHERE id=%s"
            cursor.execute(sql_usuario, (nombre, apellido_paterno, apellido_materno, user_id))
            sql_alumno = "UPDATE alumno SET matricula=%s, carrera_id=%s, fecha_nacimiento=%s, estado=%s WHERE id=%s"
            fecha_nac_db = fecha_nacimiento if fecha_nacimiento else None
            cursor.execute(sql_alumno, (matricula, carrera_id, fecha_nac_db, estado, user_id))
            conn.commit()
            return True, "Alumno actualizado correctamente"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def dar_de_baja_alumno(self, user_id: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE alumno SET estado = 'Baja' WHERE id = %s", (user_id,))
            conn.commit()
            return (True, "Alumno dado de baja") if cursor.rowcount > 0 else (False, "Alumno no encontrado")
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al dar de baja: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_grupos_disponibles_para_alumno(self, alumno_id: int, carrera_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene grupos disponibles PARA LA CARRERA DEL ALUMNO
        y en los que AÚN NO ESTÁ INSCRITO.
        """
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    g.id AS grupo_id,
                    g.codigo AS grupo_codigo,
                    m.nombre AS materia_nombre
                FROM grupo g
                JOIN materia m ON g.materia_id = m.id
                WHERE g.cupos_disponibles > 0
                  AND g.carrera_id = %s  -- Filtro por carrera del grupo
                  AND g.id NOT IN (      -- Filtro de materias ya inscritas
                     SELECT i.grupo_id 
                     FROM inscripcion i 
                     WHERE i.alumno_id = %s
                  )
                ORDER BY m.nombre;
            """
            cursor.execute(sql, (carrera_id, alumno_id))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar grupos disponibles: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_inscripciones_del_alumno(self, alumno_id: int) -> List[Dict[str, Any]]:
        """Obtiene los grupos a los que el alumno ya está inscrito"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    i.id AS inscripcion_id,
                    g.codigo AS grupo_codigo,
                    m.nombre AS materia_nombre,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin
                FROM inscripcion i
                JOIN grupo g ON i.grupo_id = g.id
                JOIN materia m ON g.materia_id = m.id
                LEFT JOIN horario h ON g.horario_id = h.id
                WHERE i.alumno_id = %s
                ORDER BY m.nombre;
            """
            cursor.execute(sql, (alumno_id,))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar inscripciones del alumno: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
            
    def _validar_conflictos_admin(self, alumno_id: int, nuevo_grupo_id: int, cursor) -> Tuple[bool, str]:
        """Valida materia y horario para el admin"""
        
        cursor.execute("SELECT materia_id, horario_id FROM grupo WHERE id = %s", (nuevo_grupo_id,))
        nuevo_grupo = cursor.fetchone()
        if not nuevo_grupo:
            return True, "El grupo que intentas inscribir ya no existe."
        
        nuevo_materia_id = nuevo_grupo[0]
        nuevo_horario_id = nuevo_grupo[1]

        sql_inscritos = """
            SELECT g.materia_id, g.horario_id 
            FROM inscripcion i
            JOIN grupo g ON i.grupo_id = g.id
            WHERE i.alumno_id = %s
        """
        cursor.execute(sql_inscritos, (alumno_id,))
        inscripciones = cursor.fetchall()

        for insc in inscripciones:
            if insc[0] == nuevo_materia_id:
                return True, "Error: El alumno ya está inscrito en otra sección de esta misma materia."
            if insc[1] == nuevo_horario_id:
                return True, "Error: El alumno tiene un choque de horario."
                
        return False, ""

    def admin_inscribir_alumno(self, alumno_id: int, grupo_id: int) -> Tuple[bool, str]:
        """Inscribe al alumno en un grupo y reduce el cupo (Transacción)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            
            # 1. Verificar cupo
            cursor.execute("SELECT cupos_disponibles FROM grupo WHERE id = %s FOR UPDATE", (grupo_id,))
            cupos = cursor.fetchone()
            if not cupos or cupos[0] <= 0:
                conn.rollback()
                return False, "Error: El grupo ya no tiene cupo"

            # 2. Insertar inscripción (la BD revisará duplicados con la llave UNIQUE)
            sql_insert = "INSERT INTO inscripcion (alumno_id, grupo_id, fecha_inscripcion, estado) VALUES (%s, %s, CURDATE(), 'ACTIVA')"
            cursor.execute(sql_insert, (alumno_id, grupo_id))
            
            # 3. Reducir cupo
            cursor.execute("UPDATE grupo SET cupos_disponibles = cupos_disponibles - 1 WHERE id = %s", (grupo_id,))
            conn.commit()
            return True, "Alumno inscrito correctamente"
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1062: # Duplicate entry
                return False, "El alumno ya está inscrito en este grupo"
            return False, f"Error al inscribir: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def admin_dar_baja_materia(self, inscripcion_id: int) -> Tuple[bool, str]:
        """Da de baja al alumno de un grupo y aumenta el cupo (Transacción)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            
            # 1. Obtener grupo_id ANTES de borrar
            cursor.execute("SELECT grupo_id FROM inscripcion WHERE id = %s", (inscripcion_id,))
            res = cursor.fetchone()
            if not res:
                conn.rollback()
                return False, "No se encontró la inscripción"
            grupo_id = res[0]
            
            # 2. Eliminar inscripción
            cursor.execute("DELETE FROM inscripcion WHERE id = %s", (inscripcion_id,))
            
            # 3. Aumentar cupo
            cursor.execute("UPDATE grupo SET cupos_disponibles = cupos_disponibles + 1 WHERE id = %s", (grupo_id,))
            conn.commit()
            return True, "Baja de materia exitosa"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al dar de baja: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    
    # --- Funciones para la pestaña de PLANEACIÓN ---
    
    def get_alumnos_por_grupo(self, grupo_id: int) -> List[Dict[str, Any]]:
        """Obtiene la lista de alumnos inscritos en un grupo específico"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    i.id as inscripcion_id,
                    u.id as alumno_id,
                    a.matricula,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as nombre_completo
                FROM inscripcion i
                JOIN alumno a ON i.alumno_id = a.id
                JOIN usuario u ON a.id = u.id
                WHERE i.grupo_id = %s
                ORDER BY u.apellido_paterno, u.nombre
            """
            cursor.execute(sql, (grupo_id,))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al obtener alumnos por grupo: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_alumnos_disponibles_para_grupo(self, carrera_id: int, grupo_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene alumnos de la misma carrera que NO están inscritos en este grupo.
        """
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    u.id as alumno_id,
                    a.matricula,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as nombre_completo
                FROM alumno a
                JOIN usuario u ON a.id = u.id
                WHERE a.carrera_id = %s
                AND a.id NOT IN (
                    SELECT alumno_id FROM inscripcion WHERE grupo_id = %s
                )
                ORDER BY u.apellido_paterno, u.nombre
            """
            cursor.execute(sql, (carrera_id, grupo_id))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al obtener alumnos disponibles: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # --- Funciones de Validación y Contraseña ---
    
    def actualizar_contrasena(self, user_id: int, nueva_password: str) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            pw_hash = hash_password(nueva_password)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuario SET password_hash=%s WHERE id=%s", (pw_hash, user_id))
            conn.commit()
            return True, "Contraseña actualizada correctamente"
        except Error as e:
            if conn: conn.rollback()
            return False, f"Error al actualizar contraseña: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_email_unico(self, email: str, user_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT id FROM usuario WHERE email=%s AND id!=%s", (email, user_id))
            else:
                cursor.execute("SELECT id FROM usuario WHERE email=%s", (email,))
            return cursor.fetchone() is None
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_matricula_unica(self, matricula: str, user_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT id FROM alumno WHERE matricula=%s AND id!=%s", (matricula, user_id))
            else:
                cursor.execute("SELECT id FROM alumno WHERE matricula=%s", (matricula,))
            return cursor.fetchone() is None
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()