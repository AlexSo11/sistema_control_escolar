"""
Interfaz de Gestión de Maestros
Correcciones: validar_email completado, búsqueda implementada (filtrado local), manejo de errores.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from DB.dbMaestros import DBMaestro
from DB.dbUsuarios import DBUsuario # Mantenemos DBUsuario por si se usa en otro lado
from conexion import ConexionDB
import re

class MaestrosUI:
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db_maestro = DBMaestro(self.con)
        self.db_usuario = DBUsuario(self.con) 
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        self.modo_admin = usuario_actual and usuario_actual.get('rol') == 'ADMIN'
        self.modo_maestro = usuario_actual and usuario_actual.get('rol') == 'MAESTRO'

        if not self.modo_admin and not self.modo_maestro:
            ttk.Label(
                self.frame,
                text="Acceso denegado: Solo maestros y administradores pueden acceder",
                font=("Segoe UI", 12),
                foreground="red"
            ).pack(expand=True)
            return

        # Variables del formulario
        self.var_id = tk.StringVar()
        self.var_numero_empleado = tk.StringVar()
        self.var_especialidad = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido_paterno = tk.StringVar()
        self.var_apellido_materno = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_carrera = tk.StringVar()

        # --- Widgets ---
        self.entry_id: ttk.Entry
        self.entry_numero_empleado: ttk.Entry
        self.entry_email: ttk.Entry
        self.entry_nombre: ttk.Entry
        self.entry_apellido_paterno: ttk.Entry
        self.entry_apellido_materno: ttk.Entry
        self.entry_telefono: ttk.Entry
        self.entry_especialidad: ttk.Entry
        self.combo_carrera: ttk.Combobox
        self.combo_materias: ttk.Combobox
        self.listbox_materias: tk.Listbox
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_eliminar: ttk.Button
        self.btn_cancelar: ttk.Button
        self.tree: ttk.Treeview
        self.search_var = tk.StringVar()

        self.materias_seleccionadas = [] 

        self.build_ui()

        if self.modo_maestro:
            self.cargar_datos_propios()
            self.set_estado("ver_propio")
        else:
            self.cargar_maestros()
            self.set_estado("inicio")

    def build_ui(self):
        """Construye la interfaz gráfica"""
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)

        # === FORMULARIO ===
        form = ttk.LabelFrame(frm_principal, text="Datos del Maestro", padding=10)
        form.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form, textvariable=self.var_id, state='readonly', width=25)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Número de Empleado:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_numero_empleado = ttk.Entry(form, textvariable=self.var_numero_empleado, width=25)
        self.entry_numero_empleado.grid(row=1, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Email:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_email = ttk.Entry(form, textvariable=self.var_email, width=25)
        self.entry_email.grid(row=2, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Nombre:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_nombre = ttk.Entry(form, textvariable=self.var_nombre, width=25)
        self.entry_nombre.grid(row=3, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Apellido Paterno:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_apellido_paterno = ttk.Entry(form, textvariable=self.var_apellido_paterno, width=25)
        self.entry_apellido_paterno.grid(row=4, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Apellido Materno:").grid(row=5, column=0, sticky='w', pady=2)
        self.entry_apellido_materno = ttk.Entry(form, textvariable=self.var_apellido_materno, width=25)
        self.entry_apellido_materno.grid(row=5, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Teléfono:").grid(row=6, column=0, sticky='w', pady=2)
        self.entry_telefono = ttk.Entry(form, textvariable=self.var_telefono, width=25)
        self.entry_telefono.grid(row=6, column=1, sticky='ew', pady=2)

        ttk.Label(form, text="Especialidad:").grid(row=7, column=0, sticky='w', pady=2)
        self.entry_especialidad = ttk.Entry(form, textvariable=self.var_especialidad, width=25)
        self.entry_especialidad.grid(row=7, column=1, sticky='ew', pady=2)

        # === SECCIÓN DE MATERIAS (Opcional) ===
        ttk.Label(form, text="Carrera:").grid(row=8, column=0, sticky='w', pady=(10, 2))
        self.combo_carrera = ttk.Combobox(form, textvariable=self.var_carrera, state='readonly', width=23)
        self.combo_carrera.grid(row=8, column=1, sticky='ew', pady=(10, 2))
        self.combo_carrera.bind('<<ComboboxSelected>>', self.cargar_materias)

        ttk.Label(form, text="Materias:").grid(row=9, column=0, sticky='nw', pady=2)
        frame_materias = ttk.Frame(form)
        frame_materias.grid(row=9, column=1, sticky='ew', pady=2)
        self.combo_materias = ttk.Combobox(frame_materias, state='readonly', width=18)
        self.combo_materias.pack(side='left', fill='x', expand=True)
        ttk.Button(frame_materias, text="+", width=3, command=self.agregar_materia).pack(side='left', padx=(2, 0))

        ttk.Label(form, text="Materias Asignadas:").grid(row=10, column=0, sticky='nw', pady=2)
        frame_list = ttk.Frame(form)
        frame_list.grid(row=10, column=1, sticky='ew', pady=2)
        scroll_materias = ttk.Scrollbar(frame_list)
        scroll_materias.pack(side='right', fill='y')
        self.listbox_materias = tk.Listbox(frame_list, height=4, yscrollcommand=scroll_materias.set)
        self.listbox_materias.pack(side='left', fill='both', expand=True)
        scroll_materias.config(command=self.listbox_materias.yview)
        ttk.Button(form, text="Quitar Materia", command=self.quitar_materia).grid(row=11, column=1, pady=2)

        # === BOTONES ===
        btns = ttk.Frame(form)
        btns.grid(row=12, column=0, columnspan=2, pady=(15, 0))

        if self.modo_admin:
            self.btn_nuevo = ttk.Button(btns, text="Nuevo", command=self.nuevo_maestro, width=12)
            self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
            self.btn_guardar = ttk.Button(btns, text="Guardar", command=self.guardar_maestro, width=12)
            self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
            self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_maestro, width=12)
            self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
            self.btn_actualizar = ttk.Button(btns, text="Actualizar", command=self.actualizar_maestro, width=12)
            self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
            self.btn_eliminar = ttk.Button(btns, text="Eliminar", command=self.eliminar_maestro, width=12)
            self.btn_eliminar.grid(row=2, column=0, padx=4, pady=2)
            self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
            self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)
        else:
            self.btn_editar = ttk.Button(btns, text="Editar", command=self.editar_maestro, width=12)
            self.btn_editar.grid(row=0, column=0, padx=4, pady=2)
            self.btn_actualizar = ttk.Button(btns, text="Guardar", command=self.actualizar_maestro, width=12)
            self.btn_actualizar.grid(row=0, column=1, padx=4, pady=2)
            self.btn_cancelar = ttk.Button(btns, text="Cancelar", command=self.cancelar_edicion, width=12)
            self.btn_cancelar.grid(row=1, column=0, columnspan=2, pady=2)

        # === LISTADO (solo para admin) ===
        if self.modo_admin:
            right = ttk.Frame(frm_principal)
            right.pack(side='left', fill='both', expand=True)

            searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
            searchfrm.pack(fill='x')
            ttk.Label(searchfrm, text="Buscar:").pack(side='left')
            self.search_var = tk.StringVar()
            ttk.Entry(searchfrm, textvariable=self.search_var, width=25).pack(side='left', padx=6)
            ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
            ttk.Button(searchfrm, text="Refrescar", command=self.cargar_maestros).pack(side='left', padx=6)

            cols = ("id", "num_empleado", "nombre", "apellidos", "email", "especialidad")
            self.tree = ttk.Treeview(right, columns=cols, show='headings', height=15)
            self.tree.heading("id", text="ID")
            self.tree.heading("num_empleado", text="Núm. Empleado")
            self.tree.heading("nombre", text="Nombre")
            self.tree.heading("apellidos", text="Apellidos")
            self.tree.heading("email", text="Email")
            self.tree.heading("especialidad", text="Especialidad")
            self.tree.column("id", width=40, anchor="center")
            self.tree.column("num_empleado", width=100, anchor="center")
            self.tree.column("nombre", width=120)
            self.tree.column("apellidos", width=150)
            self.tree.column("email", width=180)
            self.tree.column("especialidad", width=120)
            
            scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            self.tree.pack(fill='both', expand=True)
            self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.cargar_carreras()

    def cargar_carreras(self):
        """Carga las carreras en el combobox"""
        carreras = self.db_maestro.obtener_carreras()
        self.combo_carrera['values'] = [f"{c['id']} - {c['nombre']}" for c in carreras]

    def cargar_materias(self, event=None):
        """Carga las materias según la carrera seleccionada"""
        carrera_sel = self.var_carrera.get()
        if not carrera_sel:
            return
        carrera_id = int(carrera_sel.split(' - ')[0])
        materias = self.db_maestro.obtener_materias_por_carrera(carrera_id)
        self.combo_materias['values'] = [f"{m['id']} - {m['codigo']} - {m['nombre']}" for m in materias]

    def agregar_materia(self):
        """Agrega una materia al listbox"""
        materia_sel = self.combo_materias.get()
        if not materia_sel:
            messagebox.showwarning("Validación", "Selecciona una materia")
            return
        if materia_sel not in self.materias_seleccionadas:
            self.materias_seleccionadas.append(materia_sel)
            self.listbox_materias.insert(tk.END, materia_sel)

    def quitar_materia(self):
        """Quita una materia del listbox"""
        sel = self.listbox_materias.curselection()
        if sel:
            materia = self.listbox_materias.get(sel[0])
            self.listbox_materias.delete(sel[0])
            self.materias_seleccionadas.remove(materia)

    def set_estado(self, modo: str):
        """Configura el estado de los botones y campos"""
        estado = "disabled" # Default
        
        if self.modo_maestro:
            if modo == "ver_propio":
                estado = "disabled"
                self.btn_editar.config(state="normal")
                self.btn_actualizar.config(state="disabled")
                self.btn_cancelar.config(state="disabled")
            elif modo == "editar_propio":
                estado = "normal"
                self.btn_editar.config(state="disabled")
                self.btn_actualizar.config(state="normal")
                self.btn_cancelar.config(state="normal")
        
        elif self.modo_admin:
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

        # Configurar campos de texto
        for entry in (self.entry_nombre, self.entry_apellido_paterno,
                      self.entry_apellido_materno, self.entry_telefono,
                      self.entry_especialidad):
            entry.config(state=estado)
        
        # Campos con lógica especial
        if self.modo_maestro:
            self.entry_email.config(state="readonly")
            self.entry_numero_empleado.config(state="readonly")
        else: # modo_admin
            if modo == "editar":
                self.entry_email.config(state="disabled")
                self.entry_numero_empleado.config(state="disabled")
            else:
                self.entry_email.config(state=estado)
                self.entry_numero_empleado.config(state=estado)
        
        # Comboboxes y Listbox
        combo_state = "readonly" if estado == "normal" else "disabled"
        self.combo_carrera.config(state=combo_state)
        self.combo_materias.config(state=combo_state)
        # Habilitar/deshabilitar botones de materia
        try:
            self.listbox_materias.config(state="normal" if estado == "normal" else "disabled")
            form = self.listbox_materias.master.master # Navegar hasta el 'form'
            form.grid_slaves(row=9, column=1)[0].winfo_children()[1].config(state="normal" if estado == "normal" else "disabled") # Botón '+'
            form.grid_slaves(row=11, column=1)[0].config(state="normal" if estado == "normal" else "disabled") # Botón 'Quitar'
        except Exception:
            pass # Ignorar si los widgets no existen

    def limpiar_form(self):
        """Limpia todos los campos del formulario"""
        self.var_id.set('')
        self.var_numero_empleado.set('')
        self.var_email.set('')
        self.var_nombre.set('')
        self.var_apellido_paterno.set('')
        self.var_apellido_materno.set('')
        self.var_telefono.set('')
        self.var_especialidad.set('')
        self.var_carrera.set('')
        self.listbox_materias.delete(0, tk.END)
        self.materias_seleccionadas.clear()

    def nuevo_maestro(self):
        """Prepara el formulario para crear un nuevo maestro"""
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_email.focus()

    def validar_email(self, email: str) -> bool:
        """Valida el formato del email"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def validar_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe incluir al menos una mayúscula"
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe incluir al menos un número"
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return False, "La contraseña debe incluir al menos un símbolo (!@#$%^&*, etc.)"
        return True, ""

    def validar_campos_obligatorios(self) -> bool:
        """Valida que los campos obligatorios no estén vacíos"""
        campos_obligatorios = [
            (self.var_email.get().strip(), "Email"),
            (self.var_numero_empleado.get().strip(), "Número de empleado"),
            (self.var_nombre.get().strip(), "Nombre"),
            (self.var_apellido_paterno.get().strip(), "Apellido paterno")
        ]
        
        for valor, campo in campos_obligatorios:
            if not valor:
                messagebox.showwarning("Validación", f"El campo '{campo}' es obligatorio")
                return False
        return True

    def validar_solo_letras(self, texto: str, campo: str) -> tuple[bool, str]:
        """Valida que el texto contenga solo letras y espacios"""
        if not texto:
            return True, ""  # Campos opcionales pueden estar vacíos
        
        # Permitir letras, espacios, acentos y ñ
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', texto):
            return False, f"El campo '{campo}' solo puede contener letras y espacios"
        
        # Validar que no sean solo espacios
        if texto.strip() == "":
            return False, f"El campo '{campo}' no puede contener solo espacios"
        
        return True, ""

    def validar_solo_numeros(self, texto: str, campo: str) -> tuple[bool, str]:
        """Valida que el texto contenga solo números"""
        if not texto:
            return True, ""  # Campos opcionales pueden estar vacíos
        
        if not texto.isdigit():
            return False, f"El campo '{campo}' solo puede contener números"
        
        return True, ""

    def validar_alfanumerico(self, texto: str, campo: str) -> tuple[bool, str]:
        """Valida que el texto sea alfanumérico"""
        if not texto:
            return False, f"El campo '{campo}' es obligatorio"
        
        if not texto.isalnum():
            return False, f"El campo '{campo}' solo puede contener letras y números (sin espacios ni símbolos)"
        
        return True, ""

    def validar_longitud(self, texto: str, campo: str, min_len: int, max_len: int) -> tuple[bool, str]:
        """Valida la longitud del texto"""
        if not texto and min_len > 0:
            return False, f"El campo '{campo}' es obligatorio"
        
        if len(texto) < min_len:
            return False, f"El campo '{campo}' debe tener al menos {min_len} caracteres"
        
        if len(texto) > max_len:
            return False, f"El campo '{campo}' no puede tener más de {max_len} caracteres"
        
        return True, ""

    def validar_telefono(self, telefono: str) -> tuple[bool, str]:
        """Valida el formato de teléfono mexicano"""
        if not telefono:
            return True, ""  # Teléfono es opcional
        
        # Limpiar el teléfono
        tel_limpio = telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if not tel_limpio.isdigit():
            return False, "El teléfono solo debe contener números"
        
        if len(tel_limpio) != 10:
            return False, "El teléfono debe tener exactamente 10 dígitos"
        
        if tel_limpio[0] in ['0', '1']:
            return False, "El teléfono no puede iniciar con 0 o 1"
        
        # Validar código de área (primeros 2-3 dígitos)
        codigo_area = tel_limpio[:3]
        if codigo_area in ['000', '111', '222', '333', '444', '555', '666', '777', '888', '999']:
            return False, "El código de área no es válido"
        
        return True, ""

    def guardar_maestro(self):
        """Guarda un nuevo maestro con todas las validaciones"""
        
        # 1. Validar campos obligatorios
        if not self.validar_campos_obligatorios():
            return
        
        # Obtener valores
        email = self.var_email.get().strip()
        numero_empleado = self.var_numero_empleado.get().strip()
        nombre = self.var_nombre.get().strip()
        apellido_paterno = self.var_apellido_paterno.get().strip()
        apellido_materno = self.var_apellido_materno.get().strip()
        telefono = self.var_telefono.get().strip()
        especialidad = self.var_especialidad.get().strip()
        
        # 2. Validar formato de email
        if not self.validar_email(email):
            messagebox.showwarning("Validación", "El formato del email no es válido")
            self.entry_email.focus()
            return
        
        # 3. Validar email único
        if not self.db_usuario.validar_email_unico(email):
            messagebox.showwarning("Validación", "El email ya está registrado")
            self.entry_email.focus()
            return
        
        # 4. Validar número de empleado (alfanumérico)
        valida_num_emp, msg_num_emp = self.validar_alfanumerico(numero_empleado, "Número de empleado")
        if not valida_num_emp:
            messagebox.showwarning("Validación", msg_num_emp)
            self.entry_numero_empleado.focus()
            return
        
        # 5. Validar longitud número de empleado
        valida_long_num, msg_long_num = self.validar_longitud(numero_empleado, "Número de empleado", 5, 15)
        if not valida_long_num:
            messagebox.showwarning("Validación", msg_long_num)
            self.entry_numero_empleado.focus()
            return
        
        # 6. Validar número de empleado único
        if not self.db_maestro.validar_numero_empleado(numero_empleado):
            messagebox.showwarning("Validación", "El número de empleado ya está registrado")
            self.entry_numero_empleado.focus()
            return
        
        # 7. Validar nombres y apellidos (solo letras)
        campos_letras = [
            (nombre, "Nombre"),
            (apellido_paterno, "Apellido paterno"),
            (apellido_materno, "Apellido materno"),
            (especialidad, "Especialidad")
        ]
        
        for texto, campo in campos_letras:
            if texto:  # Solo validar si no está vacío (apellido materno y especialidad son opcionales)
                valida_letras, msg_letras = self.validar_solo_letras(texto, campo)
                if not valida_letras:
                    messagebox.showwarning("Validación", msg_letras)
                    # Enfocar el campo correspondiente
                    if campo == "Nombre":
                        self.entry_nombre.focus()
                    elif campo == "Apellido paterno":
                        self.entry_apellido_paterno.focus()
                    elif campo == "Apellido materno":
                        self.entry_apellido_materno.focus()
                    elif campo == "Especialidad":
                        self.entry_especialidad.focus()
                    return
        
        # 8. Validar teléfono
        if telefono:  # Teléfono es opcional
            valida_tel, msg_tel = self.validar_telefono(telefono)
            if not valida_tel:
                messagebox.showwarning("Validación", msg_tel)
                self.entry_telefono.focus()
                return
        
        # 9. Validar longitud de nombres
        valida_long_nombre, msg_long_nombre = self.validar_longitud(nombre, "Nombre", 2, 50)
        if not valida_long_nombre:
            messagebox.showwarning("Validación", msg_long_nombre)
            self.entry_nombre.focus()
            return
        
        valida_long_ap_paterno, msg_long_ap_paterno = self.validar_longitud(apellido_paterno, "Apellido paterno", 2, 30)
        if not valida_long_ap_paterno:
            messagebox.showwarning("Validación", msg_long_ap_paterno)
            self.entry_apellido_paterno.focus()
            return
        
        if apellido_materno:  # Opcional
            valida_long_ap_materno, msg_long_ap_materno = self.validar_longitud(apellido_materno, "Apellido materno", 2, 30)
            if not valida_long_ap_materno:
                messagebox.showwarning("Validación", msg_long_ap_materno)
                self.entry_apellido_materno.focus()
                return
        
        # 10. Validar que el nombre no contenga números disfrazados
        if any(char.isdigit() for char in nombre):
            messagebox.showwarning("Validación", "El nombre no puede contener números")
            self.entry_nombre.focus()
            return
        
        # SOLICITAR CONTRASEÑA (mantener tu código existente)
        password = simpledialog.askstring(
            "Contraseña", 
            f"Ingrese contraseña para {email}\n\nRequisitos:\n- Mínimo 6 caracteres\n- Al menos una mayúscula\n- Al menos un número\n- Al menos un símbolo", 
            show='*'
        )
        if not password:
            return
        
        valida, msg_error = self.validar_password(password)
        if not valida:
            messagebox.showwarning("Validación", msg_error)
            return
        
        password_confirm = simpledialog.askstring(
            "Confirmar Contraseña", "Confirme la contraseña:", show='*'
        )
        if password != password_confirm:
            messagebox.showwarning("Validación", "Las contraseñas no coinciden")
            return
        
        # CREAR MAESTRO (mantener tu código existente)
        ok, msg = self.db_maestro.crear_maestro_completo(
            email=email,
            password=password,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            telefono=telefono,
            numero_empleado=numero_empleado,
            especialidad=especialidad
        )
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_maestros()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_maestro(self):
        """Prepara el formulario para editar"""
        if not self.var_id.get() and self.modo_admin:
            messagebox.showwarning("Validación", "Selecciona primero un maestro")
            return
        if self.modo_maestro:
            self.set_estado("editar_propio")
        else:
            self.set_estado("editar")

    def actualizar_maestro(self):
        """Actualiza la información del maestro con validaciones"""
        if not self.var_id.get():
            return
        
        # 1. Validar campos obligatorios
        if not self.validar_campos_obligatorios():
            return
        
        # Obtener valores
        maestro_id = int(self.var_id.get())
        numero_empleado = self.var_numero_empleado.get().strip()
        nombre = self.var_nombre.get().strip()
        apellido_paterno = self.var_apellido_paterno.get().strip()
        apellido_materno = self.var_apellido_materno.get().strip()
        telefono = self.var_telefono.get().strip()
        especialidad = self.var_especialidad.get().strip()
        
        # 2. Validar número de empleado único (excluyendo el actual)
        if not self.db_maestro.validar_numero_empleado(numero_empleado, maestro_id):
            messagebox.showwarning("Validación", "El número de empleado ya está registrado")
            self.entry_numero_empleado.focus()
            return
        
        # 3. Validar número de empleado (alfanumérico)
        valida_num_emp, msg_num_emp = self.validar_alfanumerico(numero_empleado, "Número de empleado")
        if not valida_num_emp:
            messagebox.showwarning("Validación", msg_num_emp)
            self.entry_numero_empleado.focus()
            return
        
        # 4. Validar longitud número de empleado
        valida_long_num, msg_long_num = self.validar_longitud(numero_empleado, "Número de empleado", 5, 15)
        if not valida_long_num:
            messagebox.showwarning("Validación", msg_long_num)
            self.entry_numero_empleado.focus()
            return
        
        # 5. Validar nombres y apellidos (solo letras)
        campos_letras = [
            (nombre, "Nombre"),
            (apellido_paterno, "Apellido paterno"),
            (apellido_materno, "Apellido materno"),
            (especialidad, "Especialidad")
        ]
        
        for texto, campo in campos_letras:
            if texto:
                valida_letras, msg_letras = self.validar_solo_letras(texto, campo)
                if not valida_letras:
                    messagebox.showwarning("Validación", msg_letras)
                    return
        
        # 6. Validar teléfono
        if telefono:
            valida_tel, msg_tel = self.validar_telefono(telefono)
            if not valida_tel:
                messagebox.showwarning("Validación", msg_tel)
                self.entry_telefono.focus()
                return
        
        # 7. Validar longitud de nombres
        valida_long_nombre, msg_long_nombre = self.validar_longitud(nombre, "Nombre", 2, 50)
        if not valida_long_nombre:
            messagebox.showwarning("Validación", msg_long_nombre)
            return
        
        valida_long_ap_paterno, msg_long_ap_paterno = self.validar_longitud(apellido_paterno, "Apellido paterno", 2, 30)
        if not valida_long_ap_paterno:
            messagebox.showwarning("Validación", msg_long_ap_paterno)
            return
        
        if apellido_materno:
            valida_long_ap_materno, msg_long_ap_materno = self.validar_longitud(apellido_materno, "Apellido materno", 2, 30)
            if not valida_long_ap_materno:
                messagebox.showwarning("Validación", msg_long_ap_materno)
                return
        
        # ACTUALIZAR MAESTRO (mantener tu código existente)
        ok, msg = self.db_maestro.actualizar_maestro(
            maestro_id=maestro_id,
            numero_empleado=numero_empleado,
            especialidad=especialidad,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            telefono=telefono
        )
        
        if ok:
            messagebox.showinfo("Éxito", msg)
            if self.modo_admin:
                self.cargar_maestros()
                self.limpiar_form()
                self.set_estado("salvar")
            else:
                self.cargar_datos_propios()
                self.set_estado("ver_propio")
        else:
            messagebox.showerror("Error", msg)

    def eliminar_maestro(self):
        """Elimina el maestro seleccionado"""
        if not self.var_id.get():
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este maestro?"):
            ok, msg = self.db_maestro.eliminar_maestro(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_maestros()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        """Cancela la edición/creación actual"""
        if self.modo_maestro:
            self.cargar_datos_propios()
            self.set_estado("ver_propio")
        else:
            self.limpiar_form()
            self.set_estado("cancelar")

    def cargar_maestros(self):
        if not self.modo_admin:
            return
        if not hasattr(self, 'tree'): 
            return

        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            rows = self.db_maestro.listar_maestros()
            for r in rows:
                apellidos = f"{r.get('apellido_paterno', '')} {r.get('apellido_materno', '')}".strip()
                self.tree.insert('', 'end', values=(
                    r.get('id', ''),
                    r.get('numero_empleado', ''),
                    r.get('nombre', ''),
                    apellidos,
                    r.get('email', ''),
                    r.get('especialidad', '')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar maestros: {e}")

    def cargar_datos_propios(self):
        if not self.usuario_actual:
            return
        maestro_id = self.usuario_actual.get('id')
        try:
            maestro = self.db_maestro.buscar_maestro_por_id(maestro_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos: {e}")
            return
        
        if maestro:
            self.var_id.set(maestro.get('id', ''))
            self.var_numero_empleado.set(maestro.get('numero_empleado', ''))
            self.var_email.set(maestro.get('email', ''))
            self.var_nombre.set(maestro.get('nombre', ''))
            self.var_apellido_paterno.set(maestro.get('apellido_paterno', ''))
            self.var_apellido_materno.set(maestro.get('apellido_materno', ''))
            self.var_telefono.set(maestro.get('telefono', ''))
            self.var_especialidad.set(maestro.get('especialidad', ''))

    def on_tree_select(self, event):
        if not self.modo_admin:
            return
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], 'values')
        if not values or len(values) < 6:
            return
        
        maestro = None
        try:
            maestro = self.db_maestro.buscar_maestro_por_id(int(values[0]))
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar maestro: {e}")
            return

        if maestro:
            self.var_id.set(maestro.get('id', ''))
            self.var_numero_empleado.set(maestro.get('numero_empleado', ''))
            self.var_email.set(maestro.get('email', ''))
            self.var_nombre.set(maestro.get('nombre', ''))
            self.var_apellido_paterno.set(maestro.get('apellido_paterno', ''))
            self.var_apellido_materno.set(maestro.get('apellido_materno', ''))
            self.var_telefono.set(maestro.get('telefono', ''))
            self.var_especialidad.set(maestro.get('especialidad', ''))
            self.set_estado("buscar")
            
            self.limpiar_form_materias_seleccion()

    def limpiar_form_materias_seleccion(self):
        """Limpia solo la parte de selección de materias"""
        self.var_carrera.set('')
        self.combo_materias['values'] = []
        self.listbox_materias.delete(0, tk.END)
        self.materias_seleccionadas.clear()

    def buscar(self):
        """Busca un maestro por ID, número de empleado o por nombre (parcial)."""
        q = self.search_var.get().strip()
        if not q:
            self.cargar_maestros()
            return

        try:
            rows = self.db_maestro.listar_maestros()
        except Exception as e:
            messagebox.showerror("Error", f"Error al listar maestros: {e}")
            return

        q_lower = q.lower()
        resultados = []
        if q.isdigit():
            idq = int(q)
            resultados = [r for r in rows if int(r.get('id', -1)) == idq]
        if not resultados:
            resultados = [r for r in rows if str(r.get('numero_empleado', '')).lower() == q_lower]
        if not resultados:
            resultados = [r for r in rows if q_lower in str(r.get('nombre', '')).lower() or 
                            q_lower in str(r.get('apellido_paterno', '')).lower() or 
                            q_lower in str(r.get('apellido_materno', '')).lower()]

        # Limpiar treeview antes de mostrar resultados
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not resultados:
            messagebox.showinfo("Búsqueda", "Maestro no encontrado")
            return
        
        # Llenar treeview con resultados
        for r in resultados:
            apellidos = f"{r.get('apellido_paterno', '')} {r.get('apellido_materno', '')}".strip()
            self.tree.insert('', 'end', values=(
                r.get('id', ''), r.get('numero_empleado', ''), r.get('nombre', ''),
                apellidos, r.get('email', ''), r.get('especialidad', '')
            ))