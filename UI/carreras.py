"""
Módulo de Gestión de Carreras - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from DB.dbCarreras import DBCarrera 
from conexion import ConexionDB

class CarrerasUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBCarrera(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # --- Variables del formulario ---
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        
        # --- Widgets del formulario ---
        self.entry_id: ttk.Entry
        self.entry_nombre: ttk.Entry
        self.entry_descripcion: ttk.Entry
        
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
        self.cargar_carreras()
        self.set_estado("inicio")

    def build_ui(self):
        """Construye la interfaz gráfica"""
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # FORMULARIO 
        form = ttk.LabelFrame(frm_principal, text="Datos de la Carrera", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Nombre carrera:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre, width=30)
        self.entry_nombre.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Descripción:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_descripcion = ttk.Entry(form, textvariable=self.var_descripcion, width=30)
        self.entry_descripcion.grid(row=2, column=1, sticky='ew', pady=2)

        # BOTONES 
        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=2, pady=(15, 0)) # Fila cambiada

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_carrera, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_carrera, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_carrera, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_carrera, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns, text="Baja", command=self.eliminar_carrera, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        # LISTADO
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar por nombre:").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=20).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_carreras).pack(side='left', padx=6)

        cols = ("id", "nombre", "descripcion")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre Carrera")
        self.tree.heading("descripcion", text="Descripción")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("descripcion", width=350)
        
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

        for entry in (self.entry_nombre, self.entry_descripcion):
            entry.config(state=estado)

    def limpiar_form(self):
        self.var_id.set('')
        self.var_nombre.set('')
        self.var_descripcion.set('')

    def validar_campos(self) -> bool:
        """Valida que los campos no estén vacíos y que no contengan números"""
        nombre = self.var_nombre.get().strip()
        descripcion = self.var_descripcion.get().strip()

        if not nombre or not descripcion:
            messagebox.showwarning("Validación", "Nombre y Descripción son campos obligatorios")
            return False
            
        # Revisa si hay algún dígito (número) en el string
        if any(char.isdigit() for char in nombre):
            messagebox.showwarning("Validación", "El campo 'Nombre' no puede contener números.")
            return False
            
        if any(char.isdigit() for char in descripcion):
            messagebox.showwarning("Validación", "El campo 'Descripción' no puede contener números.")
            return False
            
        return True

    def nuevo_carrera(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_nombre.focus()

    def guardar_carrera(self):
        
        if not self.validar_campos(): return
        
        nombre = self.var_nombre.get().strip()
        if not self.db.validar_nombre_unico(nombre):
            messagebox.showwarning("Validación", "El nombre de la carrera ya está registrado")
            return
        
        ok, msg = self.db.crear_carrera(
            nombre=nombre,
            descripcion=self.var_descripcion.get().strip()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_carreras()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_carrera(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero una carrera")
            return
        self.set_estado("editar")
        self.entry_nombre.focus()

    def actualizar_carrera(self):
        if not self.var_id.get(): return
        # La validación de campos ahora revisa si hay números
        if not self.validar_campos(): return

        carrera_id = int(self.var_id.get())
        nombre = self.var_nombre.get().strip()

        if not self.db.validar_nombre_unico(nombre, carrera_id):
            messagebox.showwarning("Validación", "El nombre de la carrera ya está registrado")
            return

        ok, msg = self.db.actualizar_carrera(
            carrera_id=carrera_id,
            nombre=nombre,
            descripcion=self.var_descripcion.get().strip()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_carreras()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_carrera(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas dar de baja (eliminar) la carrera {self.var_nombre.get()}?"):
            ok, msg = self.db.eliminar_carrera(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_carreras()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cargar_carreras(self):
        """Recarga el treeview principal"""
        self.aplicar_filtro()
        
    def aplicar_filtro(self):
        """Filtra el treeview por nombre"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        q = self.search_var.get().strip()
        if not q:
            rows = self.db.listar_carreras()
        else:
            rows = self.db.buscar_carrera_por_nombre(q)
            
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('nombre', ''),
                r.get('descripcion', '')
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 3: return
        
        self.var_id.set(str(values[0]))
        self.var_nombre.set(str(values[1]))
        self.var_descripcion.set(str(values[2]))
        self.set_estado("buscar")

    def buscar(self):
        """Se activa con el botón buscar, usa la misma lógica que aplicar_filtro"""
        self.aplicar_filtro()