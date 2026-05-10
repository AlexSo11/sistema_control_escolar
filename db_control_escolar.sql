-- SIIAU 2.0 - Sistema de Control Escolar
CREATE DATABASE IF NOT EXISTS control_escolar;
USE control_escolar;

DROP TABLE IF EXISTS planeacion;
DROP TABLE IF EXISTS inscripcion;
DROP TABLE IF EXISTS grupo;
DROP TABLE IF EXISTS horario;
DROP TABLE IF EXISTS salon;
DROP TABLE IF EXISTS materia;
DROP TABLE IF EXISTS maestro;
DROP TABLE IF EXISTS alumno;
DROP TABLE IF EXISTS carrera;
DROP TABLE IF EXISTS usuario;

-- Tabla de Usuarios (Base para todos los perfiles)
CREATE TABLE usuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol ENUM('ADMIN','MAESTRO','ALUMNO') NOT NULL,
  nombre VARCHAR(150) NOT NULL,
  apellido_paterno VARCHAR(100),
  apellido_materno VARCHAR(100),
  telefono VARCHAR(20),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Carrera
CREATE TABLE carrera (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  descripcion TEXT,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Alumno (hereda de usuario)
CREATE TABLE alumno (
  id INT PRIMARY KEY,
  matricula VARCHAR(30) UNIQUE NOT NULL,
  carrera_id INT,
  fecha_nacimiento DATE,
  estado ENUM('ACTIVA','BAJA','COMPLETADA') DEFAULT 'ACTIVA',
  FOREIGN KEY (id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (carrera_id) REFERENCES carrera(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Maestro (hereda de usuario)
CREATE TABLE maestro (
  id INT PRIMARY KEY,
  numero_empleado VARCHAR(30) UNIQUE NOT NULL,
  especialidad VARCHAR(100),
  FOREIGN KEY (id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Materia
CREATE TABLE materia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(150) NOT NULL,
  creditos INT DEFAULT 0,
  carrera_id INT,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (carrera_id) REFERENCES carrera(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Salon
CREATE TABLE salon (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero VARCHAR(50) NOT NULL UNIQUE,
  capacidad INT DEFAULT 30,
  ubicacion VARCHAR(200),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Horario
CREATE TABLE horario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dia_semana ENUM('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO') NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  turno VARCHAR(30),
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Grupo
CREATE TABLE grupo (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(100) NOT NULL UNIQUE,
  materia_id INT NOT NULL,
  carrera_id INT,
  maestro_id INT,
  salon_id INT,
  horario_id INT,
  cupos INT DEFAULT 30,
  cupos_disponibles INT DEFAULT 30,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (materia_id) REFERENCES materia(id) ON DELETE CASCADE,
  FOREIGN KEY (carrera_id) REFERENCES carrera(id) ON DELETE SET NULL,
  FOREIGN KEY (maestro_id) REFERENCES maestro(id) ON DELETE SET NULL,
  FOREIGN KEY (salon_id) REFERENCES salon(id) ON DELETE SET NULL,
  FOREIGN KEY (horario_id) REFERENCES horario(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Inscripción
CREATE TABLE inscripcion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  alumno_id INT NOT NULL,
  grupo_id INT NOT NULL,
  fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('ACTIVA','BAJA','COMPLETADA') DEFAULT 'ACTIVA',
  FOREIGN KEY (alumno_id) REFERENCES alumno(id) ON DELETE CASCADE,
  FOREIGN KEY (grupo_id) REFERENCES grupo(id) ON DELETE CASCADE,
  UNIQUE KEY unique_inscripcion (alumno_id, grupo_id)
) ENGINE=InnoDB;

-- Planeación 
CREATE TABLE planeacion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  descripcion TEXT,
  generado_por INT,
  fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  archivo_referencia VARCHAR(255),
  FOREIGN KEY (generado_por) REFERENCES usuario(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Índices recomendados
CREATE INDEX idx_materia_carrera ON materia(carrera_id);
CREATE INDEX idx_grupo_materia ON grupo(materia_id);
CREATE INDEX idx_inscripcion_alumno ON inscripcion(alumno_id);
CREATE INDEX idx_inscripcion_grupo ON inscripcion(grupo_id);
CREATE INDEX idx_alumno_carrera ON alumno(carrera_id);

-- DATOS DE PRUEBA

-- Carreras de ejemplo
INSERT INTO carrera (nombre, descripcion) VALUES 
('Ingeniería en Computación', 'Carrera enfocada en el desarrollo de software y sistemas computacionales'),
('Ingeniería en Comunicaciones y Electrónica', 'Carrera enfocada en telecomunicaciones y sistemas electrónicos'),
('Licenciatura en Informática', 'Carrera enfocada en sistemas de información y bases de datos');

-- Materias de ejemplo para Ingeniería en Computación
INSERT INTO materia (codigo, nombre, creditos, carrera_id) VALUES
('CB224', 'Ingeniería de Software', 8, 1),
('CB101', 'Programación I', 8, 1),
('CB102', 'Estructuras de Datos', 8, 1),
('CB201', 'Bases de Datos', 8, 1),
('CB301', 'Redes de Computadoras', 8, 1);

-- Salones de ejemplo
INSERT INTO salon (numero, capacidad, ubicacion) VALUES
('A101', 35, 'Edificio A, Primer Piso'),
('A102', 40, 'Edificio A, Primer Piso'),
('B201', 30, 'Edificio B, Segundo Piso'),
('C301', 25, 'Edificio C, Tercer Piso');

-- Horarios de ejemplo
INSERT INTO horario (dia_semana, hora_inicio, hora_fin, turno) VALUES
('LUNES', '07:00:00', '09:00:00', 'Matutino'),
('LUNES', '09:00:00', '11:00:00', 'Matutino'),
('MARTES', '07:00:00', '09:00:00', 'Matutino'),
('MIERCOLES', '14:00:00', '16:00:00', 'Vespertino'),
('JUEVES', '16:00:00', '18:00:00', 'Vespertino');


-- VISTA ÚTIL: Información completa de usuarios
CREATE OR REPLACE VIEW vista_usuarios_completa AS
SELECT 
    u.id,
    u.email,
    u.rol,
    u.nombre,
    u.apellido_paterno,
    u.apellido_materno,
    u.telefono,
    u.fecha_creacion,
    CASE 
        WHEN u.rol = 'ALUMNO' THEN a.matricula
        WHEN u.rol = 'MAESTRO' THEN m.numero_empleado
        ELSE NULL
    END AS codigo_identificacion,
    CASE 
        WHEN u.rol = 'ALUMNO' THEN c.nombre
        WHEN u.rol = 'MAESTRO' THEN m.especialidad
        ELSE NULL
    END AS info_adicional
FROM usuario u
LEFT JOIN alumno a ON u.id = a.id
LEFT JOIN maestro m ON u.id = m.id
LEFT JOIN carrera c ON a.carrera_id = c.id;
