"""
Módulo de Gestión de Grupos - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
from typing import Tuple, Optional, Dict, Any, List
from conexion import ConexionDB
from mysql.connector import Error

class DBGrupo:
    def __init__(self, conexion: ConexionDB):
        self.conexion = conexion

    def crear_grupo(self, codigo: str, materia_id: int, carrera_id: int,
                   maestro_id: int, salon_id: int, horario_id: int,
                   cupos: int = 30) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None:
            return False, "No hay conexión a la base de datos"
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction() # Iniciar transacción
            
            # Validar capacidad del salón
            cursor.execute("SELECT capacidad FROM salon WHERE id = %s", (salon_id,))
            salon = cursor.fetchone()
            if salon and cupos > salon['capacidad']:
                return False, f"Los cupos ({cupos}) exceden la capacidad del salón ({salon['capacidad']})"
            
            # Validar que no haya conflictos de horario
            if not self.validar_horario_maestro(maestro_id, horario_id):
                return False, "El maestro ya tiene un grupo asignado en este horario"
            
            if not self.validar_horario_salon(salon_id, horario_id):
                return False, "El salón ya está ocupado en este horario"
            
            # Insertar grupo
            sql_insert = """
                INSERT INTO grupo (codigo, materia_id, carrera_id, maestro_id, salon_id, horario_id, cupos, cupos_disponibles) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (codigo, materia_id, carrera_id, maestro_id, salon_id, horario_id, cupos, cupos))
            conn.commit()
            return True, "Grupo creado correctamente"

        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1062: # Código duplicado
                return False, f"Error: El código de grupo '{codigo}' ya existe."
            return False, f"Error al crear grupo: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def listar_grupos(self) -> List[Dict[str, Any]]:
        """Lista básica de grupos (para el módulo GruposUI)"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    g.id, g.codigo, g.cupos, g.cupos_disponibles,
                    m.nombre as materia_nombre,
                    c.nombre as carrera_nombre
                FROM grupo g
                LEFT JOIN materia m ON g.materia_id = m.id
                LEFT JOIN carrera c ON g.carrera_id = c.id
                ORDER BY g.codigo
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else []
            
        except Error as e:
            print(f"Error al listar grupos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def buscar_grupo_por_id(self, grupo_id: int) -> Optional[Dict[str, Any]]:
        """Busca un grupo completo por su ID"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return None
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM grupo WHERE id = %s"
            cursor.execute(sql, (grupo_id,))
            result = cursor.fetchone()
            return result if result else None
            
        except Error as e:
            print(f"Error al buscar grupo: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def actualizar_grupo(self, grupo_id: int, codigo: str, materia_id: int, carrera_id: int,
                         maestro_id: int, salon_id: int, horario_id: int,
                         cupos: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            conn.start_transaction()
            
            cursor.execute("SELECT (cupos - cupos_disponibles) as inscritos FROM grupo WHERE id = %s", (grupo_id,))
            res = cursor.fetchone()
            inscritos = res['inscritos'] if res else 0
            
            if cupos < inscritos:
                return False, f"Los cupos ({cupos}) no pueden ser menores a los alumnos ya inscritos ({inscritos})"

            cursor.execute("SELECT capacidad FROM salon WHERE id = %s", (salon_id,))
            salon = cursor.fetchone()
            if salon and cupos > salon['capacidad']:
                return False, f"Los cupos ({cupos}) exceden la capacidad del salón ({salon['capacidad']})"
            
            if not self.validar_horario_maestro(maestro_id, horario_id, grupo_id):
                return False, "El maestro ya tiene un grupo asignado en este horario"
            
            if not self.validar_horario_salon(salon_id, horario_id, grupo_id):
                return False, "El salón ya está ocupado en este horario"
            
            cupos_disponibles = cupos - inscritos
            sql_update = """
                UPDATE grupo SET 
                    codigo = %s, materia_id = %s, carrera_id = %s, 
                    maestro_id = %s, salon_id = %s, horario_id = %s, 
                    cupos = %s, cupos_disponibles = %s
                WHERE id = %s
            """
            cursor.execute(sql_update, (codigo, materia_id, carrera_id, maestro_id, 
                                        salon_id, horario_id, cupos, cupos_disponibles, grupo_id))
            conn.commit()
            return True, "Grupo actualizado correctamente"

        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1062: # Código duplicado
                return False, f"Error: El código de grupo '{codigo}' ya existe."
            return False, f"Error al actualizar grupo: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def eliminar_grupo(self, grupo_id: int) -> Tuple[bool, str]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False, "No hay conexión"
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grupo WHERE id = %s", (grupo_id,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Grupo eliminado correctamente"
            else:
                return False, "Grupo no encontrado"
        except Error as e:
            if conn: conn.rollback()
            if e.errno == 1451: # Error de llave foránea (inscripciones)
                return False, "Error: No se puede eliminar el grupo, ya tiene alumnos inscritos."
            return False, f"Error al eliminar: {e}"
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # --- Funciones de validación ---
    
    def validar_horario_maestro(self, maestro_id: int, horario_id: int,
                                grupo_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if grupo_id:
                sql = "SELECT COUNT(*) FROM grupo WHERE maestro_id = %s AND horario_id = %s AND id != %s"
                cursor.execute(sql, (maestro_id, horario_id, grupo_id))
            else:
                sql = "SELECT COUNT(*) FROM grupo WHERE maestro_id = %s AND horario_id = %s"
                cursor.execute(sql, (maestro_id, horario_id))
            
            count = cursor.fetchone()
            return count is not None and count[0] == 0
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_horario_salon(self, salon_id: int, horario_id: int,
                             grupo_id: Optional[int] = None) -> bool:
        conn = self.conexion.obtener_conexion()
        if conn is None: return False
        cursor = None
        try:
            cursor = conn.cursor()
            if grupo_id:
                sql = "SELECT COUNT(*) FROM grupo WHERE salon_id = %s AND horario_id = %s AND id != %s"
                cursor.execute(sql, (salon_id, horario_id, grupo_id))
            else:
                sql = "SELECT COUNT(*) FROM grupo WHERE salon_id = %s AND horario_id = %s"
                cursor.execute(sql, (salon_id, horario_id))
            
            count = cursor.fetchone() 
            return count is not None and count[0] == 0
        except Error:
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # --- Funciones para Planeación y Combos ---

    def listar_grupos_detallado(self, maestro_id: Optional[int] = None, 
                                salon_id: Optional[int] = None, 
                                horario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    g.id, g.codigo, g.cupos, g.cupos_disponibles, g.carrera_id,
                    m.nombre as materia_nombre,
                    c.nombre as carrera_nombre,
                    CONCAT(u.nombre, ' ', u.apellido_paterno) as maestro_nombre,
                    s.numero as salon_numero,
                    CONCAT(h.dia_semana, ' ', TIME_FORMAT(h.hora_inicio, '%H:%i'), '-', TIME_FORMAT(h.hora_fin, '%H:%i')) as horario_desc
                FROM grupo g
                LEFT JOIN materia m ON g.materia_id = m.id
                LEFT JOIN carrera c ON g.carrera_id = c.id
                LEFT JOIN maestro ma ON g.maestro_id = ma.id
                LEFT JOIN usuario u ON ma.id = u.id
                LEFT JOIN salon s ON g.salon_id = s.id
                LEFT JOIN horario h ON g.horario_id = h.id
                WHERE 1=1
            """
            params = []
            if maestro_id:
                sql += " AND g.maestro_id = %s"
                params.append(maestro_id)
            if salon_id:
                sql += " AND g.salon_id = %s"
                params.append(salon_id)
            if horario_id:
                sql += " AND g.horario_id = %s"
                params.append(horario_id)
            
            sql += " ORDER BY g.codigo"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall() # ¡Correcto!
            return list(rows) if rows else []
        except Error as e:
            print(f"Error al listar grupos detallado: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_filtro_maestros(self) -> List[Dict[str, Any]]:
        """Obtiene ID y Nombres de Maestros para el filtro"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT u.id, CONCAT(u.nombre, ' ', u.apellido_paterno) as nombre 
                FROM usuario u
                JOIN maestro m ON u.id = m.id
                ORDER BY u.nombre
            """
            cursor.execute(sql)
            rows = cursor.fetchall() 
            return list(rows) if rows else []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_filtro_salones(self) -> List[Dict[str, Any]]:
        """Obtiene ID y Nombres de Salones para el filtro"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, numero FROM salon ORDER BY numero"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return list(rows) if rows else []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_filtro_horarios(self) -> List[Dict[str, Any]]:
        """Obtiene ID y Descripciones de Horarios para el filtro"""
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id, CONCAT(dia_semana, ' ', TIME_FORMAT(hora_inicio, '%H:%i'), '-', TIME_FORMAT(hora_fin, '%H:%i')) as horario 
                FROM horario 
                ORDER BY dia_semana, hora_inicio
            """
            cursor.execute(sql)
            rows = cursor.fetchall() 
            return list(rows) if rows else []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_carreras(self) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre FROM carrera ORDER BY nombre")
            rows = cursor.fetchall()
            return list(rows) if rows else []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_materias_por_carrera(self, carrera_id: int) -> List[Dict[str, Any]]:
        conn = self.conexion.obtener_conexion()
        if conn is None: return []
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, codigo, nombre FROM materia WHERE carrera_id = %s ORDER BY nombre", (carrera_id,))
            rows = cursor.fetchall() # Leer siempre los resultados
            return list(rows) if rows else []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def get_maestros(self) -> List[Dict[str, Any]]:
        return self.get_filtro_maestros()

    def get_salones(self) -> List[Dict[str, Any]]:
        return self.get_filtro_salones() 
    
    def get_horarios(self) -> List[Dict[str, Any]]:
        return self.get_filtro_horarios() 