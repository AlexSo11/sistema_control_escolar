"""
Módulo de Gestión de Alumnos - Base de Datos
SIIAU 2.0 - Sistema Integral de Información Académica Universitaria
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, Any
from DB.dbAlumnos import DBAlumno
from conexion import ConexionDB
import re
from datetime import datetime, date

class AlumnosUI:
    
    def __init__(self, parent: ttk.Frame, usuario_actual: Optional[Dict[str, Any]] = None):
        
        self.parent = parent
        self.usuario_actual = usuario_actual
        self.con = ConexionDB()
        self.db = DBAlumno(self.con) 
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.pack(fill='both', expand=True)

        # --- Variables de Alumno ---
        self.var_id = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellido_paterno = tk.StringVar()
        self.var_apellido_materno = tk.StringVar()
        self.var_matricula = tk.StringVar()
        self.var_fecha_nac = tk.StringVar()
        self.var_carrera = tk.StringVar()
        self.var_estado = tk.StringVar()
        self.carreras_map: Dict[str, int] = {} 
        self.carreras_map_inverso: Dict[int, str] = {}
        
        # --- Variables de Inscripción ---
        self.var_grupo = tk.StringVar() # <-- Cambiado
        self.grupos_map: Dict[str, int] = {} # <-- Mapea 'Display' -> grupo_id
        self.current_alumno_id: Optional[int] = None
        self.current_alumno_carrera_id: Optional[int] = None

        # --- Widgets (Perfil) ---
        self.entry_id: ttk.Entry
        self.entry_email: ttk.Entry
        self.entry_nombre: ttk.Entry
        self.entry_apellido_paterno: ttk.Entry
        self.entry_apellido_materno: ttk.Entry
        self.entry_matricula: ttk.Entry
        self.entry_fecha_nac: ttk.Entry
        self.combo_carrera: ttk.Combobox
        self.combo_estado: ttk.Combobox
        self.btn_nuevo: ttk.Button
        self.btn_guardar: ttk.Button
        self.btn_editar: ttk.Button
        self.btn_actualizar: ttk.Button
        self.btn_baja: ttk.Button
        self.btn_cancelar: ttk.Button
        
        # --- Widgets (Grupos) ---
        self.form_grupos: ttk.LabelFrame
        self.combo_grupos: ttk.Combobox
        self.btn_guardar_grupo: ttk.Button
        self.tree_grupos: ttk.Treeview
        self.btn_baja_grupo: ttk.Button

        # --- Widgets (Lista Alumnos) ---
        self.search_var = tk.StringVar()
        self.filtro_estado = tk.StringVar(value="TODOS")
        self.tree_alumnos: ttk.Treeview

        self.build_ui()
        self.cargar_carreras() 
        self.cargar_alumnos()
        self.set_estado("inicio")

    def build_ui(self):
        frm_principal = ttk.Frame(self.frame, padding=10)
        frm_principal.pack(fill='both', expand=True)
        form_container = ttk.Frame(frm_principal)
        form_container.pack(side='left', fill='y', padx=(0, 10))

        # --- Frame: Datos del Alumno ---
        form_datos = ttk.LabelFrame(form_container, text="Datos del Alumno", padding=10)
        form_datos.pack(fill='x', expand=False)
        
        ttk.Label(form_datos, text="ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_id = ttk.Entry(form_datos, textvariable=self.var_id, state='readonly', width=30)
        self.entry_id.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Matrícula:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_matricula = ttk.Entry(form_datos, textvariable=self.var_matricula, width=30)
        self.entry_matricula.grid(row=1, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Email (usuario):").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_email = ttk.Entry(form_datos, textvariable=self.var_email, width=30)
        self.entry_email.grid(row=2, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Nombre:").grid(row=3, column=0, sticky='w', pady=2)
        self.entry_nombre = ttk.Entry(form_datos, textvariable=self.var_nombre, width=30)
        self.entry_nombre.grid(row=3, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="A. Paterno:").grid(row=4, column=0, sticky='w', pady=2)
        self.entry_apellido_paterno = ttk.Entry(form_datos, textvariable=self.var_apellido_paterno, width=30)
        self.entry_apellido_paterno.grid(row=4, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="A. Materno:").grid(row=5, column=0, sticky='w', pady=2)
        self.entry_apellido_materno = ttk.Entry(form_datos, textvariable=self.var_apellido_materno, width=30)
        self.entry_apellido_materno.grid(row=5, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Fecha Nac (DD-MM-YYYY):").grid(row=6, column=0, sticky='w', pady=2)
        self.entry_fecha_nac = ttk.Entry(form_datos, textvariable=self.var_fecha_nac, width=30)
        self.entry_fecha_nac.grid(row=6, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Estado:").grid(row=7, column=0, sticky='w', pady=2)
        self.combo_estado = ttk.Combobox(
            form_datos, values=['Activo', 'Baja', 'Egresado'], 
            textvariable=self.var_estado, state='readonly', width=28
        )
        self.combo_estado.grid(row=7, column=1, sticky='ew', pady=2)
        ttk.Label(form_datos, text="Carrera:").grid(row=8, column=0, sticky='w', pady=2)
        self.combo_carrera = ttk.Combobox(
            form_datos, values=[], textvariable=self.var_carrera, state='readonly', width=28
        )
        self.combo_carrera.grid(row=8, column=1, sticky='ew', pady=2)

        # --- Frame: Botones Perfil ---
        btns_perfil = ttk.Frame(form_datos)
        btns_perfil.grid(row=9, column=0, columnspan=2, pady=(15, 0))
        self.btn_nuevo = ttk.Button(btns_perfil, text="Nuevo", command=self.nuevo_alumno, width=12)
        self.btn_nuevo.grid(row=0, column=0, padx=4, pady=2)
        self.btn_guardar = ttk.Button(btns_perfil, text="Guardar", command=self.guardar_alumno, width=12)
        self.btn_guardar.grid(row=0, column=1, padx=4, pady=2)
        self.btn_editar = ttk.Button(btns_perfil, text="Editar", command=self.editar_alumno, width=12)
        self.btn_editar.grid(row=1, column=0, padx=4, pady=2)
        self.btn_actualizar = ttk.Button(btns_perfil, text="Actualizar", command=self.actualizar_alumno, width=12)
        self.btn_actualizar.grid(row=1, column=1, padx=4, pady=2)
        self.btn_baja = ttk.Button(btns_perfil, text="Baja", command=self.dar_de_baja_alumno, width=12)
        self.btn_baja.grid(row=2, column=0, padx=4, pady=2)
        self.btn_cancelar = ttk.Button(btns_perfil, text="Cancelar", command=self.cancelar_edicion, width=12)
        self.btn_cancelar.grid(row=2, column=1, padx=4, pady=2)
        ttk.Button(
            btns_perfil, text="Cambiar Contraseña", command=self.cambiar_contrasena, width=25
        ).grid(row=3, column=0, columnspan=2, pady=(8, 0))
        
        # --- Frame: Inscribir Grupos ---
        self.form_grupos = ttk.LabelFrame(form_container, text="Inscribir Grupos", padding=10)
        self.form_grupos.pack(fill='x', expand=False, pady=(10, 0)) 
        
        ttk.Label(self.form_grupos, text="Grupos Disponibles (de su carrera):").pack(anchor='w')
        self.combo_grupos = ttk.Combobox(self.form_grupos, textvariable=self.var_grupo, state='readonly', width=35)
        self.combo_grupos.pack(fill='x', pady=2)

        btns_materia_frame = ttk.Frame(self.form_grupos)
        btns_materia_frame.pack(fill='x', pady=5)
        self.btn_guardar_grupo = ttk.Button(btns_materia_frame, text="Inscribir", command=self.inscribir_grupo)
        self.btn_guardar_grupo.pack(side='left', fill='x', expand=True, padx=(0, 2))
        self.btn_baja_grupo = ttk.Button(btns_materia_frame, text="Dar de Baja", command=self.baja_grupo)
        self.btn_baja_grupo.pack(side='left', fill='x', expand=True, padx=(2, 0))

        ttk.Label(self.form_grupos, text="Grupos Inscritos:").pack(anchor='w', pady=(5,0))
        cols_insc = ("insc_id", "grupo_codigo", "materia_nombre", "horario")
        self.tree_grupos = ttk.Treeview(self.form_grupos, columns=cols_insc, show='headings', height=5)
        self.tree_grupos.heading("insc_id", text="ID")
        self.tree_grupos.heading("grupo_codigo", text="Grupo")
        self.tree_grupos.heading("materia_nombre", text="Materia")
        self.tree_grupos.heading("horario", text="Horario")
        self.tree_grupos.column("insc_id", width=30, anchor="center")
        self.tree_grupos.column("grupo_codigo", width=80)
        self.tree_grupos.column("materia_nombre", width=120)
        self.tree_grupos.column("horario", width=120)
        self.tree_grupos.pack(fill='x', expand=True, pady=5)

        # === LISTADO (DERECHA) ===
        right = ttk.Frame(frm_principal)
        right.pack(side='left', fill='both', expand=True)
        searchfrm = ttk.Frame(right, padding=(0, 0, 0, 6))
        searchfrm.pack(fill='x')
        ttk.Label(searchfrm, text="Buscar (matrícula o email):").pack(side='left')
        ttk.Entry(searchfrm, textvariable=self.search_var, width=20).pack(side='left', padx=6)
        ttk.Button(searchfrm, text="Buscar", command=self.buscar).pack(side='left')
        ttk.Button(searchfrm, text="Refrescar", command=self.cargar_alumnos).pack(side='left', padx=6)
        ttk.Label(searchfrm, text="Filtrar Estado:").pack(side='left', padx=(15, 4))
        ttk.Combobox(
            searchfrm, values=['TODOS', 'Activo', 'Baja', 'Egresado'],
            textvariable=self.filtro_estado, state='readonly', width=12
        ).pack(side='left')
        ttk.Button(searchfrm, text="Aplicar", command=self.aplicar_filtro).pack(side='left', padx=4)

        cols_alumnos = ("id", "matricula", "email", "nombre", "ap_paterno", "ap_materno", "carrera", "estado")
        self.tree_alumnos = ttk.Treeview(right, columns=cols_alumnos, show='headings', height=15)
        self.tree_alumnos.heading("id", text="ID")
        self.tree_alumnos.heading("matricula", text="Matrícula")
        self.tree_alumnos.heading("email", text="Email")
        self.tree_alumnos.heading("nombre", text="Nombre")
        self.tree_alumnos.heading("ap_paterno", text="A. Paterno")
        self.tree_alumnos.heading("ap_materno", text="A. Materno")
        self.tree_alumnos.heading("carrera", text="Carrera")
        self.tree_alumnos.heading("estado", text="Estado")
        self.tree_alumnos.column("id", width=40, anchor="center")
        self.tree_alumnos.column("matricula", width=80, anchor="center")
        self.tree_alumnos.column("email", width=160)
        self.tree_alumnos.column("nombre", width=110)
        self.tree_alumnos.column("ap_paterno", width=100)
        self.tree_alumnos.column("ap_materno", width=100)
        self.tree_alumnos.column("carrera", width=110)
        self.tree_alumnos.column("estado", width=70, anchor="center")
        
        scrollbar = ttk.Scrollbar(right, orient='vertical', command=self.tree_alumnos.yview)
        self.tree_alumnos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree_alumnos.pack(fill='both', expand=True)
        self.tree_alumnos.bind('<<TreeviewSelect>>', self.on_alumno_select)

    def set_estado(self, modo):
        if modo == "nuevo": estado_perfil = "normal"
        elif modo == "editar": estado_perfil = "normal"
        else: estado_perfil = "disabled"
        
        self.btn_nuevo.config(state="normal" if modo not in ("nuevo", "editar") else "disabled")
        self.btn_guardar.config(state="normal" if modo == "nuevo" else "disabled")
        self.btn_editar.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_actualizar.config(state="normal" if modo == "editar" else "disabled")
        self.btn_baja.config(state="normal" if modo == "buscar" else "disabled")
        self.btn_cancelar.config(state="normal" if modo in ("nuevo", "editar", "buscar") else "disabled")

        if modo != "editar":
            self.entry_email.config(state=estado_perfil)# type: ignore
        self.entry_matricula.config(state=estado_perfil)# type: ignore
        for entry in (self.entry_nombre, self.entry_apellido_paterno,
                      self.entry_apellido_materno, self.entry_fecha_nac):
            entry.config(state=estado_perfil)# type: ignore
        for combo in (self.combo_carrera, self.combo_estado):
             combo.config(state="readonly" if estado_perfil == "normal" else "disabled")# type: ignore

        estado_grupos = "normal" if modo in ("editar", "buscar") else "disabled"
        self.combo_grupos.config(state="readonly" if estado_grupos == "normal" else "disabled") # type: ignore
        self.btn_guardar_grupo.config(state=estado_grupos)
        self.btn_baja_grupo.config(state=estado_grupos)
        if estado_grupos == "disabled":
            self.limpiar_form_grupos()

    def limpiar_form(self):
        self.var_id.set('') 
        self.var_email.set('')
        self.var_nombre.set('')
        self.var_apellido_paterno.set('')
        self.var_apellido_materno.set('')
        self.var_matricula.set('')
        self.var_fecha_nac.set('')
        self.var_carrera.set('')
        self.var_estado.set('Activo')
        self.current_alumno_id = None
        self.current_alumno_carrera_id = None
        self.limpiar_form_grupos()
    
    def limpiar_form_grupos(self):
        self.var_grupo.set('')
        self.grupos_map.clear()
        self.combo_grupos['values'] = []
        for row in self.tree_grupos.get_children():
            self.tree_grupos.delete(row)

    # --- Funciones de Formato y Validación ---
    
    def validar_email(self, email):
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def validar_fecha(self, fecha_str: str) -> tuple[bool, str]:
        if not fecha_str:
            return True, ""
        try:
            dob = datetime.strptime(fecha_str, '%d-%m-%Y').date()
        except ValueError:
            try:
                dob = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return False, "El formato de fecha debe ser DD-MM-YYYY."
        
        today = date.today()
        if dob > today:
            return False, "La fecha de nacimiento no puede ser en el futuro."
        
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 15:
            return False, f"El alumno debe tener al menos 15 años (edad calculada: {age})."

        if age > 100:
            return False, f"La edad calculada ({age} años) no es válida."

        if age < 17:
            from tkinter import messagebox
            if not messagebox.askyesno("Confirmar", 
                f"El alumno tiene {age} años. ¿Desea continuar?"):
                return False, "Operación cancelada por el usuario."

        return True, ""
        
    def _formato_fecha_bd(self, fecha: str) -> Optional[str]:
        if not fecha: return None
        if re.match(r'^\d{2}-\d{2}-\d{4}$', fecha):
            partes = fecha.split('-')
            return f"{partes[2]}-{partes[1]}-{partes[0]}"
        return fecha 

    def _formato_fecha_ui(self, fecha: str) -> str:
        if not fecha: return ""
        if re.match(r'^\d{4}-\d{2}-\d{2}$', fecha):
            partes = fecha.split('-')
            return f"{partes[2]}-{partes[1]}-{partes[0]}"
        return fecha

    def validar_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        return True, ""
    
    def validar_matricula_formato(self, matricula: str) -> tuple[bool, str]:
        """Valida el formato de la matrícula"""
        if not matricula:
            return False, "La matrícula es obligatoria"
        
        # Validar longitud
        if len(matricula) < 9 or len(matricula) > 15:
            return False, "La matrícula debe tener entre 9 y 15 caracteres"
        
        # Validar que sea alfanumérica
        if not matricula.isalnum():
            return False, "La matrícula solo puede contener letras y números"
        
        # Validar que tenga al menos algunos números
        if not any(char.isdigit() for char in matricula):
            return False, "La matrícula debe contener al menos un número"
        
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

    # --- Funciones de Carga de Datos ---
    
    def cargar_carreras(self):
        carreras = self.db.get_carreras()
        self.carreras_map = {c['nombre']: c['id'] for c in carreras}
        self.carreras_map_inverso = {c['id']: c['nombre'] for c in carreras}
        self.combo_carrera['values'] = [''] + list(self.carreras_map.keys())

    def cargar_alumnos(self):
        self.aplicar_filtro()
        
    def aplicar_filtro(self):
        for row in self.tree_alumnos.get_children():
            self.tree_alumnos.delete(row)
        estado = self.filtro_estado.get()
        rows = self.db.listar_alumnos(estado)
        for r in rows:
            self.tree_alumnos.insert('', 'end', values=(
                r.get('id', ''), r.get('matricula', ''), r.get('email', ''),
                r.get('nombre', ''), r.get('apellido_paterno', ''), r.get('apellido_materno', ''),
                r.get('carrera_nombre', ''), r.get('estado', '')
            ))
            
    def cargar_grupos_disponibles(self, alumno_id: Optional[int], carrera_id: Optional[int]):
        """Carga los GRUPOS en el combobox"""
        self.var_grupo.set('')
        self.grupos_map.clear()
        
        if not alumno_id or not carrera_id:
            self.combo_grupos['values'] = []
            return
            
        grupos = self.db.get_grupos_disponibles_para_alumno(alumno_id, carrera_id)
        display_names = []
        for g in grupos:
            display = f"{g['grupo_codigo']} - {g['materia_nombre']}"
            self.grupos_map[display] = g['grupo_id']
            display_names.append(display)
            
        if not display_names:
            display_names = ["No hay grupos de esta carrera disponibles"]
            
        self.combo_grupos['values'] = display_names

    def cargar_grupos_inscritos(self, alumno_id: Optional[int]):
        """Carga los grupos del alumno en el treeview"""
        for row in self.tree_grupos.get_children():
            self.tree_grupos.delete(row)
        if not alumno_id:
            return
            
        inscripciones = self.db.get_inscripciones_del_alumno(int(alumno_id))
        
        for i in inscripciones:
            dia = i.get('dia_semana', 'N/A')
            inicio = str(i.get('hora_inicio', ''))
            fin = str(i.get('hora_fin', ''))
            horario_str = f"{dia} {inicio}-{fin}"
            
            self.tree_grupos.insert('', 'end', values=(
                i.get('inscripcion_id', ''),
                i.get('grupo_codigo', 'N/A'),
                i.get('materia_nombre', 'N/A'),
                horario_str
            ))

    # --- Funciones de Botones (Perfil) ---

    def nuevo_alumno(self):
        self.limpiar_form()
        self.set_estado("nuevo")
        self.entry_matricula.focus()

    def guardar_alumno(self):
        email = self.var_email.get().strip()
        nombre = self.var_nombre.get().strip()
        matricula = self.var_matricula.get().strip()
        fecha_nac = self.var_fecha_nac.get().strip()
        
        if not email or not nombre or not matricula:
            messagebox.showwarning("Validación", "Matrícula, Email y Nombre son obligatorios"); return
        if not self.validar_email(email):
            messagebox.showwarning("Validación", "El formato del email no es válido"); return
        
        es_valida, msg_error_fecha = self.validar_fecha(fecha_nac)
        if not es_valida:
            messagebox.showwarning("Validación", msg_error_fecha); return
            
        if not self.db.validar_email_unico(email):
            messagebox.showwarning("Validación", "El email ya está registrado"); return
        if not self.db.validar_matricula_unica(matricula):
            messagebox.showwarning("Validación", "La matrícula ya está registrada"); return
        
        valida_mat, msg_mat = self.validar_matricula_formato(matricula)
        if not valida_mat:
            messagebox.showwarning("Validación", msg_mat)
            return
        telefono = self.var_telefono.get().strip()
        valida_tel, msg_tel = self.validar_telefono(telefono)
        if not valida_tel:
            messagebox.showwarning("Validación", msg_tel)
            return
        
        password = simpledialog.askstring("Contraseña", f"Ingrese contraseña para {email}", show='*')
        if not password: return
        valida, msg_error = self.validar_password(password)
        if not valida:
            messagebox.showwarning("Validación", msg_error); return
        password_confirm = simpledialog.askstring("Confirmar", "Confirme la contraseña:", show='*')
        if password != password_confirm:
            messagebox.showwarning("Validación", "Las contraseñas no coinciden"); return
        
        carrera_nombre = self.var_carrera.get()
        carrera_id = self.carreras_map.get(carrera_nombre)
        fecha_nac_bd = self._formato_fecha_bd(fecha_nac)
        
        ok, msg = self.db.crear_alumno(
            email=email, password=password, nombre=nombre,
            apellido_paterno=self.var_apellido_paterno.get().strip(),
            apellido_materno=self.var_apellido_materno.get().strip(),
            matricula=matricula, fecha_nacimiento=fecha_nac_bd,
            carrera_id=carrera_id, estado=self.var_estado.get()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_alumnos()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def editar_alumno(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un alumno"); return
        self.set_estado("editar")
        self.entry_nombre.focus()

    def actualizar_alumno(self):
        if not self.var_id.get(): return
        nombre = self.var_nombre.get().strip()
        matricula = self.var_matricula.get().strip()
        fecha_nac = self.var_fecha_nac.get().strip()
        user_id = int(self.var_id.get())

        if not nombre or not matricula:
            messagebox.showwarning("Validación", "Nombre y Matrícula son obligatorios"); return
        
        es_valida, msg_error_fecha = self.validar_fecha(fecha_nac)
        if not es_valida:
            messagebox.showwarning("Validación", msg_error_fecha); return
            
        if not self.db.validar_matricula_unica(matricula, user_id):
            messagebox.showwarning("Validación", "La matrícula ya está registrada"); return
        
        valida_mat, msg_mat = self.validar_matricula_formato(matricula)
        if not valida_mat:
            messagebox.showwarning("Validación", msg_mat)
            return
        telefono = self.var_telefono.get().strip()
        valida_tel, msg_tel = self.validar_telefono(telefono)
        if not valida_tel:
            messagebox.showwarning("Validación", msg_tel)
            return

        carrera_nombre = self.var_carrera.get()
        carrera_id = self.carreras_map.get(carrera_nombre)
        fecha_nac_bd = self._formato_fecha_bd(fecha_nac)

        ok, msg = self.db.actualizar_alumno(
            user_id=user_id, nombre=nombre,
            apellido_paterno=self.var_apellido_paterno.get().strip(),
            apellido_materno=self.var_apellido_materno.get().strip(),
            matricula=matricula, fecha_nacimiento=fecha_nac_bd,
            carrera_id=carrera_id, estado=self.var_estado.get()
        )
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.cargar_alumnos()
            self.limpiar_form()
            self.set_estado("salvar")
        else:
            messagebox.showerror("Error", msg)

    def dar_de_baja_alumno(self):
        if not self.var_id.get(): return
        if messagebox.askyesno("Confirmar Baja", f"¿Seguro que deseas dar de baja al alumno {self.var_nombre.get()}?"):
            ok, msg = self.db.dar_de_baja_alumno(int(self.var_id.get()))
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_alumnos()
                self.limpiar_form()
                self.set_estado("remover")
            else:
                messagebox.showerror("Error", msg)

    def cancelar_edicion(self):
        self.limpiar_form()
        self.set_estado("cancelar")

    def cambiar_contrasena(self):
        if not self.var_id.get():
            messagebox.showwarning("Validación", "Selecciona primero un alumno"); return
        nueva = simpledialog.askstring("Nueva Contraseña", "Ingrese la nueva contraseña:", show='*')
        if not nueva: return
        valida, msg_error = self.validar_password(nueva)
        if not valida:
            messagebox.showwarning("Validación", msg_error); return
        ok, msg = self.db.actualizar_contrasena(int(self.var_id.get()), nueva)
        messagebox.showinfo("Éxito", msg) if ok else messagebox.showerror("Error", msg)

    # --- Event Handlers (Selección y Búsqueda) ---

    def on_alumno_select(self, event):
        sel = self.tree_alumnos.selection()
        if not sel: return
        values = self.tree_alumnos.item(sel[0], 'values')
        if not values or len(values) < 8: return
        
        self.var_id.set(str(values[0]))
        self.var_matricula.set(str(values[1]))
        self.var_email.set(str(values[2]))
        self.var_nombre.set(str(values[3]))
        self.var_apellido_paterno.set(str(values[4]))
        self.var_apellido_materno.set(str(values[5]))
        self.var_carrera.set(str(values[6]))
        self.var_estado.set(str(values[7]))
        
        alumno_id = int(self.var_id.get())
        alumno_data = self.db.buscar_alumno_por_id(alumno_id)
        
        if alumno_data:
            fecha_nac_db = alumno_data.get('fecha_nacimiento')
            self.var_fecha_nac.set(self._formato_fecha_ui(str(fecha_nac_db)) if fecha_nac_db else '')
            self.current_alumno_id = alumno_data.get('id')
            self.current_alumno_carrera_id = alumno_data.get('carrera_id')
        else:
            self.current_alumno_id = None
            self.current_alumno_carrera_id = None
        
        self.cargar_grupos_disponibles(self.current_alumno_id, self.current_alumno_carrera_id)
        self.cargar_grupos_inscritos(self.current_alumno_id)
        self.set_estado("buscar")

    def buscar(self):
        q = self.search_var.get().strip()
        if not q:
            self.cargar_alumnos(); return
        alumno = self.db.buscar_alumno_por_matricula(q)
        if not alumno:
            alumno = self.db.buscar_alumno_por_email(q)
        if not alumno:
            messagebox.showinfo("Búsqueda", "Alumno no encontrado"); return
        
        self.var_id.set(alumno['id'])
        self.var_matricula.set(alumno.get('matricula', ''))
        self.var_email.set(alumno['email'])
        self.var_nombre.set(alumno.get('nombre', ''))
        self.var_apellido_paterno.set(alumno.get('apellido_paterno', ''))
        self.var_apellido_materno.set(alumno.get('apellido_materno', ''))
        carrera_id = alumno.get('carrera_id')
        self.var_carrera.set(self.carreras_map_inverso.get(carrera_id, ''))
        self.var_estado.set(alumno.get('estado', ''))
        fecha_nac_db = alumno.get('fecha_nacimiento')
        self.var_fecha_nac.set(self._formato_fecha_ui(str(fecha_nac_db)) if fecha_nac_db else '')

        self.current_alumno_id = alumno.get('id')
        self.current_alumno_carrera_id = alumno.get('carrera_id')
        self.cargar_grupos_disponibles(self.current_alumno_id, self.current_alumno_carrera_id)
        self.cargar_grupos_inscritos(self.current_alumno_id)
        
        self.set_estado("buscar")

    # --- Funciones de Botones (Grupos) ---
    
    def inscribir_grupo(self):
        grupo_display = self.var_grupo.get()
        if not self.current_alumno_id:
            messagebox.showwarning("Error", "No hay un alumno seleccionado")
            return
        if not grupo_display or grupo_display == "No hay grupos de esta carrera disponibles":
            messagebox.showwarning("Validación", "Selecciona un grupo válido del combobox")
            return
            
        grupo_id = self.grupos_map.get(grupo_display)
        if not grupo_id:
            messagebox.showerror("Error", "No se pudo encontrar el ID del grupo seleccionado")
            return
        
        # Extraer el nombre de la materia (está después del " - ")
        try:
            materia_seleccionada = grupo_display.split(" - ")[1]
        except IndexError:
            messagebox.showerror("Error", "Formato de grupo inválido")
            return
        
        # Verificar si ya está inscrito en esta materia
        conn = self.db.conexion.obtener_conexion()  # ✅ Obtener conexión correctamente
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.nombre 
                FROM inscripcion i
                JOIN grupo g ON i.grupo_id = g.id
                JOIN materia m ON g.materia_id = m.id
                WHERE i.alumno_id = %s AND m.nombre = %s
            """, (self.current_alumno_id, materia_seleccionada))
            
            materia_existente = cursor.fetchone()
            
            if materia_existente:
                messagebox.showwarning("Error", f"El alumno ya está inscrito en la materia: {materia_seleccionada}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar inscripción: {str(e)}")
            return
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        if messagebox.askyesno("Confirmar", f"¿Inscribir a {self.var_nombre.get()} en {grupo_display}?"):
            ok, msg = self.db.admin_inscribir_alumno(self.current_alumno_id, grupo_id) 
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos_disponibles(self.current_alumno_id, self.current_alumno_carrera_id)
                self.cargar_grupos_inscritos(self.current_alumno_id)
            else:
                messagebox.showerror("Error", msg)
                
    def baja_grupo(self):
        sel = self.tree_grupos.selection()
        if not sel:
            messagebox.showwarning("Validación", "Selecciona un grupo de la lista de inscritos"); return
        values = self.tree_grupos.item(sel[0], 'values')
        if not values: return
        
        inscripcion_id = int(values[0])
        grupo_nombre = str(values[1]) # El código del grupo

        if messagebox.askyesno("Confirmar Baja", f"¿Dar de baja a {self.var_nombre.get()} del grupo {grupo_nombre}?"):
            ok, msg = self.db.admin_dar_baja_materia(inscripcion_id)
            if ok:
                messagebox.showinfo("Éxito", msg)
                self.cargar_grupos_disponibles(self.current_alumno_id, self.current_alumno_carrera_id)
                self.cargar_grupos_inscritos(self.current_alumno_id)
            else:
                messagebox.showerror("Error", msg)