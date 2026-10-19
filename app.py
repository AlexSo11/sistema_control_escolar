"""

⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⡿⠗⠀⠠⠄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⠈⠑⢶⣶⡄
⢀⣶⣦⣸⠀⢼⣟⡇⠀⠀⢀⣀⠀⠘⡿⠃
⠀⢿⣿⣿⣄⠒⠀⠠⢶⡂⢫⣿⢇⢀⠃⠀
⠀⠈⠻⣿⣿⣿⣶⣤⣀⣀⣀⣂⡠⠊⠀⠀
⠀⠀⠀⠃⠀⠀⠉⠙⠛⠿⣿⣿⣧⠀⠀⠀
⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀
⠀⠀⠀⣷⣄⡀⠀⠀⠀⢀⣴⡟⠿⠃⠀⠀
⠀⠀⠀⢻⣿⣿⠉⠉⢹⣿⣿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠁

Desarrollo AlexWhite USER GIT AlexSo11
"""
#Sistema Integral de Información Académica Universitaria
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from conexion import ConexionDB
from UI.usuarios import UsuariosUI
from DB.dbUsuarios import DBUsuario
from UI.maestros import MaestrosUI
from UI.grupos import GruposUI
from UI.materias import MateriasUI
from UI.horarios import HorariosUI
from UI.alumnos import AlumnosUI
from UI.carreras import CarrerasUI
from UI.salones import SalonesUI
from UI.planeacion import PlaneacionUI
from DB.dbAlumnoVista import DBAlumnoVista
from UI.alumno_perfil import AlumnoPerfilUI
from UI.alumno_inscripcion import AlumnoInscripcionUI
from UI.alumno_horario import AlumnoHorarioUI

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MeTiFAA1E7',
    'database': 'control_escolar'
}

