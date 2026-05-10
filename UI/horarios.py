"""
Módulo de Gestión de Horarios - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from DB.dbHorarios import DBHorario
from conexion import ConexionDB
import re
from datetime import datetime, time, timedelta

class HorariosUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBHorario(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # --- Variables del formulario ---
        self.var_id = tk.StringVar()
        self.var_dia = tk.StringVar()
        self.var_hora_inicio = tk.StringVar()
        self.var_hora_fin = tk.StringVar()
        self.var_turno = tk.StringVar()
        
        # --- Widgets del formulario ---
        self.entry_id: ttk.Entry
        self.combo_dia: ttk.Combobox
        self.entry_hora_inicio: ttk.Entry
        self.entry_hora_fin: ttk.Entry
        self.entry_turno: ttk.Entry
        
        # --- Widgets de lista y búsqueda ---
        self.search_var = tk.StringVar()
        self.tree: ttk.Treeview
        
        # --- Botones ---
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_baja: ttk.Button
        self.btn_cancelar: ttk.Button

        # Construir interfaz
        self.build_ui()
        self.cargar_horarios()
        self.set_estado("inicio")

    def build_ui(self):
        """Construye la interfaz gráfica"""
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # FORMULARIO 
        form = ttk.LabelFrame(frm_principal, text="Datos del Horario", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Día:").grid(row=1, column=0, sticky='w', pady=2)
        self.combo_dia = ttk.Combobox(
            form, textvariable=self.var_dia, state='readonly', width=28,
            values=['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
        )
        self.combo_dia.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Hora Inicio (HH:MM):").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_hora_inicio = ttk.Entry(form, textvariable=self.var_hora_inicio, width=30)
        self.entry_hora_inicio.grid(row=2, column=1, sticky='ew', pady=2)
        self.entry_hora_inicio.bind("<FocusOut>", self._determinar_turno)

        ttk.Label(form, text="Hora Fin (HH:MM):").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_hora_fin = ttk.Entry(form, textvariable=self.var_hora_fin, width=30)
        self.entry_hora_fin.grid(row=3, column=1, sticky='ew', pady=2)
        
        ttk.Label(form, text="Turno:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_turno = ttk.Entry(
            form, textvariable=self.var_turno, state='readonly', width=30
        )
        self.entry_turno.grid(row=4, column=1, sticky='ew', pady=2)

        # === BOTONES ===
        btns = ttk.Frame(form)
        btns.grid(row=5, column=0, columnspan=2, pady=(15, 0))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_horario, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_horario, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_horario, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_horario, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns, text="Baja", command=self.eliminar_horario, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        # LISTADO
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar por ID:").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=10).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_horarios).pack(side='left', padx=6)

        cols = ("id", "dia_semana", "hora_inicio", "hora_fin", "turno")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("dia_semana", text="Día")
        self.tree.heading("hora_inicio", text="Inicio")
        self.tree.heading("hora_fin", text="Fin")
        self.tree.heading("turno", text="Turno")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("dia_semana", width=150)
        self.tree.column("hora_inicio", width=100, anchor="center")
        self.tree.column("hora_fin", width=100, anchor="center")
        self.tree.column("turno", width=150)
        
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        if modo == "nuevo": 
            estado_campos = "normal"
            estado_turno = "readonly"
        elif modo == "editar": 
            estado_campos = "normal"
            estado_turno = "readonly"
        else: 
            estado_campos = "disabled"
            estado_turno = "disabled"

        self.btn_nuevo.config(state="normal" if modo not in ("nuevo", "editar") else "disabled")
        self.btn_guardar.config(state="normal" if modo == "nuevo" else "disabled")
        self.btn_editar.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_actualizar.config(state="normal" if modo == "editar" else "disabled")
        self.btn_baja.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_cancelar.config(state="normal" if modo in ("nuevo", "editar", "buscar") else "disabled")

        self.entry_hora_inicio.config(state=estado_campos)# type: ignore
        self.entry_hora_fin.config(state=estado_campos)# type: ignore
        self.combo_dia.config(state="readonly" if estado_campos == "normal" else "disabled")# type: ignore
        self.entry_turno.config(state=estado_turno)# type: ignore

    def limpiar_form(self):
        self.var_id.set('')
        self.var_dia.set('')
        self.var_hora_inicio.set('HH:MM')
        self.var_hora_fin.set('HH:MM')
        self.var_turno.set('')

    def _parse_time(self, time_str: str) -> Optional[time]:
        """Intenta parsear HH:MM:SS o HH:MM"""
        try:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            try:
                return datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                return None

    def _determinar_turno(self, event=None):
        """Determina el turno basado en la hora de inicio con validaciones"""
        hora_inicio_str = self.var_hora_inicio.get()
        t_inicio = self._parse_time(hora_inicio_str)
        
        if not t_inicio:
            self.var_turno.set("")
            return
        
        # Validar que esté en horario escolar
        if t_inicio < time(7, 0):
            messagebox.showwarning("Validación", 
                "Las clases no pueden iniciar antes de las 7:00 AM")
            self.var_hora_inicio.set("07:00")
            self.var_turno.set("")
            return
        
        if t_inicio >= time(21, 0):
            messagebox.showwarning("Validación", 
                "Las clases no pueden iniciar después de las 9:00 PM")
            self.var_hora_inicio.set("20:00")
            self.var_turno.set("")
            return
        
        # Determinar turno
        if t_inicio < time(14, 0):
            self.var_turno.set("Matutino")
        elif t_inicio < time(20, 0):
            self.var_turno.set("Vespertino")
        else:
            self.var_turno.set("Nocturno")

    def validar_campos(self) -> bool:
        """Valida formato y duración de 4 horas"""
        dia = self.var_dia.get()
        turno = self.var_turno.get()
        hora_inicio_str = self.var_hora_inicio.get().strip()
        hora_fin_str = self.var_hora_fin.get().strip()
        
        if not dia or not turno or not hora_inicio_str or not hora_fin_str:
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return False
        
        t_inicio = self._parse_time(hora_inicio_str)
        t_fin = self._parse_time(hora_fin_str)

        # Validar rango horario permitido (7:00 AM - 9:00 PM)
        if t_inicio < time(7, 0) or t_inicio >= time(21, 0):
            messagebox.showwarning("Validación", 
                "La hora de inicio debe estar entre las 7:00 AM y las 9:00 PM")
            return False

        if t_fin > time(21, 0) or t_fin <= time(7, 0):
            messagebox.showwarning("Validación", 
                "La hora de fin no puede ser después de las 9:00 PM")
            return False
        
        if not t_inicio or not t_fin:
            messagebox.showwarning("Validación", "El formato de hora debe ser HH:MM o HH:MM:SS")
            return False
        
        if t_fin <= t_inicio:
            messagebox.showwarning("Validación", "La hora de fin debe ser mayor a la hora de inicio")
            return False
            
        hoy = datetime(2000, 1, 1)
        dt_inicio = datetime.combine(hoy, t_inicio)
        dt_fin = datetime.combine(hoy, t_fin)
        duracion = dt_fin - dt_inicio
        
        if duracion > timedelta(hours=4):
            messagebox.showwarning("Validación", "La duración de la clase no puede ser mayor a 4 horas")
            return False
            
        return True
    
    def campos_obligatorios_llenos(self) -> bool:
        """Verifica que los campos obligatorios no estén vacíos"""
        campos = [self.var_nombre.get().strip(), self.var_email.get().strip()]
        if any(not campo for campo in campos):
            messagebox.showwarning("Validación", "Complete todos los campos obligatorios")
            return False
        return True

    def nuevo_horario(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.combo_dia.focus()

    def guardar_horario(self):
        if not self.validar_campos(): return
        
        dia = self.var_dia.get()
        hora_inicio = self.var_hora_inicio.get().strip()
        hora_fin = self.var_hora_fin.get().strip()
        
        if not self.db.validar_horario_unico(dia, hora_inicio, hora_fin):
            messagebox.showwarning("Duplicado", "Este horario (Día + Hora Inicio + Hora Fin) ya existe.")
            return

        ok, msg = self.db.crear_horario(
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            turno=self.var_turno.get()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_horarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_horario(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un horario")
            return
        self.set_estado("editar")
        self.combo_dia.focus()

    def actualizar_horario(self):
        if not self.var_id.get(): return
        if not self.validar_campos(): return

        horario_id = int(self.var_id.get())
        dia = self.var_dia.get()
        hora_inicio = self.var_hora_inicio.get().strip()
        hora_fin = self.var_hora_fin.get().strip()

        if not self.db.validar_horario_unico(dia, hora_inicio, hora_fin, horario_id):
            messagebox.showwarning("Duplicado", "Este horario (Día + Hora Inicio + Hora Fin) ya existe.")
            return

        ok, msg = self.db.actualizar_horario(
            horario_id=horario_id,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            turno=self.var_turno.get()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_horarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_horario(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas eliminar el horario ID: {self.var_id.get()}?"):
            ok, msg = self.db.eliminar_horario(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_horarios()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cargar_horarios(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.listar_horarios()
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('dia_semana', ''),
                str(r.get('hora_inicio', '')),
                str(r.get('hora_fin', '')),
                r.get('turno', '')
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 5: return
        
        self.var_id.set(str(values[0]))
        self.var_dia.set(str(values[1]))
        self.var_hora_inicio.set(str(values[2]))
        self.var_hora_fin.set(str(values[3]))
        self.var_turno.set(str(values[4]))
        self.set_estado("buscar")

    def buscar(self):
        q = self.search_var.get().strip()
        if not q:
            self.cargar_horarios()
            return
        
        if not q.isdigit():
            messagebox.showwarning("Búsqueda", "La búsqueda solo se puede hacer por ID numérico.")
            return
            
        horario = self.db.buscar_horario_por_id(int(q))
        if not horario:
            messagebox.showinfo("Búsqueda", "Horario no encontrado")
            return
        
        self.var_id.set(horario['id'])
        self.var_dia.set(horario.get('dia_semana', ''))
        self.var_hora_inicio.set(str(horario.get('hora_inicio', '')))
        self.var_hora_fin.set(str(horario.get('hora_fin', '')))
        self.var_turno.set(horario.get('turno', ''))
        self.set_estado("buscar")