"""
Módulo de Gestión de Alumno "Horario" - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from DB.dbAlumnoVista import DBAlumnoVista
from conexion import ConexionDB
from datetime import time, timedelta

class AlumnoHorarioUI:
    def __init__(self, parent: ttk.Frame, usuario_actual: Dict[str, Any], conexion: ConexionDB):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = conexion
        self.db = DBAlumnoVista(self.con)
        self.alumno_id = self.usuario_actual['id']
        
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)
        
        self._crear_tab_horario()
        self.cargar_mi_horario_visual()
 
        self.parent.bind("<<RecargarHorario>>", lambda e: self.cargar_mi_horario_visual())

    def _crear_tab_horario(self):
        """Crea la cuadrícula visual del horario"""

        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar_y = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient='horizontal', command=canvas.xview)
        
        grid_frame = ttk.Frame(canvas)
        
        grid_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=grid_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        canvas.pack(side='left', fill='both', expand=True)

        # --- Definir Horas y Días ---
        self.dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
        self.horas_dia = [time(h, 0, 0) for h in range(7, 22)]
        
        self.celdas_horario: Dict[tuple, tk.Label] = {}
        self.info_clases: Dict[tuple, Dict] = {}

        ttk.Label(grid_frame, text="Hora", font=("Segoe UI", 10, "bold"), relief="solid", padding=5, anchor='center').grid(row=0, column=0, sticky="nsew")

        for c, dia in enumerate(self.dias_semana):
            ttk.Label(grid_frame, text=dia, font=("Segoe UI", 10, "bold"), relief="solid", padding=5, anchor='center').grid(row=0, column=c+1, sticky="nsew")
            grid_frame.columnconfigure(c+1, weight=1, minsize=150)

        for r, hora in enumerate(self.horas_dia):
            hora_str = hora.strftime('%H:%M')
            ttk.Label(grid_frame, text=hora_str, font=("Segoe UI", 10, "bold"), relief="solid", padding=5, anchor='center').grid(row=r+1, column=0, sticky="nsew")
            grid_frame.rowconfigure(r+1, weight=1, minsize=80)
            
            for c, dia in enumerate(self.dias_semana):
                celda = tk.Label(grid_frame, text="", relief="solid", borderwidth=1, anchor='nw', 
                                 justify='left', wraplength=140, bg="white", 
                                 font=("Segoe UI", 9))
                celda.grid(row=r+1, column=c+1, sticky="nsew")
                self.celdas_horario[(hora, dia)] = celda

    def cargar_mi_horario_visual(self):
        """Carga los grupos del maestro en la cuadrícula visual"""
        self.info_clases.clear()
        for celda in self.celdas_horario.values():
            celda.config(text="", bg="white", cursor="")
            celda.unbind("<Button-1>")

        grupos = self.db.get_mi_horario_visual(self.maestro_id)

        for grupo in grupos:
            dia = grupo.get('dia_semana')
            hora_inicio = grupo.get('hora_inicio')

            if isinstance(hora_inicio, timedelta):
                total_seconds = int(hora_inicio.total_seconds())
                hora_inicio = time(total_seconds // 3600, (total_seconds % 3600) // 60, total_seconds % 60)
            
            if hora_inicio:
                hora_inicio_redondeada = hora_inicio.replace(minute=0, second=0, microsecond=0)
            else:
                continue

            if dia in self.dias_semana and hora_inicio_redondeada in self.horas_dia:
                key = (hora_inicio_redondeada, dia)
                
                if key in self.celdas_horario:
                    celda = self.celdas_horario[key]
                    
                    texto = f"{grupo.get('materia_nombre')}\n"
                    texto += f"({grupo.get('grupo_codigo')})\n"
                    texto += f"Salón: {grupo.get('salon_numero', 'N/A')}"
                    
                    celda.config(text=texto, bg="#D1E8FF", fg="black", cursor="hand2")
                    
                    self.info_clases[key] = grupo
                    
                    celda.bind("<Button-1>", lambda e, k=key: self.mostrar_detalles_clase(k))

    def mostrar_detalles_clase(self, key: tuple):
        """Muestra una ventana con los detalles completos del grupo seleccionado"""
        if key not in self.info_clases:
            return
            
        grupo = self.info_clases[key]
        
        hora_i = grupo.get('hora_inicio')
        hora_f = grupo.get('hora_fin')
        
        # Formatear horas
        def format_time(t):
            if isinstance(t, timedelta):
                total_seconds = int(t.total_seconds())
                h = total_seconds // 3600
                m = (total_seconds % 3600) // 60
                return f"{h:02d}:{m:02d}"
            if isinstance(t, time):
                return t.strftime('%H:%M')
            if t is None:
                return "N/A"
            return str(t)
            
        hora_i_str = format_time(hora_i)
        hora_f_str = format_time(hora_f)
        
        detalles = f"Materia: {grupo.get('materia_nombre')}\n"
        detalles += f"Grupo: {grupo.get('grupo_codigo')}\n"
        detalles += f"Maestro: {grupo.get('maestro_nombre', 'N/A')}\n"
        detalles += f"Salón: {grupo.get('salon_numero', 'N/A')}\n"
        detalles += f"Horario: {grupo.get('dia_semana')} de {hora_i_str} a {hora_f_str}"
        
        messagebox.showinfo(f"Detalle de Clase - {grupo.get('materia_nombre')}", detalles)