class App:    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SIIAU 2.0 - Sistema de Control Escolar")
        #self.root.geometry("350x280")
        self.root.resizable(True, True)
        
        # Configurar ícono (opcional)
        # self.root.iconbitmap('icon.ico')
        
        # Conexión a base de datos
        self.con = ConexionDB(**DB_CONFIG)
        self.db = DBUsuario(self.con)
        self.usuario_actual: Optional[Dict[str, Any]] = None
        
        # Variables de entry para login
        self.entry_user: Optional[ttk.Entry] = None
        self.entry_pass: Optional[ttk.Entry] = None
        
        # Verificar conexión
        if not self.con.verificar_conexion():
            messagebox.showerror(
                "Error de Conexión",
                "No se pudo conectar a la base de datos.\n\n"
                "Verifica que MySQL esté ejecutándose y que la base de datos 'control_escolar' exista."
            )
            self.root.destroy()
            return
        
        # Iniciar con pantalla de login
        self.build_login()

    def build_login(self):
        """Construye la pantalla de inicio de sesión"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        frm = ttk.Frame(self.root, padding=20)
        frm.pack(expand=True, fill='both')

        # Título
        ttk.Label(
            frm, 
            text="SIIAU 2.0", 
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(0, 5))
        
        ttk.Label(
            frm, 
            text="Sistema de Control Escolar", 
            font=("Segoe UI", 9)
        ).pack(pady=(0, 20))

        # Campo de usuario (email)
        ttk.Label(frm, text="Email:").pack(anchor='w')
        self.entry_user = ttk.Entry(frm, width=30)
        self.entry_user.pack(fill='x', pady=(0, 10))

        # Campo de contraseña
        ttk.Label(frm, text="Contraseña:").pack(anchor='w')
        self.entry_pass = ttk.Entry(frm, show="*", width=30)
        self.entry_pass.pack(fill='x', pady=(0, 15))

        btn_login = ttk.Button(
            frm, 
            text="Iniciar Sesión", 
            command=self.login,
            width=20
        )
        btn_login.pack(pady=5)

        # Botón para crear cuenta demo (MUCHO MÁS SIMPLE)
        ttk.Button(
            frm, 
            text="Crear cuenta (demo)", 
            command=self.crear_cuenta_demo
        ).pack(pady=10)

        # Info de ayuda
        ttk.Label(
            frm,
            text="Usuario demo: admin@demo.udg.mx\nContraseña: Demo123!",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(pady=(15, 0))
        
        # Atajos de teclado
        self.entry_pass.bind('<Return>', lambda e: self.login())
        self.entry_user.bind('<Return>', lambda e: self.entry_pass.focus()) # type: ignore
        
        # Focus inicial
        self.entry_user.focus()

    def crear_cuenta_demo(self):
        # Crear usuario admin si no existe
        exists = self.db.buscar_usuario_por_email('admin@demo.udg.mx')
        if not exists:
            ok, msg = self.db.crear_usuario(
                email='admin@demo.udg.mx',
                password='Demo123!',
                rol='ADMIN',
                nombre='Administrador Demo',
                apellido_paterno='Sistema',
                apellido_materno='UDG',
                telefono='3312345678'
            )
            if ok:
                messagebox.showinfo("Cuenta Demo", f"Admin creado: admin@demo.udg.mx\nContraseña: Demo123!")
            else:
                messagebox.showerror("Error", msg)
        
        # Crear usuario maestro si no existe
        exists = self.db.buscar_usuario_por_email('maestro@demo.udg.mx')
        if not exists:
            ok, msg = self.db.crear_usuario(
                email='maestro@demo.udg.mx',
                password='Demo123!',
                rol='MAESTRO', 
                nombre='Juan',
                apellido_paterno='Pérez',
                apellido_materno='Demo',
                telefono='3344556677'
            )
            if ok:
                messagebox.showinfo("Cuenta Demo", f"Maestro creado: maestro@demo.udg.mx\nContraseña: Demo123!")
        
        # Crear usuario alumno si no existe  
        exists = self.db.buscar_usuario_por_email('alumno@demo.udg.mx')
        if not exists:
            ok, msg = self.db.crear_usuario(
                email='alumno@demo.udg.mx',
                password='Demo123!',
                rol='ALUMNO',
                nombre='María',
                apellido_paterno='García', 
                apellido_materno='Demo',
                telefono='3377889900'
            )
            if ok:
                messagebox.showinfo("Cuenta Demo", f"Alumno creado: alumno@demo.udg.mx\nContraseña: Demo123!")

        # Autocompletar con admin demo
        self.entry_user.delete(0, tk.END)
        self.entry_user.insert(0, 'admin@demo.udg.mx')
        self.entry_pass.delete(0, tk.END) 
        self.entry_pass.insert(0, 'Demo123!')

    def login(self):
        if self.entry_user is None or self.entry_pass is None:
            return
            
        email = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        
        # Validaciones básicas
        if not email or not password:
            messagebox.showwarning(
                "Validación", 
                "Por favor, introduce email y contraseña."
            )
            return
        
        # Autenticar usuario
        ok, resp = self.db.autenticar(email, password)
        
        if ok and isinstance(resp, dict):
            # VERIFICACIÓN CRÍTICA: Asegurar que resp no sea None
            if resp is None:
                messagebox.showerror("Error", "Error interno: datos de usuario vacíos")
                return
                
            self.usuario_actual = resp
            
            # VERIFICAR que usuario_actual tenga los campos esenciales
            if not self.usuario_actual.get('id') or not self.usuario_actual.get('rol'):
                messagebox.showerror("Error", "Datos de usuario incompletos")
                self.usuario_actual = None
                return
            
            # Solo para alumnos, cargar perfil adicional
            if self.usuario_actual.get('rol') == "ALUMNO":
                try:
                    # VERIFICAR CONEXIÓN PRIMERO
                    if not hasattr(self, 'con') or self.con is None:
                        messagebox.showerror("Error", "Conexión a BD no disponible")
                        return
                        
                    db_vista_alumno = DBAlumnoVista(self.con)
                    perfil_completo = db_vista_alumno.get_mi_perfil(self.usuario_actual['id'])
                    
                    if perfil_completo:
                        self.usuario_actual.update(perfil_completo)
                    # Si no hay perfil adicional no es fatal: se usan los datos del login.
                        
                except Exception as e:
                    print(f"Error al cargar el perfil del alumno: {e}")
                    # No es fatal, continuar con datos básicos del login
            
            # CONSTRUIR MENÚ (esto debe ejecutarse SIEMPRE)
            self.build_menu()
            
        else:
            # resp es un string con el mensaje de error
            mensaje_error = str(resp) if resp else "Error desconocido en autenticación"
            messagebox.showerror("Error de Autenticación", mensaje_error)
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.focus()

    def build_menu(self):
        # VERIFICACIÓN CRÍTICA: usuario_actual no debe ser None
        if self.usuario_actual is None:
            messagebox.showerror("Error", "Sesión no válida. Por favor, inicie sesión nuevamente.")
            self.cerrar_sesion()
            return

        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Redimensionar ventana
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        # Menú superior
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        
        # Header con información del usuario - CON VERIFICACIONES
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill='x')
        
        # Usar get() con valores por defecto para evitar NoneType
        nombre = self.usuario_actual.get('nombre', 'Usuario')
        apellido = self.usuario_actual.get('apellido_paterno', '')
        rol = self.usuario_actual.get('rol', 'DESCONOCIDO')
        email = self.usuario_actual.get('email', '')
        
        ttk.Label(
            header, 
            text=f"Bienvenido: {nombre} {apellido}",
            font=("Segoe UI", 12, "bold")
        ).pack(side='left')
        
        ttk.Label(
            header, 
            text=f"Rol: {rol}  |  {email}",
            font=("Segoe UI", 9)
        ).pack(side='right')

        # Notebook (pestañas) para los módulos
        tab_control = ttk.Notebook(self.root)

        # === MÓDULOS SEGÚN EL ROL ===
        if rol == 'ADMIN':
            self._crear_tabs_admin(tab_control)
        elif rol == 'MAESTRO':
            self._crear_tabs_maestro(tab_control)
        elif rol == 'ALUMNO':
            self._crear_tabs_alumno(tab_control)
        else:
            messagebox.showerror("Error", f"Rol no reconocido: {rol}")
            self.cerrar_sesion()
            return

        tab_control.pack(fill='both', expand=True, padx=5, pady=5)

    def _crear_tabs_admin(self, tab_control: ttk.Notebook):
        """Crea las pestañas para el rol ADMINISTRADOR"""
        
        # Validar que usuario_actual no sea None
        if self.usuario_actual is None:
            return
        
        # Tab: Usuarios (RF2)
        tab_usuarios = ttk.Frame(tab_control)
        tab_control.add(tab_usuarios, text='Usuarios')
        UsuariosUI(tab_usuarios, self.usuario_actual)
        
        # Tab: Carreras (RF5)
        tab_carreras = ttk.Frame(tab_control)
        tab_control.add(tab_carreras, text='Carreras')
        CarrerasUI(tab_carreras, self.usuario_actual)
        
        # Tab: Materias (RF5)
        tab_materias = ttk.Frame(tab_control)
        tab_control.add(tab_materias, text='Materias')
        MateriasUI(tab_materias, self.usuario_actual)
        
        # Tab: Salones (RF5)
        tab_salones = ttk.Frame(tab_control)
        tab_control.add(tab_salones, text='Salones')
        SalonesUI(tab_salones, self.usuario_actual)
        
        # Tab: Horarios (RF5)
        tab_horarios = ttk.Frame(tab_control)
        tab_control.add(tab_horarios, text='Horarios')
        HorariosUI(tab_horarios, self.usuario_actual)
        
        # Tab: Maestros (RF5)
        tab_maestros = ttk.Frame(tab_control)
        tab_control.add(tab_maestros, text='Maestros')
        MaestrosUI(tab_maestros, self.usuario_actual)
        
        # Tab: Alumnos (RF5)
        tab_alumnos = ttk.Frame(tab_control)
        tab_control.add(tab_alumnos, text='Alumnos')
        AlumnosUI(tab_alumnos, self.usuario_actual)
        
        # Tab: Grupos (RF6)
        tab_grupos = ttk.Frame(tab_control)
        tab_control.add(tab_grupos, text='Grupos')
        GruposUI(tab_grupos, self.usuario_actual)
        
        # Tab: Planeación (RF7)
        tab_planeacion = ttk.Frame(tab_control)
        tab_control.add(tab_planeacion, text='Planeación')
        PlaneacionUI(tab_planeacion, self.usuario_actual)
        
    def _crear_tabs_maestro(self, tab_control):
        """Crea las pestañas para el rol MAESTRO"""
        
        # Tab: Mi Perfil (RF4)
        tab_perfil = ttk.Frame(tab_control)
        tab_control.add(tab_perfil, text='Mi Perfil')
        MaestrosUI(tab_perfil, self.usuario_actual)
        
        # Tab: Mis Grupos
        #tab_grupos = ttk.Frame(tab_control)
        #tab_control.add(tab_grupos, text='Mis Grupos')
        #AlumnoHorarioUI(tab_grupos, self.usuario_actual)

    def _crear_tabs_alumno(self, tab_control):
        """Crea las pestañas para el rol ALUMNO"""
        
        # VERIFICAR que usuario_actual no sea None
        if self.usuario_actual is None:
            print("ERROR: No se pueden crear tabs para alumno - usuario_actual es None")
            return
            
        # Tab: Mi Perfil
        tab_perfil = ttk.Frame(tab_control)
        tab_control.add(tab_perfil, text='Mi Perfil')
        AlumnoPerfilUI(tab_perfil, self.usuario_actual, self.con)
        
        # Tab: Inscripciones (RF3)
        tab_inscripciones = ttk.Frame(tab_control)
        tab_control.add(tab_inscripciones, text='Inscripciones')
        AlumnoInscripcionUI(tab_inscripciones, self.usuario_actual, self.con)
        
        # Tab: Mi Horario
        tab_horario = ttk.Frame(tab_control)
        tab_control.add(tab_horario, text='Mi Horario')
        AlumnoHorarioUI(tab_horario, self.usuario_actual, self.con)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Deseas cerrar sesión?"):
            self.usuario_actual = None
            #self.root.geometry("350x350")
            self.root.resizable(False, False)
            self.build_login()

    def mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de SIIAU 2.0",
            "SIIAU 2.0 - Sistema de Control Escolar\n\n"
            "Universidad de Guadalajara - CUCEI\n"
            "División de Tecnologías para la Integración Ciber-Humana\n"
            "Departamento de Ciencias Computacionales\n\n"
            "Materia: Ingeniería de Software (CB224)\n"
            "Sección: D02 - NRC: 209845\n"
            "Profesor: Ramiro Lupercio Coronel\n\n"
            "Equipo de Desarrollo:\n"
            "• González Velázquez Mariana\n"
            "• Ramírez Llamas Anahí\n"
            "• Solís Quiñones Héctor Alejandro\n\n"
            "Versión: 1.0 (2025-B)"
        )


def main():
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')  # Se puede cambiar a: 'alt', 'default', 'classic', 'vista', 'xpnative'
    
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
