"""
Módulo de Gestión de Alumno "Inscripciones" - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from DB.dbAlumnoVista import DBAlumnoVista
from conexion import ConexionDB

class AlumnoInscripcionUI:
    def __init__(self, parent: ttk.Frame, usuario_actual: Dict[str, Any], conexion: ConexionDB):
        self.parent = parent # 'parent' es la PESTAÑA (tab_inscripciones)
        self.usuario_actual = usuario_actual
        self.con = conexion
        self.db = DBAlumnoVista(self.con)
        
        self.alumno_id = self.usuario_actual['id']
        self.alumno_carrera_id = self.usuario_actual.get('carrera_id')
        
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self._crear_tab_inscripciones()
        
        if self.alumno_carrera_id:
            self.cargar_grupos_disponibles()
            self.cargar_mis_inscripciones()
        else:
            messagebox.showerror("Error de Perfil", "No se pudo identificar tu carrera. Las inscripciones no funcionarán.")

    def _crear_tab_inscripciones(self):
        frame_disponibles = ttk.LabelFrame(self.frame, text="Grupos Disponibles para tu Carrera", padding=10)
        frame_disponibles.pack(fill='both', expand=True, pady=(0, 10))

        cols_disp = ('codigo', 'materia', 'maestro', 'horario', 'cupos')
        self.tree_disponibles = ttk.Treeview(frame_disponibles, columns=cols_disp, show='headings', height=7)
        self.tree_disponibles.heading('codigo', text='Grupo')
        self.tree_disponibles.heading('materia', text='Materia')
        self.tree_disponibles.heading('maestro', text='Maestro')
        self.tree_disponibles.heading('horario', text='Horario')
        self.tree_disponibles.heading('cupos', text='Disp.')
        
        self.tree_disponibles.column('codigo', width=80)
        self.tree_disponibles.column('materia', width=200)
        self.tree_disponibles.column('maestro', width=200)
        self.tree_disponibles.column('horario', width=180)
        self.tree_disponibles.column('cupos', width=50, anchor='center')
        
        sb_disp = ttk.Scrollbar(frame_disponibles, orient='vertical', command=self.tree_disponibles.yview)
        self.tree_disponibles.configure(yscrollcommand=sb_disp.set)
        sb_disp.pack(side='right', fill='y')
        self.tree_disponibles.pack(side='left', fill='both', expand=True)
        
        btn_inscribir = ttk.Button(frame_disponibles, text="Inscribir\nSeleccionado", command=self.inscribir_materia_seleccionada)
        btn_inscribir.pack(side='right', fill='y', padx=(10, 0))

        frame_inscritos = ttk.LabelFrame(self.frame, text="Mis Materias Inscritas (Solo Visualización)", padding=10)
        frame_inscritos.pack(fill='both', expand=True, pady=(10, 0))
        
        cols_insc = ('codigo', 'materia', 'maestro', 'horario', 'salon', 'estado')
        self.tree_inscritas = ttk.Treeview(frame_inscritos, columns=cols_insc, show='headings', height=7)
        self.tree_inscritas.heading('codigo', text='Grupo')
        self.tree_inscritas.heading('materia', text='Materia')
        self.tree_inscritas.heading('maestro', text='Maestro')
        self.tree_inscritas.heading('horario', text='Horario')
        self.tree_inscritas.heading('salon', text='Salón')
        self.tree_inscritas.heading('estado', text='Estado')
        
        self.tree_inscritas.column('codigo', width=80)
        self.tree_inscritas.column('materia', width=200)
        self.tree_inscritas.column('maestro', width=200)
        self.tree_inscritas.column('horario', width=180)
        self.tree_inscritas.column('salon', width=80)
        self.tree_inscritas.column('estado', width=80)
        
        sb_insc = ttk.Scrollbar(frame_inscritos, orient='vertical', command=self.tree_inscritas.yview)
        self.tree_inscritas.configure(yscrollcommand=sb_insc.set)
        sb_insc.pack(side='right', fill='y')
        self.tree_inscritas.pack(fill='both', expand=True)

    def cargar_grupos_disponibles(self):
        for row in self.tree_disponibles.get_children():
            self.tree_disponibles.delete(row)
            
        if not self.alumno_carrera_id:
            return
            
        grupos = self.db.get_grupos_disponibles(self.alumno_id, self.alumno_carrera_id)
        for g in grupos:
            self.tree_disponibles.insert('', 'end', values=(
                g.get('grupo_codigo'),
                g.get('materia_nombre'),
                g.get('maestro_nombre', 'N/A'),
                g.get('horario_desc', 'N/A'),
                g.get('cupos_disponibles')
            ), iid=g.get('grupo_id'))

    def cargar_mis_inscripciones(self):
        for row in self.tree_inscritas.get_children():
            self.tree_inscritas.delete(row)
            
        grupos = self.db.get_mis_inscripciones(self.alumno_id)
        for g in grupos:
            self.tree_inscritas.insert('', 'end', values=(
                g.get('grupo_codigo'),
                g.get('materia_nombre'),
                g.get('maestro_nombre', 'N/A'),
                g.get('horario_desc', 'N/A'),
                g.get('salon_numero', 'N/A'),
                g.get('estado')
            ))
            
    def inscribir_materia_seleccionada(self):
        sel = self.tree_disponibles.selection()
        if not sel:
            messagebox.showwarning("Selección", "Por favor, selecciona un grupo de la lista de disponibles.")
            return
            
        grupo_id_real = int(sel[0]) 
        values = self.tree_disponibles.item(sel[0], 'values')
        grupo_codigo = values[0]
        materia_nombre = values[1]

        if messagebox.askyesno("Confirmar Inscripción", f"¿Seguro que deseas inscribirte a:\n\n{materia_nombre} (Grupo: {grupo_codigo})?"):
            ok, msg = self.db.inscribir_grupo(self.alumno_id, grupo_id_real)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos_disponibles()
                self.cargar_mis_inscripciones()
                
                try:
                    notebook = self.parent.master
                    for tab_id in notebook.tabs():
                        if notebook.tab(tab_id, "text") == "Mi Horario":
                            tab_widget = self.parent.nametowidget(tab_id)
                            tab_widget.event_generate("<<RecargarHorario>>")
                            break
                except Exception as e:
                    print(f"No se pudo refrescar el horario visual: {e}")

            else:
                messagebox.showerror("Error", msg)