-- Crear base de datos
CREATE DATABASE sistema_control_escolar;
USE sistema_control_escolar;

-- Tabla de usuarios
CREATE TABLE usuarios (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    tipo ENUM('Administrador', 'Maestro', 'Alumno') NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de carreras
CREATE TABLE carreras (
    carrera_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Tabla de materias
CREATE TABLE materias (
    materia_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    carrera_id INT,
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE SET NULL
);

-- Tabla de alumnos
CREATE TABLE alumnos (
    alumno_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT,
    carrera_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE,
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE SET NULL
);

-- Tabla de maestros
CREATE TABLE maestros (
    maestro_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id) ON DELETE CASCADE
);

-- Tabla de horarios
CREATE TABLE horarios (
    horario_id INT PRIMARY KEY AUTO_INCREMENT,
    dia ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado') NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

-- Tabla de salones
CREATE TABLE salones (
    salon_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL
);

-- Tabla de grupos
CREATE TABLE grupos (
    grupo_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    carrera_id INT,
    maestro_id INT,
    horario_id INT,
    salon_id INT,
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE SET NULL,
    FOREIGN KEY (maestro_id) REFERENCES maestros(maestro_id) ON DELETE SET NULL,
    FOREIGN KEY (horario_id) REFERENCES horarios(horario_id) ON DELETE SET NULL,
    FOREIGN KEY (salon_id) REFERENCES salones(salon_id) ON DELETE SET NULL
);

-- Tabla de inscripciones de alumnos en grupos
CREATE TABLE inscripciones (
    inscripcion_id INT PRIMARY KEY AUTO_INCREMENT,
    alumno_id INT,
    grupo_id INT,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(alumno_id) ON DELETE CASCADE,
    FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id) ON DELETE CASCADE
);

-- Tabla de asignación de materias a maestros en cada carrera
CREATE TABLE asignaciones (
    asignacion_id INT PRIMARY KEY AUTO_INCREMENT,
    maestro_id INT,
    materia_id INT,
    carrera_id INT,
    FOREIGN KEY (maestro_id) REFERENCES maestros(maestro_id) ON DELETE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(materia_id) ON DELETE CASCADE,
    FOREIGN KEY (carrera_id) REFERENCES carreras(carrera_id) ON DELETE SET NULL
);