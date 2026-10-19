"""
Interfaz de Gestión de Materias
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from DB.dbMaterias import DBMateria
from conexion import ConexionDB

class MateriasUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBMateria(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # --- Variables del formulario ---
        self.var_id = tk.StringVar()
        self.var_codigo = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_creditos = tk.StringVar()
        self.var_carrera = tk.StringVar() # <-- AÑADIDO
        
        self.carreras_map: Dict[str, int] = {} # <-- AÑADIDO
        self.carreras_map_inverso: Dict[int, str] = {} # <-- AÑADIDO

        # --- Widgets del formulario ---
        self.entry_id: ttk.Entry
        self.entry_codigo: ttk.Entry
        self.entry_nombre: ttk.Entry
        self.entry_creditos: ttk.Entry
        self.combo_carrera: ttk.Combobox # <-- AÑADIDO
        
        self.search_var = tk.StringVar()
        self.tree: ttk.Treeview
        
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_baja: ttk.Button
        self.btn_cancelar: ttk.Button

        self.build_ui()
        self.cargar_carreras_combo() # <-- AÑADIDO
        self.cargar_materias()
        self.set_estado("inicio")
        
    def cargar_carreras_combo(self):
        """Carga la lista de carreras en el combobox"""
        carreras = self.db.get_carreras()
        self.carreras_map = {c['nombre']: c['id'] for c in carreras}
        self.carreras_map_inverso = {c['id']: c['nombre'] for c in carreras}
        self.combo_carrera['values'] = [''] + list(self.carreras_map.keys())

    def build_ui(self):
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        form = ttk.LabelFrame(frm_principal, text="Datos de la Materia", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Label(form, text="Código:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_codigo = ttk.Entry(form, textvariable=self.var_codigo, width=30)
        self.entry_codigo.grid(row=1, column=1, sticky='ew', pady=2)
        ttk.Label(form, text="Nombre materia:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre, width=30)
        self.entry_nombre.grid(row=2, column=1, sticky='ew', pady=2)
        ttk.Label(form, text="Créditos:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_creditos = ttk.Entry(form, textvariable=self.var_creditos, width=30)
        self.entry_creditos.grid(row=3, column=1, sticky='ew', pady=2)

        # --- Carrera (AÑADIDO) ---
        ttk.Label(form, text="Carrera:").grid(row=4, column=0, sticky='w', pady=2)
        self.combo_carrera = ttk.Combobox(
            form, textvariable=self.var_carrera, state='readonly', width=28
        )
        self.combo_carrera.grid(row=4, column=1, sticky='ew', pady=2)

        # --- Botones (fila movida) ---
        btns = ttk.Frame(form)
        btns.grid(row=5, column=0, columnspan=2, pady=(15, 0)) # <-- Fila 5

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_materia, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_materia, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_materia, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_materia, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns, text="Baja", command=self.eliminar_materia, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        # === LISTADO ===
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Ingrese codigo materia:").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=20).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_materias).pack(side='left', padx=6)

        # --- Treeview (AÑADIDO 'carrera') ---
        cols = ("id", "codigo", "nombre", "creditos", "carrera")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre Materia")
        self.tree.heading("creditos", text="Créditos")
        self.tree.heading("carrera", text="Carrera") # <-- AÑADIDO
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("nombre", width=250)
        self.tree.column("creditos", width=80, anchor="center")
        self.tree.column("carrera", width=150) # <-- AÑADIDO
        
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        if modo == "nuevo": estado = "normal"
        elif modo == "editar": estado = "normal"
        else: estado = "disabled" # "inicio", "buscar", "salvar", etc.

        self.btn_nuevo.config(state="normal" if modo not in ("nuevo", "editar") else "disabled")
        self.btn_guardar.config(state="normal" if modo == "nuevo" else "disabled")
        self.btn_editar.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_actualizar.config(state="normal" if modo == "editar" else "disabled")
        self.btn_baja.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_cancelar.config(state="normal" if modo in ("nuevo", "editar", "buscar") else "disabled")

        for entry in (self.entry_codigo, self.entry_nombre, self.entry_creditos):
            entry.config(state=estado)# type: ignore
        self.combo_carrera.config(state="readonly" if estado == "normal" else "disabled")# type: ignore

    def limpiar_form(self):
        self.var_id.set('')
        self.var_codigo.set('')
        self.var_nombre.set('')
        self.var_creditos.set('')
        self.var_carrera.set('')

    def validar_campos(self) -> bool:
        codigo = self.var_codigo.get().strip()
        nombre = self.var_nombre.get().strip()
        creditos = self.var_creditos.get().strip()
        carrera = self.var_carrera.get()

        if not codigo or not nombre or not creditos:
            messagebox.showwarning("Validación", "Código, Nombre y Créditos son campos obligatorios")
            return False
        if any(char.isdigit() for char in nombre):
            messagebox.showwarning("Validación", "El nombre de la materia no puede contener números")
            return False
        if not creditos.isdigit():
            messagebox.showwarning("Validación", "Los 'Créditos' deben ser un número entero")
            return False
        creditos_int = int(creditos)
        if creditos_int < 1 or creditos_int > 20:
            messagebox.showwarning("Validación", "Los créditos deben estar entre 1 y 20")
            return False
        if not carrera:
             messagebox.showwarning("Validación", "Debes seleccionar una carrera")
             return False
        return True

    def nuevo_materia(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_codigo.focus()

    def guardar_materia(self):
        if not self.validar_campos(): return
        codigo = self.var_codigo.get().strip()
        if not self.db.validar_codigo_unico(codigo):
            messagebox.showwarning("Validación", "El código de materia ya está registrado")
            return
        
        carrera_id = self.carreras_map.get(self.var_carrera.get()) # <-- AÑADIDO
        
        ok, msg = self.db.crear_materia(
            codigo=codigo,
            nombre=self.var_nombre.get().strip(),
            creditos=int(self.var_creditos.get().strip()),
            carrera_id=carrera_id # <-- AÑADIDO
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_materias()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_materia(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero una materia")
            return
        self.set_estado("editar")
        self.entry_codigo.focus()

    def actualizar_materia(self):
        if not self.var_id.get(): return
        if not self.validar_campos(): return

        materia_id = int(self.var_id.get())
        codigo = self.var_codigo.get().strip()

        if not self.db.validar_codigo_unico(codigo, materia_id):
            messagebox.showwarning("Validación", "El código de materia ya está registrado")
            return

        carrera_id = self.carreras_map.get(self.var_carrera.get()) # <-- AÑADIDO

        ok, msg = self.db.actualizar_materia(
            materia_id=materia_id,
            codigo=codigo,
            nombre=self.var_nombre.get().strip(),
            creditos=int(self.var_creditos.get().strip()),
            carrera_id=carrera_id # <-- AÑADIDO
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_materias()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_materia(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas dar de baja (eliminar) la materia {self.var_nombre.get()}?"):
            ok, msg = self.db.eliminar_materia(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_materias()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cargar_materias(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.listar_materias()
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('codigo', ''),
                r.get('nombre', ''),
                r.get('creditos', ''),
                r.get('carrera_nombre', '') # <-- AÑADIDO
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 5: return # <-- Cambiado a 5
        
        self.var_id.set(str(values[0]))
        self.var_codigo.set(str(values[1]))
        self.var_nombre.set(str(values[2]))
        self.var_creditos.set(str(values[3]))
        self.var_carrera.set(str(values[4])) # <-- AÑADIDO
        
        self.set_estado("buscar")

    def buscar(self):
        q = self.search_var.get().strip()
        if not q:
            self.cargar_materias()
            return
        materia = self.db.buscar_materia_por_codigo(q)
        if not materia:
            messagebox.showinfo("Búsqueda", "Materia no encontrada")
            return
        
        self.var_id.set(materia['id'])
        self.var_codigo.set(materia.get('codigo', ''))
        self.var_nombre.set(materia.get('nombre', ''))
        self.var_creditos.set(materia.get('creditos', ''))
        
        # --- AÑADIDO ---
        carrera_id = materia.get('carrera_id')
        self.var_carrera.set(self.carreras_map_inverso.get(carrera_id, ''))
        
        self.set_estado("buscar")