"""
Módulo de Gestión de Alumno "Mi Perfil" - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from conexion import ConexionDB
from datetime import datetime, date

class AlumnoPerfilUI:
    def __init__(self, parent: ttk.Frame, usuario_actual: Dict[str, Any], conexion: ConexionDB):
        self.parent = parent
        self.usuario_actual = usuario_actual 
        self.con = conexion
        
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)
        
        self._crear_tab_perfil()
        self.cargar_datos_perfil() 

    def _crear_tab_perfil(self):
        """Crea los widgets de la pestaña 'Mi Perfil' (solo lectura)"""
        form = ttk.LabelFrame(self.frame, text="Mis Datos Personales", padding=15)
        form.pack(fill='x', expand=False, padx=20, pady=20)

        self.perfil_vars = {
            "Matrícula:": tk.StringVar(),
            "Nombre:": tk.StringVar(),
            "Email:": tk.StringVar(),
            "Carrera:": tk.StringVar(),
            "Estado:": tk.StringVar(),
            "Fecha Nacimiento:": tk.StringVar()
        }
        
        row = 0
        for label, var in self.perfil_vars.items():
            ttk.Label(form, text=label, font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(form, textvariable=var, state='readonly', width=50, font=("Segoe UI", 10))
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            row += 1
            
    def cargar_datos_perfil(self):
        """Carga los datos en las variables desde el dict 'usuario_actual'"""
        # VERIFICACIÓN CRÍTICA: usuario_actual no debe ser None
        if self.usuario_actual is None:
            print("ERROR: usuario_actual es None en cargar_datos_perfil")
            # Establecer valores por defecto
            valores_por_defecto = {
                "Matrícula:": "No disponible",
                "Nombre:": "Usuario", 
                "Email:": "No disponible",
                "Carrera:": "No asignada",
                "Estado:": "No disponible",
                "Fecha Nacimiento:": "No disponible"
            }
            
            for label, valor in valores_por_defecto.items():
                if label in self.perfil_vars:
                    self.perfil_vars[label].set(valor)
            return
        
        # Si tenemos usuario_actual, proceder normalmente
        perfil = self.usuario_actual
        
        # Usar get() con valores por defecto para todos los campos
        nombre = perfil.get('nombre', '')
        apellido_paterno = perfil.get('apellido_paterno', '')
        apellido_materno = perfil.get('apellido_materno', '')
        
        nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}".strip()
        if not nombre_completo:
            nombre_completo = perfil.get('email', 'Usuario')  # Fallback al email
        
        # Asignar valores con verificaciones
        datos_seguros = {
            "Matrícula:": perfil.get('matricula', 'No asignada'),
            "Nombre:": nombre_completo,
            "Email:": perfil.get('email', 'No disponible'),
            "Carrera:": perfil.get('carrera_nombre', 'No asignada'),
            "Estado:": perfil.get('estado', 'Activo')
        }
        
        # Manejar fecha de nacimiento de forma segura
        fecha_nac = perfil.get('fecha_nacimiento')
        fecha_str = 'No disponible'
        
        if fecha_nac:
            try:
                if isinstance(fecha_nac, date):
                    fecha_str = fecha_nac.strftime('%d-%m-%Y')
                elif isinstance(fecha_nac, str):
                    # Intentar parsear si es string
                    from datetime import datetime
                    fecha_obj = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
                    fecha_str = fecha_obj.strftime('%d-%m-%Y')
                else:
                    fecha_str = str(fecha_nac)
            except Exception as e:
                print(f"Error formateando fecha: {e}")
                fecha_str = 'Formato inválido'
        
        datos_seguros["Fecha Nacimiento:"] = fecha_str
        
        # Actualizar la UI
        for label, valor in datos_seguros.items():
            if label in self.perfil_vars:
                self.perfil_vars[label].set(valor)