"""
Módulo de Gestión de Planeación - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from DB.dbGrupos import DBGrupo
from DB.dbAlumnos import DBAlumno
from conexion import ConexionDB

class PlaneacionUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db_grupo = DBGrupo(self.con)
        self.db_alumno = DBAlumno(self.con)
        
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        if not self.usuario_actual or self.usuario_actual.get('rol') != 'ADMIN':
            ttk.Label(self.frame, text="Acceso denegado. Solo administradores.", foreground="red").pack(pady=50)
            return
            
        self.admin_id = self.usuario_actual.get('id')

        # --- Variables de Filtros ---
        self.var_filtro_maestro = tk.StringVar()
        self.var_filtro_salon = tk.StringVar()
        self.var_filtro_horario = tk.StringVar()
        self.filtro_maestro_map: Dict[str, int] = {}
        self.filtro_salon_map: Dict[str, int] = {}
        self.filtro_horario_map: Dict[str, int] = {}

        # --- Variables de Gestión de Alumnos ---
        self.var_alumno_agregar = tk.StringVar()
        self.alumnos_disponibles_map: Dict[str, int] = {}
        self.grupo_seleccionado_id: Optional[int] = None
        self.grupo_seleccionado_carrera_id: Optional[int] = None

        # --- Widgets ---
        self.tree_grupos: ttk.Treeview
        self.gestor_alumnos_frame: ttk.LabelFrame
        self.combo_alumnos_disponibles: ttk.Combobox
        self.tree_alumnos_inscritos: ttk.Treeview
        self.btn_agregar_alumno: ttk.Button
        self.btn_quitar_alumno: ttk.Button

        # --- Construir UI ---
        self.build_ui()
        self.cargar_datos_filtros()
        self.aplicar_filtros() # Carga inicial de todos los grupos

    def build_ui(self):
        """Construye la interfaz de filtros, lista y gestión"""
        
        # --- Frame 1: Filtros ---
        filtro_frame = ttk.LabelFrame(self.frame, text="Filtros de Grupos", padding=10)
        filtro_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(filtro_frame, text="Maestro:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_filtro_maestro = ttk.Combobox(filtro_frame, textvariable=self.var_filtro_maestro, state='readonly', width=30)
        self.combo_filtro_maestro.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filtro_frame, text="Salón:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_filtro_salon = ttk.Combobox(filtro_frame, textvariable=self.var_filtro_salon, state='readonly', width=20)
        self.combo_filtro_salon.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filtro_frame, text="Horario:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_filtro_horario = ttk.Combobox(filtro_frame, textvariable=self.var_filtro_horario, state='readonly', width=30)
        self.combo_filtro_horario.grid(row=1, column=1, padx=5, pady=5)

        btn_aplicar = ttk.Button(filtro_frame, text="Aplicar Filtros", command=self.aplicar_filtros)
        btn_aplicar.grid(row=1, column=2, padx=5, pady=5, sticky='e')
        
        btn_limpiar = ttk.Button(filtro_frame, text="Limpiar", command=self.limpiar_filtros)
        btn_limpiar.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # --- Frame 2: Lista de Grupos ---
        grupos_frame = ttk.LabelFrame(self.frame, text="Lista de Grupos Creados", padding=10)
        grupos_frame.pack(fill='both', expand=True, pady=(0, 10))

        cols = ("id", "codigo", "materia", "carrera", "maestro", "salon", "horario", "cupos", "disponibles")
        self.tree_grupos = ttk.Treeview(grupos_frame, columns=cols, show='headings', height=8)
        self.tree_grupos.heading("id", text="ID")
        self.tree_grupos.heading("codigo", text="Código")
        self.tree_grupos.heading("materia", text="Materia")
        self.tree_grupos.heading("carrera", text="Carrera")
        self.tree_grupos.heading("maestro", text="Maestro")
        self.tree_grupos.heading("salon", text="Salón")
        self.tree_grupos.heading("horario", text="Horario")
        self.tree_grupos.heading("cupos", text="Cupos")
        self.tree_grupos.heading("disponibles", text="Disp.")
        
        self.tree_grupos.column("id", width=40, anchor='center')
        self.tree_grupos.column("codigo", width=80)
        self.tree_grupos.column("materia", width=150)
        self.tree_grupos.column("carrera", width=150)
        self.tree_grupos.column("maestro", width=150)
        self.tree_grupos.column("salon", width=60, anchor='center')
        self.tree_grupos.column("horario", width=180)
        self.tree_grupos.column("cupos", width=50, anchor='center')
        self.tree_grupos.column("disponibles", width=50, anchor='center')

        scrollbar_y = ttk.Scrollbar(grupos_frame, orient='vertical', command=self.tree_grupos.yview)
        scrollbar_x = ttk.Scrollbar(grupos_frame, orient='horizontal', command=self.tree_grupos.xview)
        self.tree_grupos.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        self.tree_grupos.pack(fill='both', expand=True)
        
        self.tree_grupos.bind("<<TreeviewSelect>>", self.on_grupo_select)

        # --- Frame 3: Gestión de Alumnos (inicialmente deshabilitado) ---
        self.gestor_alumnos_frame = ttk.LabelFrame(self.frame, text="Gestionar Alumnos del Grupo Seleccionado", padding=10)
        self.gestor_alumnos_frame.pack(fill='both', expand=True)
        
        # Sub-frame Izquierdo: Agregar Alumno
        add_frame = ttk.Frame(self.gestor_alumnos_frame)
        add_frame.pack(side='left', fill='y', padx=10)
        
        ttk.Label(add_frame, text="Alumnos disponibles (de la carrera):").pack(anchor='w')
        self.combo_alumnos_disponibles = ttk.Combobox(add_frame, textvariable=self.var_alumno_agregar, state='disabled', width=40)
        self.combo_alumnos_disponibles.pack(fill='x', pady=5)
        self.btn_agregar_alumno = ttk.Button(add_frame, text="Agregar Alumno al Grupo", command=self.agregar_alumno, state='disabled')
        self.btn_agregar_alumno.pack(pady=10)

        # Sub-frame Derecho: Lista de Inscritos
        list_frame = ttk.Frame(self.gestor_alumnos_frame)
        list_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        ttk.Label(list_frame, text="Alumnos Inscritos:").pack(anchor='w')
        cols_insc = ("insc_id", "matricula", "nombre")
        self.tree_alumnos_inscritos = ttk.Treeview(list_frame, columns=cols_insc, show='headings', height=5)
        self.tree_alumnos_inscritos.heading("insc_id", text="ID Insc.")
        self.tree_alumnos_inscritos.heading("matricula", text="Matrícula")
        self.tree_alumnos_inscritos.heading("nombre", text="Nombre Alumno")
        self.tree_alumnos_inscritos.column("insc_id", width=60, anchor='center')
        self.tree_alumnos_inscritos.column("matricula", width=100)
        self.tree_alumnos_inscritos.column("nombre", width=250)
        
        scrollbar_insc = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_alumnos_inscritos.yview)
        self.tree_alumnos_inscritos.configure(yscrollcommand=scrollbar_insc.set)
        scrollbar_insc.pack(side='right', fill='y')
        self.tree_alumnos_inscritos.pack(fill='both', expand=True)
        
        self.btn_quitar_alumno = ttk.Button(list_frame, text="Quitar Alumno Seleccionado", command=self.quitar_alumno, state='disabled')
        self.btn_quitar_alumno.pack(pady=5)
        
        self.set_estado_gestor_alumnos(False) # Deshabilitar al inicio

    def set_estado_gestor_alumnos(self, habilitar: bool):
        """Habilita o deshabilita la sección de gestión de alumnos"""
        estado_combo = 'readonly' if habilitar else 'disabled'
        estado_btn = 'normal' if habilitar else 'disabled'
        
        self.combo_alumnos_disponibles.config(state=estado_combo)
        self.btn_agregar_alumno.config(state=estado_btn)
        self.btn_quitar_alumno.config(state=estado_btn)
        if not habilitar:
            self.var_alumno_agregar.set('')
            for row in self.tree_alumnos_inscritos.get_children():
                self.tree_alumnos_inscritos.delete(row)

    def cargar_datos_filtros(self):
        """Carga los datos para los combobox de filtros"""
        # Maestros
        maestros = self.db_grupo.get_filtro_maestros()
        self.filtro_maestro_map = {f"{m['nombre']} (ID: {m['id']})": m['id'] for m in maestros}
        self.combo_filtro_maestro['values'] = [''] + list(self.filtro_maestro_map.keys())
        
        # Salones
        salones = self.db_grupo.get_filtro_salones()
        self.filtro_salon_map = {f"{s['numero']} (ID: {s['id']})": s['id'] for s in salones}
        self.combo_filtro_salon['values'] = [''] + list(self.filtro_salon_map.keys())

        # Horarios
        horarios = self.db_grupo.get_filtro_horarios()
        self.filtro_horario_map = {h['horario']: h['id'] for h in horarios}
        self.combo_filtro_horario['values'] = [''] + list(self.filtro_horario_map.keys())

    def limpiar_filtros(self):
        self.var_filtro_maestro.set('')
        self.var_filtro_salon.set('')
        self.var_filtro_horario.set('')
        self.aplicar_filtros()
        self.set_estado_gestor_alumnos(False)

    def aplicar_filtros(self):
        """Busca en la BD con los filtros seleccionados"""
        # Obtener IDs de los filtros
        maestro_id = self.filtro_maestro_map.get(self.var_filtro_maestro.get())
        salon_id = self.filtro_salon_map.get(self.var_filtro_salon.get())
        horario_id = self.filtro_horario_map.get(self.var_filtro_horario.get())
        
        # Limpiar treeview
        for row in self.tree_grupos.get_children():
            self.tree_grupos.delete(row)
        
        # Cargar datos
        grupos = self.db_grupo.listar_grupos_detallado(maestro_id, salon_id, horario_id)
        
        for g in grupos:
            self.tree_grupos.insert('', 'end', values=(
                g.get('id'),
                g.get('codigo'),
                g.get('materia_nombre'),
                g.get('carrera_nombre'),
                g.get('maestro_nombre'),
                g.get('salon_numero'),
                g.get('horario_desc'),
                g.get('cupos'),
                g.get('cupos_disponibles')
            ), iid=g.get('id')) 
            
        self.set_estado_gestor_alumnos(False)

    def on_grupo_select(self, event):
        """Se activa al seleccionar un grupo del Treeview principal"""
        sel = self.tree_grupos.selection()
        if not sel:
            self.set_estado_gestor_alumnos(False)
            return
            
        item = self.tree_grupos.item(sel[0])
        grupo_id = item['values'][0] 
        
        grupo_data = next((g for g in self.db_grupo.listar_grupos_detallado() if g['id'] == grupo_id), None)
        
        if not grupo_data:
            messagebox.showerror("Error", "No se pudieron cargar los detalles del grupo")
            self.set_estado_gestor_alumnos(False)
            return

        self.grupo_seleccionado_id = grupo_id
        self.grupo_seleccionado_carrera_id = grupo_data.get('carrera_id')

        self.set_estado_gestor_alumnos(True)
        self.cargar_alumnos_disponibles()
        self.cargar_alumnos_inscritos()

    def cargar_alumnos_disponibles(self):
        """Carga el combo de alumnos que pueden inscribirse a este grupo"""
        self.var_alumno_agregar.set('')
        self.alumnos_disponibles_map.clear()
        
        if not self.grupo_seleccionado_id or not self.grupo_seleccionado_carrera_id:
            self.combo_alumnos_disponibles['values'] = []
            return

        alumnos = self.db_alumno.get_alumnos_disponibles_para_grupo(
            self.grupo_seleccionado_carrera_id, 
            self.grupo_seleccionado_id
        )
        
        display_names = []
        for a in alumnos:
            display = f"{a['matricula']} - {a['nombre_completo']}"
            self.alumnos_disponibles_map[display] = a['alumno_id']
            display_names.append(display)
            
        if not display_names:
            display_names = ["No hay alumnos de esta carrera disponibles"]
            
        self.combo_alumnos_disponibles['values'] = display_names

    def cargar_alumnos_inscritos(self):
        """Carga la lista de alumnos ya inscritos en este grupo"""
        for row in self.tree_alumnos_inscritos.get_children():
            self.tree_alumnos_inscritos.delete(row)
        
        if not self.grupo_seleccionado_id:
            return

        inscritos = self.db_alumno.get_alumnos_por_grupo(self.grupo_seleccionado_id)
        
        for i in inscritos:
            self.tree_alumnos_inscritos.insert('', 'end', values=(
                i.get('inscripcion_id'),
                i.get('matricula'),
                i.get('nombre_completo')
            ))

    def agregar_alumno(self):
        alumno_display = self.var_alumno_agregar.get()
        if not alumno_display or alumno_display == "No hay alumnos de esta carrera disponibles":
            messagebox.showwarning("Validación", "Selecciona un alumno válido")
            return
            
        alumno_id = self.alumnos_disponibles_map.get(alumno_display)
        if not alumno_id or not self.grupo_seleccionado_id:
            messagebox.showerror("Error", "No se pudo encontrar el ID del alumno o del grupo")
            return

        ok, msg = self.db_alumno.admin_inscribir_alumno(alumno_id, self.grupo_seleccionado_id)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_alumnos_disponibles()
            self.cargar_alumnos_inscritos()
            self.aplicar_filtros() 
        else:
            messagebox.showerror("Error", msg)

    def quitar_alumno(self):
        sel = self.tree_alumnos_inscritos.selection()
        if not sel:
            messagebox.showwarning("Validación", "Selecciona un alumno de la lista de inscritos")
            return
            
        values = self.tree_alumnos_inscritos.item(sel[0], 'values')
        inscripcion_id = int(values[0])
        nombre_alumno = str(values[2])
        
        if messagebox.askyesno("Confirmar Baja", f"¿Dar de baja a {nombre_alumno} de este grupo?"):
            ok, msg = self.db_alumno.admin_dar_baja_materia(inscripcion_id)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_alumnos_disponibles()
                self.cargar_alumnos_inscritos()
                self.aplicar_filtros()
            else:
                messagebox.showerror("Error", msg)