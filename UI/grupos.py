"""
Interfaz de Gestión de Grupos
Correcciones: implementar buscar(), robustecer parsing de combo values y validaciones.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from DB.dbGrupos import DBGrupo
from conexion import ConexionDB
import re

class GruposUI:
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBGrupo(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        if not usuario_actual or usuario_actual.get('rol') != 'ADMIN':
            ttk.Label(
                self.frame,
                text="Acceso denegado: Solo administradores pueden gestionar grupos",
                font=("Segoe UI", 12),
                foreground="red"
            ).pack(expand=True)
            return

        # Variables del formulario
        self.var_id = tk.StringVar()
        self.var_codigo = tk.StringVar()
        self.var_cupos = tk.StringVar(value='30')
        self.var_carrera = tk.StringVar()
        self.var_materia = tk.StringVar()
        self.var_maestro = tk.StringVar()
        self.var_salon = tk.StringVar()
        self.var_horario = tk.StringVar()
        self.search_var = tk.StringVar()

        # Mapas para combos
        self.carreras_map: Dict[str, int] = {}
        self.materias_map: Dict[str, int] = {}
        self.maestros_map: Dict[str, int] = {}
        self.salones_map: Dict[str, int] = {}
        self.horarios_map: Dict[str, int] = {}

        # --- Widgets ---
        self.combo_carrera: ttk.Combobox
        self.combo_materia: ttk.Combobox
        self.combo_maestro: ttk.Combobox
        self.combo_salon: ttk.Combobox
        self.combo_horario: ttk.Combobox
        self.entry_id: ttk.Entry
        self.entry_codigo: ttk.Entry
        self.entry_cupos: ttk.Entry
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_baja: ttk.Button
        self.btn_cancelar: ttk.Button
        self.tree: ttk.Treeview

        # Construir interfaz
        self.build_ui()
        self.cargar_combos()
        self.cargar_grupos()
        self.set_estado("inicio")

    def _parse_combo_value(self, value_str: str) -> Optional[int]:
        """Extrae el ID de un string 'ID - Nombre'"""
        try:
            return int(value_str.split(' - ')[0])
        except (ValueError, IndexError, AttributeError):
            return None

    def build_ui(self):
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # === FORMULARIO ===
        form = ttk.LabelFrame(frm_principal, text="Datos del Grupo", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Código Grupo:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_codigo = ttk.Entry(form, textvariable=self.var_codigo, width=30)
        self.entry_codigo.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Carrera:").grid(row=2, column=0, sticky='w', pady=2)
        self.combo_carrera = ttk.Combobox(form, textvariable=self.var_carrera, state='readonly', width=28)
        self.combo_carrera.grid(row=2, column=1, sticky='ew', pady=2)
        self.combo_carrera.bind('<<ComboboxSelected>>', self.cargar_materias)

        ttk.Label(form, text="Materia:").grid(row=3, column=0, sticky='w', pady=2)
        self.combo_materia = ttk.Combobox(form, textvariable=self.var_materia, state='readonly', width=28)
        self.combo_materia.grid(row=3, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Maestro:").grid(row=4, column=0, sticky='w', pady=2)
        self.combo_maestro = ttk.Combobox(form, textvariable=self.var_maestro, state='readonly', width=28)
        self.combo_maestro.grid(row=4, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Salón:").grid(row=5, column=0, sticky='w', pady=2)
        self.combo_salon = ttk.Combobox(form, textvariable=self.var_salon, state='readonly', width=28)
        self.combo_salon.grid(row=5, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Horario:").grid(row=6, column=0, sticky='w', pady=2)
        self.combo_horario = ttk.Combobox(form, textvariable=self.var_horario, state='readonly', width=28)
        self.combo_horario.grid(row=6, column=1, sticky='ew', pady=2)
        
        ttk.Label(form, text="Cupos:").grid(row=7, column=0, sticky='w', pady=2)
        self.entry_cupos = ttk.Entry(form, textvariable=self.var_cupos, width=30)
        self.entry_cupos.grid(row=7, column=1, sticky='ew', pady=2)

        # === BOTONES ===
        btns = ttk.Frame(form)
        btns.grid(row=8, column=0, columnspan=2, pady=(15, 0))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_grupo, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_grupo, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_grupo, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_grupo, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns, text="Baja", command=self.eliminar_grupo, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        # === LISTADO ===
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar (Código):").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=20).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_grupos).pack(side='left', padx=6)

        cols = ("id", "codigo", "materia", "carrera", "cupos", "disponibles")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("materia", text="Materia")
        self.tree.heading("carrera", text="Carrera")
        self.tree.heading("cupos", text="Cupos")
        self.tree.heading("disponibles", text="Disp.")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("codigo", width=100)
        self.tree.column("materia", width=200)
        self.tree.column("carrera", width=200)
        self.tree.column("cupos", width=60, anchor="center")
        self.tree.column("disponibles", width=60, anchor="center")
        
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        if modo == "nuevo": estado = "normal"
        elif modo == "editar": estado = "normal"
        else: estado = "disabled"

        self.btn_nuevo.config(state="normal" if modo not in ("nuevo", "editar") else "disabled")
        self.btn_guardar.config(state="normal" if modo == "nuevo" else "disabled")
        self.btn_editar.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_actualizar.config(state="normal" if modo == "editar" else "disabled")
        self.btn_baja.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_cancelar.config(state="normal" if modo in ("nuevo", "editar", "buscar") else "disabled")

        self.entry_codigo.config(state=estado)# type: ignore
        self.entry_cupos.config(state=estado)# type: ignore
        
        combo_state = "readonly" if estado == "normal" else "disabled"
        self.combo_carrera.config(state=combo_state)# type: ignore
        self.combo_materia.config(state=combo_state)# type: ignore
        self.combo_maestro.config(state=combo_state)# type: ignore
        self.combo_salon.config(state=combo_state)# type: ignore
        self.combo_horario.config(state=combo_state)# type: ignore

    def limpiar_form(self):
        self.var_id.set('')
        self.var_codigo.set('')
        self.var_cupos.set('30')
        self.var_carrera.set('')
        self.var_materia.set('')
        self.var_maestro.set('')
        self.var_salon.set('')
        self.var_horario.set('')
        self.combo_materia['values'] = []

    def cargar_combos(self):
        """Carga los datos iniciales de todos los combobox"""
        try:
            # Carreras
            carreras = self.db.get_carreras()
            self.carreras_map = {f"{c['id']} - {c['nombre']}": c['id'] for c in carreras}
            self.combo_carrera['values'] = list(self.carreras_map.keys())
            
            # Maestros
            maestros = self.db.get_maestros()
            self.maestros_map = {f"{m['id']} - {m['nombre']}": m['id'] for m in maestros}
            self.combo_maestro['values'] = list(self.maestros_map.keys())

            # Salones
            salones = self.db.get_salones()
            self.salones_map = {f"{s['id']} - {s['numero']}": s['id'] for s in salones}
            self.combo_salon['values'] = list(self.salones_map.keys())

            # Horarios
            horarios = self.db.get_horarios()
            self.horarios_map = {f"{h['id']} - {h['horario']}": h['id'] for h in horarios}
            self.combo_horario['values'] = list(self.horarios_map.keys())
        
        except Exception as e:
            messagebox.showerror("Error al Cargar Datos", f"No se pudieron cargar los combos: {e}")

    def cargar_materias(self, event=None):
        """Carga las materias según la carrera seleccionada"""
        self.var_materia.set('')
        carrera_id = self._parse_combo_value(self.var_carrera.get())
        if not carrera_id:
            self.combo_materia['values'] = []
            return

        materias = self.db.get_materias_por_carrera(carrera_id)
        self.materias_map = {f"{m['id']} - {m['codigo']} - {m['nombre']}": m['id'] for m in materias}
        self.combo_materia['values'] = list(self.materias_map.keys())

    def validar_campos(self) -> bool:
        codigo = self.var_codigo.get().strip()
        cupos_str = self.var_cupos.get().strip()
        
        if not (codigo and cupos_str and self.var_carrera.get() and 
                self.var_materia.get() and self.var_maestro.get() and 
                self.var_salon.get() and self.var_horario.get()):
            messagebox.showwarning("Validación", "Todos los campos son obligatorios")
            return False
        
        if len(codigo) < 3 or len(codigo) > 20:
            messagebox.showwarning("Validación", 
                "El código debe tener entre 3 y 20 caracteres")
            return False
        
        if not cupos_str.isdigit() or int(cupos_str) <= 0:
            messagebox.showwarning("Validación", 
                "Los cupos deben ser un número positivo")
            return False
        
        cupos = int(cupos_str)
        if cupos < 10 or cupos > 45:
            messagebox.showwarning("Validación", 
                "Los cupos deben estar entre 10 y 45 estudiantes")
            return False
        
        return True

    def campos_obligatorios_llenos(self) -> bool:
        """Verifica que los campos obligatorios no estén vacíos"""
        campos = [self.var_nombre.get().strip(), self.var_email.get().strip()]
        if any(not campo for campo in campos):
            messagebox.showwarning("Validación", "Complete todos los campos obligatorios")
            return False
        return True

    def nuevo_grupo(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_codigo.focus()

    def guardar_grupo(self):
        if not self.validar_campos(): return
        
        try:
            codigo = self.var_codigo.get().strip()
            cupos = int(self.var_cupos.get().strip())
            carrera_id = self._parse_combo_value(self.var_carrera.get())
            materia_id = self._parse_combo_value(self.var_materia.get())
            maestro_id = self._parse_combo_value(self.var_maestro.get())
            salon_id = self._parse_combo_value(self.var_salon.get())
            horario_id = self._parse_combo_value(self.var_horario.get())
            
            if not all([carrera_id, materia_id, maestro_id, salon_id, horario_id]):
                messagebox.showerror("Error", "Error al procesar los IDs de los combos.")
                return

            ok, msg = self.db.crear_grupo(
                codigo, materia_id, carrera_id, maestro_id, 
                salon_id, horario_id, cupos
            )
            
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos()
                self.limpiar_form()
                self.set_estado("salvar")
            else:
                messagebox.showwarning("Error de Validación", msg)
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def editar_grupo(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un grupo")
            return
        self.set_estado("editar")

    def actualizar_grupo(self):
        if not self.var_id.get(): return
        if not self.validar_campos(): return
        
        try:
            grupo_id = int(self.var_id.get())
            codigo = self.var_codigo.get().strip()
            cupos = int(self.var_cupos.get().strip())
            carrera_id = self._parse_combo_value(self.var_carrera.get())
            materia_id = self._parse_combo_value(self.var_materia.get())
            maestro_id = self._parse_combo_value(self.var_maestro.get())
            salon_id = self._parse_combo_value(self.var_salon.get())
            horario_id = self._parse_combo_value(self.var_horario.get())

            if not all([carrera_id, materia_id, maestro_id, salon_id, horario_id]):
                messagebox.showerror("Error", "Error al procesar los IDs de los combos.")
                return

            ok, msg = self.db.actualizar_grupo(
                grupo_id, codigo, materia_id, carrera_id, maestro_id, 
                salon_id, horario_id, cupos
            )
            
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos()
                self.limpiar_form()
                self.set_estado("salvar")
            else:
                messagebox.showwarning("Error de Validación", msg)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def eliminar_grupo(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas eliminar el grupo {self.var_codigo.get()}?"):
            ok, msg = self.db.eliminar_grupo(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cargar_grupos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.listar_grupos()
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('codigo', ''),
                r.get('materia_nombre', ''),
                r.get('carrera_nombre', ''),
                r.get('cupos', ''),
                r.get('cupos_disponibles', '')
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        values = self.tree.item(sel[0], 'values')
        if not values: return
        
        grupo_id = int(values[0])
        grupo = self.db.buscar_grupo_por_id(grupo_id)
        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo.")
            return

        self.var_id.set(grupo.get('id', ''))
        self.var_codigo.set(grupo.get('codigo', ''))
        self.var_cupos.set(grupo.get('cupos', ''))
        
        # Función para encontrar y seleccionar el valor en el combo
        def seleccionar_en_combo(combo, map, key_id):
            for display_val, id_val in map.items():
                if id_val == key_id:
                    combo.set(display_val)
                    return
            combo.set('') # No se encontró

        # Cargar y seleccionar Carrera
        carrera_id = grupo.get('carrera_id')
        seleccionar_en_combo(self.combo_carrera, self.carreras_map, carrera_id)
        
        # Cargar materias de esa carrera
        self.cargar_materias()
        
        # Seleccionar Materia, Maestro, Salón, Horario
        materia_id = grupo.get('materia_id')
        seleccionar_en_combo(self.combo_materia, self.materias_map, materia_id)
        
        maestro_id = grupo.get('maestro_id')
        seleccionar_en_combo(self.combo_maestro, self.maestros_map, maestro_id)
        
        salon_id = grupo.get('salon_id')
        seleccionar_en_combo(self.combo_salon, self.salones_map, salon_id)
        
        horario_id = grupo.get('horario_id')
        seleccionar_en_combo(self.combo_horario, self.horarios_map, horario_id)
        
        self.set_estado("buscar")

    def buscar(self):
        """Busca un grupo por su código"""
        q = self.search_var.get().strip()
        if not q:
            self.cargar_grupos()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = self.db.listar_grupos() # Obtiene todos
        
        # Filtra localmente
        resultados = [r for r in rows if q.lower() in r.get('codigo', '').lower()]
        
        if not resultados:
            messagebox.showinfo("Búsqueda", "No se encontraron grupos con ese código.")
            return

        for r in resultados:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('codigo', ''),
                r.get('materia_nombre', ''),
                r.get('carrera_nombre', ''),
                r.get('cupos', ''),
                r.get('cupos_disponibles', '')
            ))