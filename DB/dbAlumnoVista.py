"""
Módulo de Gestión de la vista Alumno - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBAlumnoVista:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def get_mi_perfil(self, alumno_id: int) -> Optional[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    u.email, u.nombre, u.apellido_paterno, u.apellido_materno,
                    a.matricula, a.fecha_nacimiento, a.estado,
                    c.id as carrera_id, c.nombre as carrera_nombre
                FROM usuario u
                JOIN alumno a ON u.id = a.id
                LEFT JOIN carrera c ON a.carrera_id = c.id
                WHERE u.id = %s
            """
            cursor.execute(sql, (alumno_id,))
            result = cursor.fetchone()
            return result if result else None
        except Error as e:
            print(f"Error al obtener perfil de alumno: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_grupos_disponibles(self, alumno_id: int, carrera_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene grupos con cupo, de la carrera, donde el alumno no esté inscrito
        Y que NO se empalmen con su horario O materia.
        """
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            # --- ¡INICIO DE LA CORRECCIÓN! ---
            # Usamos subconsultas (WITH) para obtener los IDs de horarios y materias
            # que el alumno YA tiene inscritos.
            sql = """
                WITH MateriasInscritas AS (
                    SELECT DISTINCT m.id 
                    FROM inscripcion i
                    JOIN grupo g_insc ON i.grupo_id = g_insc.id
                    JOIN materia m ON g_insc.materia_id = m.id
                    WHERE i.alumno_id = %s
                ),
                HorariosInscritos AS (
                    SELECT DISTINCT g_insc.horario_id
                    FROM inscripcion i
                    JOIN grupo g_insc ON i.grupo_id = g_insc.id
                    WHERE i.alumno_id = %s
                )
                SELECT 
                    g.id AS grupo_id,
                    g.codigo AS grupo_codigo,
                    m.nombre AS materia_nombre,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as maestro_nombre,
                    CONCAT(h.dia_semana, ' ', TIME_FORMAT(h.hora_inicio, '%H:%i'), '-', TIME_FORMAT(h.hora_fin, '%H:%i')) as horario_desc,
                    g.cupos_disponibles
                FROM grupo g
                JOIN materia m ON g.materia_id = m.id
                LEFT JOIN maestro ma ON g.maestro_id = ma.id
                LEFT JOIN usuario u ON ma.id = u.id
                LEFT JOIN horario h ON g.horario_id = h.id
                WHERE g.carrera_id = %s
                  AND g.cupos_disponibles > 0
                  AND m.id NOT IN (SELECT id FROM MateriasInscritas)
                  AND g.horario_id NOT IN (SELECT horario_id FROM HorariosInscritos)
                ORDER BY m.nombre;
            """
            # Pasamos el alumno_id dos veces (para las 2 subconsultas) y la carrera_id
            cursor.execute(sql, (alumno_id, alumno_id, carrera_id))
            # --- FIN DE LA CORRECCIÓN ---
            
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar grupos disponibles (alumno): {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_mis_inscripciones(self, alumno_id: int) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    g.codigo AS grupo_codigo,
                    m.nombre AS materia_nombre,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as maestro_nombre,
                    s.numero as salon_numero,
                    CONCAT(h.dia_semana, ' ', TIME_FORMAT(h.hora_inicio, '%H:%i'), '-', TIME_FORMAT(h.hora_fin, '%H:%i')) as horario_desc,
                    i.estado
                FROM inscripcion i
                JOIN grupo g ON i.grupo_id = g.id
                JOIN materia m ON g.materia_id = m.id
                LEFT JOIN maestro ma ON g.maestro_id = ma.id
                LEFT JOIN usuario u ON ma.id = u.id
                LEFT JOIN salon s ON g.salon_id = s.id
                LEFT JOIN horario h ON g.horario_id = h.id
                WHERE i.alumno_id = %s
                ORDER BY h.hora_inicio, h.dia_semana;
            """
            cursor.execute(sql, (alumno_id,))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar mis inscripciones: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _validar_conflictos(self, alumno_id: int, nuevo_grupo_id: int, cursor) -> Tuple[bool, str]:
        """Función helper para validar materia y horario (DEBE ser llamada dentro de una transacción)"""
        
        # 1. Obtener info del nuevo grupo
        cursor.execute("SELECT materia_id, horario_id FROM grupo WHERE id = %s", (nuevo_grupo_id,))
        nuevo_grupo = cursor.fetchone()
        if not nuevo_grupo:
            return True, "El grupo que intentas inscribir ya no existe."
        
        nuevo_materia_id = nuevo_grupo[0]
        nuevo_horario_id = nuevo_grupo[1]

        # 2. Obtener info de los grupos YA inscritos
        sql_inscritos = """
            SELECT g.materia_id, g.horario_id 
            FROM inscripcion i
            JOIN grupo g ON i.grupo_id = g.id
            WHERE i.alumno_id = %s
        """
        cursor.execute(sql_inscritos, (alumno_id,))
        inscripciones = cursor.fetchall()

        # 3. Validar
        for insc in inscripciones:
            materia_id_inscrita = insc[0]
            horario_id_inscrito = insc[1]
            
            if materia_id_inscrita == nuevo_materia_id:
                return True, "Error: Ya estás inscrito en otra sección de esta misma materia."
            if horario_id_inscrito == nuevo_horario_id:
                return True, "Error: Tienes un choque de horario. Ya tienes una materia a esta hora."
                
        return False, "" # No hay conflictos

    def inscribir_grupo(self, alumno_id: int, grupo_id: int) -> Tuple[bool, str]:
        """Inscribe al alumno en un grupo (Transacción con validación de conflictos)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        cursor = None
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            
            # 1. Verificar cupo (con bloqueo)
            cursor.execute("SELECT cupos_disponibles FROM grupo WHERE id = %s FOR UPDATE", (grupo_id,))
            cupos = cursor.fetchone()
            if not cupos or cupos[0] <= 0:
                conn.rollback()
                return False, "Error: El grupo ya no tiene cupo."

            # --- ¡INICIO DE LA CORRECCIÓN! ---
            # 2. Verificar conflictos de horario y materia
            hay_conflicto, msg_conflicto = self._validar_conflictos(alumno_id, grupo_id, cursor)
            if hay_conflicto:
                conn.rollback()
                return False, msg_conflicto
            # --- FIN DE LA CORRECCIÓN ---

            # 3. Insertar inscripción
            sql_insert = "INSERT INTO inscripcion (alumno_id, grupo_id, fecha_inscripcion, estado) VALUES (%s, %s, CURDATE(), 'ACTIVA')"
            cursor.execute(sql_insert, (alumno_id, grupo_id))
            
            # 4. Reducir cupo
            cursor.execute("UPDATE grupo SET cupos_disponibles = cupos_disponibles - 1 WHERE id = %s", (grupo_id,))
            conn.commit()
            return True, "¡Inscripción exitosa!"
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1062: # Duplicate entry
                return False, "Error: Ya estás inscrito en este grupo."
            return False, f"Error al inscribir: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_mi_horario_visual(self, alumno_id: int) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    g.codigo AS grupo_codigo,
                    m.nombre AS materia_nombre,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as maestro_nombre,
                    s.numero as salon_numero,
                    h.dia_semana,
                    h.hora_inicio,
                    h.hora_fin
                FROM inscripcion i
                JOIN grupo g ON i.grupo_id = g.id
                JOIN materia m ON g.materia_id = m.id
                LEFT JOIN maestro ma ON g.maestro_id = ma.id
                LEFT JOIN usuario u ON ma.id = u.id
                LEFT JOIN salon s ON g.salon_id = s.id
                LEFT JOIN horario h ON g.horario_id = h.id
                WHERE i.alumno_id = %s AND i.estado = 'ACTIVA'
            """
            cursor.execute(sql, (alumno_id,))
            rows = cursor.fetchall()
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al obtener mi horario visual: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()