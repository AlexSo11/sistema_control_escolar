# Sistema de Control Escolar

Plataforma de escritorio para la administración académica de una institución
educativa. Centraliza usuarios, carreras, materias, salones, horarios, maestros,
alumnos, grupos e inscripciones en una sola aplicación **Python + Tkinter**
sobre **MySQL**.

## Roles y funcionalidades

| Rol | Módulos disponibles |
|---|---|
| **ADMIN** | Usuarios, Carreras, Materias, Salones, Horarios, Maestros, Alumnos, Grupos, Planeación |
| **MAESTRO** | Mi Perfil |
| **ALUMNO** | Mi Perfil, Inscripciones, Mi Horario |

El login autentica contra la tabla `usuario` y construye las pestañas según el
rol. Para los alumnos se carga además el perfil desde la vista/consulta
correspondiente.

## Requisitos

- Python 3.10+
- MySQL (XAMPP, MySQL Server o MariaDB)
- Dependencias:

```bash
pip install -r requirements.txt
```

## Base de datos

1. Crear la base de datos `control_escolar`.
2. Importar el esquema:

```bash
mysql -u root -p control_escolar < db_control_escolar.sql
```

3. Ajustar las credenciales de conexión en:
   - `conexion.py` → valores por defecto del constructor `ConexionDB`.
   - `app.py` → diccionario `DB_CONFIG` que se pasa a `ConexionDB`.

Tablas creadas por el script: `usuario`, `carrera`, `alumno`, `maestro`,
`materia`, `salon`, `horario`, `grupo`, `inscripcion` y `planeacion`.

## Ejecución

```bash
python app.py
```

La pantalla de login incluye un botón **"Crear cuenta (demo)"** que da de alta
tres usuarios si no existen:

| Email | Contraseña | Rol |
|---|---|---|
| `admin@demo.udg.mx` | `Demo123!` | ADMIN |
| `maestro@demo.udg.mx` | `Demo123!` | MAESTRO |
| `alumno@demo.udg.mx` | `Demo123!` | ALUMNO |

## Estructura

```
app.py                  Punto de entrada: login, menú y pestañas por rol
conexion.py             Conexión a MySQL (clase ConexionDB)
db_control_escolar.sql  Script de creación del esquema

DB/
  dbUsuarios.py         Usuarios y autenticación (hash SHA-256)
  dbAlumnos.py          Alumnos
  dbAlumnoVista.py      Perfil/inscripciones/horario del alumno
  dbMaestros.py         Maestros
  dbCarreras.py         Carreras
  dbMaterias.py         Materias
  dbSalones.py          Salones
  dbHorarios.py         Horarios
  dbGrupos.py           Grupos
  dbPlaneacion.py       Planeación

UI/
  usuarios.py           CRUD de usuarios
  alumnos.py            CRUD de alumnos
  maestros.py           CRUD de maestros
  carreras.py           CRUD de carreras
  materias.py           CRUD de materias
  salones.py            CRUD de salones
  horarios.py           CRUD de horarios
  grupos.py             CRUD de grupos
  planeacion.py         Planeación académica
  alumno_perfil.py      Perfil del alumno
  alumno_inscripcion.py Inscripciones del alumno
  alumno_horario.py     Horario del alumno
  maestroHorario.py     Horario (vista de maestro)
```

Cada clase de `DB/` recibe una instancia de `ConexionDB` y devuelve tuplas
`(ok, datos)` o `(ok, mensaje)`. Las clases de `UI/` construyen su interfaz
sobre el `ttk.Frame` (pestaña) que reciben.

## Notas y limitaciones conocidas

- **Credenciales hardcodeadas:** la contraseña de MySQL (`MeTiFAA1E7`) está
  escrita directamente en `conexion.py` y en `DB_CONFIG` de `app.py`. No se
  modificó el código; se recomienda moverla a variables de entorno.
- **Hash de contraseñas:** se usa SHA-256 sin sal (`hash_password`). Para
  producción conviene un algoritmo dedicado (bcrypt/argon2).
- Las cuentas demo y sus contraseñas son públicas (`Demo123!`); deben eliminarse
  o cambiarse antes de un despliegue real.
- La aplicación abre y cierra una conexión por operación (no usa pool).
