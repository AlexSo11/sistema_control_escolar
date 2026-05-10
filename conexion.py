"""
Módulo de Conexión a Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import mysql.connector
from mysql.connector import Error

class ConexionDB:    
    def __init__(self, host='localhost', user='root', password='MeTiFAA1E7', database='control_escolar'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            #'charset': 'utf8mb4',
            #'collation': 'utf8mb4_unicode_ci'
        }

    def obtener_conexion(self):
        """
        Establece y retorna una conexión a la base de datos
        
        Returns:
            mysql.connector.connection: Objeto de conexión si es exitoso, None en caso de error
        """
        try:
            conn = mysql.connector.connect(**self.config)
            if conn.is_connected():
                return conn
        except Error as e:
            print(f'Error al conectar a la base de datos: {e}')
            return None
    
    def verificar_conexion(self):
        """
        Verifica si la conexión a la base de datos es exitosa
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        conn = self.obtener_conexion()
        if conn:
            conn.close()
            return True
        return False