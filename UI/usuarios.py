"""
Interfaz de Gestión de Usuarios
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from DB.dbUsuarios import DBUsuario
from conexion import ConexionDB
import re

class UsuariosUI:    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBUsuario(self.con)
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # Verificar permisos de administrador
        if not usuario_actual or usuario_actual.get('rol') != 'ADMIN':
            ttk.Label(
                self.frame, 
                text="Acceso denegado: Solo administradores pueden gestionar usuarios", 
                font=("Segoe UI", 12), 
                foreground="red"
            ).pack(expand=True)
            return

        # Variables del formulario
        self.var_id = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido_paterno = tk.StringVar()
        self.var_apellido_materno = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_rol = tk.StringVar(value='ALUMNO')
        
        # Variables adicionales
        self.search_var: tk.StringVar
        self.filtro_rol: tk.StringVar
        self.tree: ttk.Treeview
        
        # Widgets del formulario
        self.entry_id: ttk.Entry
        self.entry_email: ttk.Entry
        self.entry_nombre: ttk.Entry
        self.entry_apellido_paterno: ttk.Entry
        self.entry_apellido_materno: ttk.Entry
        self.entry_telefono: ttk.Entry
        self.combo_rol: ttk.Combobox
        
        # Botones
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_eliminar: ttk.Button
        self.btn_cancelar: ttk.Button

        # Construir interfaz
        self.build_ui()
        self.cargar_usuarios()
        self.set_estado("inicio")

    def build_ui(self):
        """Construye la interfaz gráfica"""
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # === FORMULARIO ===
        form = ttk.LabelFrame(frm_principal, text="Datos del Usuario", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        # ID (solo lectura)
        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=25)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        # Email (usado como username)
        ttk.Label(form, text="Email (usuario):").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_email = ttk.Entry(form, textvariable=self.var_email, width=25)
        self.entry_email.grid(row=1, column=1, sticky='ew', pady=2)

        # Nombre
        ttk.Label(form, text="Nombre:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre, width=25)
        self.entry_nombre.grid(row=2, column=1, sticky='ew', pady=2)

        # Apellido Paterno
        ttk.Label(form, text="Apellido Paterno:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_apellido_paterno = ttk.Entry(form, textvariable=self.var_apellido_paterno, width=25)
        self.entry_apellido_paterno.grid(row=3, column=1, sticky='ew', pady=2)

        # Apellido Materno
        ttk.Label(form, text="Apellido Materno:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_apellido_materno = ttk.Entry(form, textvariable=self.var_apellido_materno, width=25)
        self.entry_apellido_materno.grid(row=4, column=1, sticky='ew', pady=2)

        # Teléfono
        ttk.Label(form, text="Teléfono:").grid(row=5, column=0, sticky='w', pady=2)
        self.entry_telefono = ttk.Entry(form, textvariable=self.var_telefono, width=25)
        self.entry_telefono.grid(row=5, column=1, sticky='ew', pady=2)

        # Rol
        ttk.Label(form, text="Rol:").grid(row=6, column=0, sticky='w', pady=2)
        self.combo_rol = ttk.Combobox(
            form, 
            values=['ADMIN', 'MAESTRO', 'ALUMNO'], 
            textvariable=self.var_rol, 
            state='readonly',
            width=23
        )
        self.combo_rol.grid(row=6, column=1, sticky='ew', pady=2)

        # === BOTONES ===
        btns = ttk.Frame(form)
        btns.grid(row=7, column=0, columnspan=2, pady=(15, 0))

        self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_usuario, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)

        self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_usuario, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)

        self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_usuario, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)

        self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_usuario, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)

        self.btn_eliminar = ttk.Button(btns, text="Eliminar", command=self.eliminar_usuario, width=12)
        self.btn_eliminar.grid(row=2, column=0, padx=4, pady=2)

        self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)

        ttk.Button(
            btns, 
            text="Cambiar Contraseña", 
            command=self.cambiar_contrasena,
            width=25
        ).grid(row=3, column=0, columnspan=2, pady=(8, 0))

        # === LISTADO ===
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)

        # Búsqueda
        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar (email o ID):").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(searchfrm, textvariable=self.search_var, width=25).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_usuarios).pack(side='left', padx=6)

        # Filtro por rol
        ttk.Label(searchfrm, text="Filtrar:").pack(side='left', padx=(20, 4))
        self.filtro_rol = tk.StringVar(value="TODOS")
        ttk.Combobox(
            searchfrm, 
            values=['TODOS', 'ADMIN', 'MAESTRO', 'ALUMNO'],
            textvariable=self.filtro_rol,
            state='readonly',
            width=12
        ).pack(side='left')
        ttk.Button(searchfrm, text="Aplicar", command=self.aplicar_filtro).pack(side='left', padx=4)

        # Treeview
        cols = ("id", "email", "nombre", "apellido_paterno", "apellido_materno", "telefono", "rol")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("email", text="Email")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellido_paterno", text="Ap. Paterno")
        self.tree.heading("apellido_materno", text="Ap. Materno")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("rol", text="Rol")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("email", width=180)
        self.tree.column("nombre", width=100)
        self.tree.column("apellido_paterno", width=100)
        self.tree.column("apellido_materno", width=100)
        self.tree.column("telefono", width=90, anchor="center")
        self.tree.column("rol", width=80, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def set_estado(self, modo):
        if modo == "nuevo":
            estado = "normal"
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="normal")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            
        elif modo == "editar":
            estado = "normal"
            self.entry_email.config(state="disabled")  # No permitir cambiar email al editar
            self.btn_nuevo.config(state="disabled")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="normal")
            self.btn_eliminar.config(state="disabled")
            
        elif modo in ("salvar", "cancelar", "remover", "inicio"):
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="disabled")
            self.btn_editar.config(state="disabled")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="disabled")
            
        elif modo == "buscar":
            estado = "disabled"
            self.btn_nuevo.config(state="normal")
            self.btn_guardar.config(state="disabled")
            self.btn_cancelar.config(state="normal")
            self.btn_editar.config(state="normal")
            self.btn_actualizar.config(state="disabled")
            self.btn_eliminar.config(state="normal")

        # Configurar campos
        if modo != "editar":
            self.entry_email.config(state=estado)# type: ignore
            
        for entry in (self.entry_nombre, self.entry_apellido_paterno,
                      self.entry_apellido_materno, self.entry_telefono):
            entry.config(state=estado)# type: ignore
            
        self.combo_rol.config(state="readonly" if estado == "normal" else "disabled")# type: ignore

    def limpiar_form(self):
        """Limpia todos los campos del formulario"""
        self.var_id.set('')
        self.var_email.set('')
        self.var_nombre.set('')
        self.var_apellido_paterno.set('')
        self.var_apellido_materno.set('')
        self.var_telefono.set('')
        self.var_rol.set('ALUMNO')

    def validar_email(self, email):
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def validar_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe incluir al menos una mayúscula"
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe incluir al menos un número"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "La contraseña debe incluir al menos un símbolo (!@#$%^&*, etc.)"
        return True, ""

    def validar_telefono(self, telefono: str) -> tuple[bool, str]:
        """Valida el formato de teléfono mexicano"""
        if not telefono:
            return True, ""  
        
        # Eliminar espacios, guiones y paréntesis
        tel_limpio = telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Validar que solo tenga dígitos
        if not tel_limpio.isdigit():
            return False, "El teléfono solo debe contener números"
        
        # Validar longitud (10 dígitos en México)
        if len(tel_limpio) != 10:
            return False, "El teléfono debe tener 10 dígitos"
        
        # Validar que no inicie con 0
        if tel_limpio[0] == '0':
            return False, "El teléfono no debe iniciar con 0"
        
        return True, ""
    
    def campos_obligatorios_llenos(self) -> bool:
        """Verifica que los campos obligatorios no estén vacíos"""
        campos = [self.var_nombre.get().strip(), self.var_email.get().strip()]
        if any(not campo for campo in campos):
            messagebox.showwarning("Validación", "Complete todos los campos obligatorios")
            return False
        return True

    def nuevo_usuario(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_email.focus()

    def guardar_usuario(self):
        # Validaciones
        email = self.var_email.get().strip()
        nombre = self.var_nombre.get().strip()
        
        if not email or not nombre:
            messagebox.showwarning("Validación", "Email y Nombre son campos obligatorios")
            return
            
        if not self.validar_email(email):
            messagebox.showwarning("Validación", "El formato del email no es válido")
            return
        
        # Verificar email único
        if not self.db.validar_email_unico(email):
            messagebox.showwarning("Validación", "El email ya está registrado")
            return
        
        telefono = self.var_telefono.get().strip()
        valida_tel, msg_tel = self.validar_telefono(telefono)
        if not valida_tel:
            messagebox.showwarning("Validación", msg_tel)
            return
        
        # Solicitar contraseña
        password = simpledialog.askstring(
            "Contraseña", 
            f"Ingrese contraseña para {email}\n\nRequisitos:\n- Mínimo 6 caracteres\n- Al menos una mayúscula\n- Al menos un número\n- Al menos un símbolo", 
            show='*'
        )
        
        if not password:
            return
        
        # Validar contraseña
        valida, msg_error = self.validar_password(password)
        if not valida:
            messagebox.showwarning("Validación", msg_error)
            return
        
        # Confirmar contraseña
        password_confirm = simpledialog.askstring(
            "Confirmar Contraseña", 
            "Confirme la contraseña:", 
            show='*'
        )
        
        if password != password_confirm:
            messagebox.showwarning("Validación", "Las contraseñas no coinciden")
            return
        
        # Crear usuario
        ok, msg = self.db.crear_usuario(
            email=email,
            password=password,
            rol=self.var_rol.get(),
            nombre=nombre,
            apellido_paterno=self.var_apellido_paterno.get().strip(),
            apellido_materno=self.var_apellido_materno.get().strip(),
            telefono=self.var_telefono.get().strip()
        )
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_usuarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_usuario(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un usuario")
            return
        self.set_estado("editar")

    def actualizar_usuario(self):
        if not self.var_id.get():
            return
        
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return
        
        ok, msg = self.db.actualizar_usuario(
            user_id=int(self.var_id.get()),
            nombre=nombre,
            apellido_paterno=self.var_apellido_paterno.get().strip(),
            apellido_materno=self.var_apellido_materno.get().strip(),
            telefono=self.var_telefono.get().strip(),
            rol=self.var_rol.get()
        )
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_usuarios()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_usuario(self):
        if not self.var_id.get():
            return
        
        # Prevenir eliminación del propio usuario admin
        if self.usuario_actual is not None and int(self.var_id.get()) == self.usuario_actual.get('id', -1):
            messagebox.showwarning("Advertencia", "No puedes eliminar tu propia cuenta")
            return
        
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este usuario?\n\nEsta acción no se puede deshacer."):
            ok, msg = self.db.eliminar_usuario(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_usuarios()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cambiar_contrasena(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un usuario")
            return
        
        nueva = simpledialog.askstring(
            "Nueva Contraseña", 
            "Ingrese la nueva contraseña:\n\nRequisitos:\n- Mínimo 6 caracteres\n- Al menos una mayúscula\n- Al menos un número\n- Al menos un símbolo",
            show='*'
        )
        
        if not nueva:
            return
        
        # Validar contraseña
        valida, msg_error = self.validar_password(nueva)
        if not valida:
            messagebox.showwarning("Validación", msg_error)
            return
        
        ok, msg = self.db.actualizar_contrasena(int(self.var_id.get()), nueva)
        if ok:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def cargar_usuarios(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        rows = self.db.listar_usuarios()
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('email', ''),
                r.get('nombre', ''),
                r.get('apellido_paterno', ''),
                r.get('apellido_materno', ''),
                r.get('telefono', ''),
                r.get('rol', '')
            ))

    def aplicar_filtro(self):

        for row in self.tree.get_children():
            self.tree.delete(row)
        
        rol = self.filtro_rol.get()
        rows = self.db.listar_usuarios(None if rol == "TODOS" else rol)
        
        for r in rows:
            self.tree.insert('', 'end', values=(
                r.get('id', ''),
                r.get('email', ''),
                r.get('nombre', ''),
                r.get('apellido_paterno', ''),
                r.get('apellido_materno', ''),
                r.get('telefono', ''),
                r.get('rol', '')
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
            
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 7:
            return
            
        self.var_id.set(str(values[0]))
        self.var_email.set(str(values[1]))
        self.var_nombre.set(str(values[2]))
        self.var_apellido_paterno.set(str(values[3]))
        self.var_apellido_materno.set(str(values[4]))
        self.var_telefono.set(str(values[5]))
        self.var_rol.set(str(values[6]))
        self.set_estado("buscar")

    def buscar(self):
        q = self.search_var.get().strip()
        if not q:
            self.cargar_usuarios()
            return
            
        user = None
        if q.isdigit():
            user = self.db.buscar_usuario_por_id(int(q))
        
        if not user:
            user = self.db.buscar_usuario_por_email(q)
            
        if not user:
            messagebox.showinfo("Búsqueda", "Usuario no encontrado")
            return
            
        self.var_id.set(user['id'])
        self.var_email.set(user['email'])
        self.var_nombre.set(user.get('nombre', ''))
        self.var_apellido_paterno.set(user.get('apellido_paterno', ''))
        self.var_apellido_materno.set(user.get('apellido_materno', ''))
        self.var_telefono.set(user.get('telefono', ''))
        self.var_rol.set(user.get('rol', 'ALUMNO'))
        self.set_estado("buscar")
