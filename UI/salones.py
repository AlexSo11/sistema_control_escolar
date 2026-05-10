"""
Módulo de Gestión de Salones - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from DB.dbSalones import DBSalon 
from conexion import ConexionDB

class SalonesUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBSalon(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # --- Variables del formulario ---
        self.var_id = tk.StringVar()
        self.var_numero = tk.StringVar()
        self.var_capacidad = tk.StringVar()
        self.var_ubicacion = tk.StringVar()
        
        # --- Widgets del formulario ---
        self.entry_id: ttk.Entry
        self.entry_numero: ttk.Entry
        self.entry_capacidad: ttk.Entry
        self.entry_ubicacion: ttk.Entry
        
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
        self.cargar_salones()
        self.set_estado("inicio")

    def build_ui(self):
        """Construye la interfaz gráfica"""
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # === FORMULARIO ===
        form = ttk.LabelFrame(frm_principal, text="Datos del Salón", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Nombre/Número salón:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_numero = ttk.Entry(form, textvariable=self.var_numero, width=30)
        self.entry_numero.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Capacidad:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_capacidad = ttk.Entry(form, textvariable=self.var_capacidad, width=30)
        self.entry_capacidad.grid(row=2, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Ubicación (Edificio):").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_ubicacion = ttk.Entry(form, textvariable=self.var_ubicacion, width=30)
        self.entry_ubicacion.grid(row=3, column=1, sticky='ew', pady=2)

        # === BOTONES ===
        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=2, pady=(15, 0))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_salon, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_salon, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_salon, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_salon, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns, text="Baja", command=self.eliminar_salon, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        # === LISTADO ===
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Ingrese código/número salón:").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=20).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_salones).pack(side='left', padx=6)

        cols = ("id", "numero", "capacidad", "ubicacion")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("numero", text="Número")
        self.tree.heading("capacidad", text="Capacidad")
        self.tree.heading("ubicacion", text="Ubicación")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("numero", width=100, anchor="center")
        self.tree.column("capacidad", width=80, anchor="center")
        self.tree.column("ubicacion", width=300)
        
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

        for entry in (self.entry_numero, self.entry_capacidad, self.entry_ubicacion):
            entry.config(state=estado)

    def limpiar_form(self):
        self.var_id.set('')
        self.var_numero.set('')
        self.var_capacidad.set('')
        self.var_ubicacion.set('')

    def validar_campos(self) -> bool:
        numero = self.var_numero.get().strip()
        capacidad = self.var_capacidad.get().strip()

        if not numero or not capacidad:
            messagebox.showwarning("Validación", "Número y Capacidad son campos obligatorios")
            return False
        if not capacidad.isdigit():
            messagebox.showwarning("Validación", "La 'Capacidad' debe ser un número entero")
            return False
        capacidad_int = int(capacidad)
        if capacidad_int < 10 or capacidad_int > 200:
            messagebox.showwarning("Validación", 
                "La capacidad debe estar entre 10 y 200 estudiantes")
            return False
        return True
    
    def campos_obligatorios_llenos(self) -> bool:
        """Verifica que los campos obligatorios no estén vacíos"""
        campos = [self.var_nombre.get().strip(), self.var_email.get().strip()]
        if any(not campo for campo in campos):
            messagebox.showwarning("Validación", "Complete todos los campos obligatorios")
            return False
        return True

    def nuevo_salon(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_numero.focus()

    def guardar_salon(self):
        if not self.validar_campos(): return
        numero = self.var_numero.get().strip()
        if not self.db.validar_numero_unico(numero):
            messagebox.showwarning("Validación", "El número de salón ya está registrado")
            return
        
        ok, msg = self.db.crear_salon(
            numero=numero,
            capacidad=int(self.var_capacidad.get().strip()),
            ubicacion=self.var_ubicacion.get().strip()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_salones()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_salon(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un salón")
            return
        self.set_estado("editar")
        self.entry_numero.focus()

    def actualizar_salon(self):
        if not self.var_id.get(): return
        if not self.validar_campos(): return

        salon_id = int(self.var_id.get())
        numero = self.var_numero.get().strip()

        if not self.db.validar_numero_unico(numero, salon_id):
            messagebox.showwarning("Validación", "El número de salón ya está registrado")
            return

        ok, msg = self.db.actualizar_salon(
            salon_id=salon_id,
            numero=numero,
            capacidad=int(self.var_capacidad.get().strip()),
            ubicacion=self.var_ubicacion.get().strip()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_salones()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_salon(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas dar de baja (eliminar) el salón {self.var_numero.get()}?"):
            ok, msg = self.db.eliminar_salon(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_salones()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cargar_salones(self):
        """Recarga el treeview principal"""
        self.aplicar_filtro()
        
    def aplicar_filtro(self):
        """Filtra el treeview por número de salón"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        q = self.search_var.get().strip()
        if not q:
            rows = self.db.listar_salones()
        else:
            rows = self.db.buscar_salon_por_numero(q)
            
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('numero', ''),
                r.get('capacidad', ''),
                r.get('ubicacion', '')
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 4: return
        
        self.var_id.set(str(values[0]))
        self.var_numero.set(str(values[1]))
        self.var_capacidad.set(str(values[2]))
        self.var_ubicacion.set(str(values[3]))
        self.set_estado("buscar")

    def buscar(self):
        """Se activa con el botón buscar, usa la misma lógica que aplicar_filtro"""
        self.aplicar_filtro()