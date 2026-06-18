# Sistema de gestión de citas médicas con módulos de análisis y visualización de datos

Desarrollado como parte de la asignatura 101 "Programación aplicada a la Ciencia de Datos" del Programa de Maestría en Ciencia de Datos (Data Science) de la Universidad Nacional de Moquegua periodo 2026-2027

## Herramientas
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- MySQL

## Funcionalidades
- Gestión de usuarios con roles fijos
- Gestión de datos personales de pacientes
- Gestión de campañas de salud
- Gestión de citas médicas (reservación online y registro en persona)
- Gestión de atenciones médicas (generadas desde citas o campañas):
  - Gestión de análisis
  - Gestión de diagnosticos
  - Gestión de prescripciones
  - Gestión de vacunaciones
  - Gestión de procedimientos
- Reportes en formato Excel
- Visualización de datos en gráficos

## Como instalar y ejecutar el sistema
1. Clonar el repositorio con el comando "git clone"
2. Instalar Python 3.10.4 desde https://www.python.org/downloads/
3. Instalar MySQL Server 8.0.31 desde https://dev.mysql.com/downloads/installer/
4. Ejecutar MySQL Server y crear una base de datos
5. Ejecutar el comando "pip install -r requirements.txt" desde la carpeta del repositorio
6. Ejecutar el comando "flask db init" desde la carpeta del repositorio
7. Ejecutar el comando "flask db migrate" desde la carpeta del repositorio
8. Ejecutar el comando "flask db upgrade" desde la carpeta del repositorio
9. Ejecutar el comando "flask run" desde la carpeta del repositorio
10. Abrir el navegador web en el puerto indicado en la terminal
11. Iniciar sesión con el usuario "admin" y la contraseña "admin"