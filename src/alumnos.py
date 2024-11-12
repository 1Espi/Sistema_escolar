import tkinter as tk
import utilities.connection as connfile
from tkinter import END, messagebox, ttk
from utilities.connection import MySQLConnection  # Importa la clase de conexión
from tkcalendar import DateEntry
from datetime import datetime
import re

class AlumnosFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info  # Información del usuario logueado
        self.db_connection = MySQLConnection()  # Crear instancia de la conexión a MySQL
        self.db_connection.connect()  # Conectar a la base de datos
        
        self.todas_las_carreras = None
        self.todos_los_usuarios = None

        self.setup_ui()
        self.cargar_usuarios()
        self.cargar_carreras()

    def setup_ui(self):
        title = tk.Label(self, text="Alumnos", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self, text="Buscar por código:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.id_busqueda = tk.Entry(self, state="normal")
        self.id_busqueda.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(self, text="Buscar", command=self.buscar_alumno).grid(row=1, column=2, padx=5, sticky='w')

        #ENTRYS DE LA IZQUIERDA
        tk.Label(self, text="Código de alumno:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_codigo = tk.Entry(self, state="disabled")
        self.entry_codigo.grid(row=2, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Id de usuario:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_id = ttk.Combobox(self, state="disabled")
        self.entry_id.grid(row=3, column=1, sticky="w", padx=5)
        self.entry_id.bind("<<ComboboxSelected>>", self.rellenar_datos_usuario)

        tk.Label(self, text="Nombre:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_nombre = tk.Entry(self, state="disabled")
        self.entry_nombre.grid(row=4, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Apellido paterno:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_apellido_paterno = tk.Entry(self, state="disabled")
        self.entry_apellido_paterno.grid(row=5, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Apellido materno:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_apellido_materno = tk.Entry(self, state="disabled")
        self.entry_apellido_materno.grid(row=6, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Email:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.entry_correo = tk.Entry(self, state="disabled")
        self.entry_correo.grid(row=7, column=1, sticky="w", padx=5)
        
        #ENTRYS DE LA DERECHA
        tk.Label(self, text="Estado:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_estado = ttk.Combobox(self, state="disabled", values=["Activo", "Egresado", "Titulado", "Baja Temporal", "Baja Definitiva", "Intercambio", "Suspensión", "Reingreso"])
        self.entry_estado.grid(row=2, column=3, sticky="w", padx=5)

        tk.Label(self, text="Fecha de nacimiento:").grid(row=3, column=2, sticky='e', padx=5, pady=4)
        self.entry_fecha_nacimiento = DateEntry(self, state='readonly', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_fecha_nacimiento.grid(row=3, column=3, sticky="w", padx=5)
        self.entry_fecha_nacimiento.set_date(datetime.now())

        ttk.Label(self, text="Carrera:").grid(row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_carrera = ttk.Combobox(self, state="disabled")
        self.entry_carrera.grid(row=4, column=3, sticky="w", padx=5)
        self.entry_carrera.bind("<<ComboboxSelected>>", self.cargar_materias)

        

        # Configurar la expansión de las columnas en la fila de los botones
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=1)
        # self.grid_columnconfigure(3, weight=1)
        # self.grid_columnconfigure(4, weight=1)

        #BOTONES
        self.frame_botones = tk.Frame(self)
        self.frame_botones.grid(row=8, column=0, columnspan=100, pady=10)
        
        self.button_crear = tk.Button(self.frame_botones, text="Crear", command=self.crear_alumno)
        self.button_crear.grid(row=0, column=0, padx=5)
        
        self.button_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_alumno, state="disabled")
        self.button_guardar.grid(row=0, column=1, padx=5)
        
        self.button_actualizar = tk.Button(self.frame_botones, text="Actualizar", command=self.actualizar_alumno, state="disabled")
        self.button_actualizar.grid(row=0, column=2, padx=5)
        
        self.button_eliminar = tk.Button(self.frame_botones, text="Eliminar", command=self.eliminar_alumno, state="disabled")
        self.button_eliminar.grid(row=0, column=3, padx=5)
    
        self.button_cancelar = tk.Button(self.frame_botones, text="Cancelar", command=self.cancelar_alumno, state="disabled")
        self.button_cancelar.grid(row=0, column=4, padx=5)

    #METODOS PARA CARGAR DATOS

    def cargar_carreras(self):
        query = "SELECT nombre, carrera_id FROM carreras"
        result = self.db_connection.fetch_all(query)
        self.todas_las_carreras = result.copy()
        
    def cargar_usuarios(self):
        self.todos_los_usuarios = None
        query = """
                    SELECT usuario_id 
                    FROM usuarios 
                    WHERE tipo = 'Alumno' 
                    AND usuario_id NOT IN (SELECT usuario_id FROM alumnos)
                """
        result = self.db_connection.fetch_all(query)
        self.todos_los_usuarios = result.copy()
        
    def cargar_materias(self, event):
        carrera_nombre = self.entry_carrera.get()
        carrera_id = None
        for carrera in self.todas_las_carreras:
            if carrera[0] == carrera_nombre:
                carrera_id = carrera[1]
                break
            
        if not carrera_id:
            messagebox.showerror("Error", "No se pudo seleccionar la carrera")
            return
        
        query = "SELECT nombre, materia_id FROM materias WHERE carrera_id = %s"
        result = self.db_connection.fetch_all(query, (carrera_id,))
        
        if not result:
            messagebox.showwarning("Advertencia", "La carrera no tiene materias ofertadas")
            return
        
        #AQUI SE LLENARIA UN COMBOBOX PARA AGREGAR MATERIAS A LAS AGENDADAS POR EL ALUMNO

    def rellenar_datos_usuario(self, event):
        id_usuario = self.entry_id.get()

        query = "SELECT nombre, correo FROM usuarios WHERE usuario_id = %s"
        result = self.db_connection.fetch_all(query, (id_usuario,))
        
        if not result:
            messagebox.showerror("Error", "No se obtuvo la información de este usuario")
            return
        
        usuario = result[0]
        full_name = usuario[0].split()

        self.entry_nombre.config(state="normal")
        self.entry_nombre.delete(0, END)
        self.entry_nombre.insert(0, full_name[0] if len(full_name) > 0 else "")
        self.entry_nombre.config(state="disabled")
        
        self.entry_apellido_paterno.config(state="normal")
        self.entry_apellido_paterno.delete(0, END)
        self.entry_apellido_paterno.insert(0, full_name[1] if len(full_name) > 1 else "")
        self.entry_apellido_paterno.config(state="disabled")
        
        self.entry_apellido_materno.config(state="normal")
        self.entry_apellido_materno.delete(0, END)
        self.entry_apellido_materno.insert(0, full_name[2] if len(full_name) > 2 else "")
        self.entry_apellido_materno.config(state="disabled")
        
        self.entry_correo.config(state="normal")
        self.entry_correo.delete(0, END)
        self.entry_correo.insert(0, usuario[1])
        self.entry_correo.config(state="disabled")

    #METODOS PARA REALIZAR LAS FUNCIONES PRINCIPALES

    def limpiar_campos(self):
        self.id_busqueda.delete(0, END)
        
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, END)

        for entry in [self.entry_id, self.entry_carrera, self.entry_estado]:
            entry.config(state="readonly")
            entry.delete(0, END)
            
        self.entry_fecha_nacimiento.set_date(datetime.now())

    def desbloquear_campos(self):
        self.entry_codigo.config(state="normal")
        self.entry_id.config(state="normal")
        self.entry_nombre.config(state="normal")
        self.entry_apellido_paterno.config(state="normal")
        self.entry_apellido_materno.config(state="normal")
        self.entry_correo.config(state="normal")
        self.entry_estado.config(state="normal")
        self.entry_carrera.config(state="normal")
        
    def entrys_modo_editar(self):
        self.entry_codigo.config(state="disabled")
        self.entry_id.config(state="readonly")
        self.entry_nombre.config(state="normal")
        self.entry_apellido_paterno.config(state="normal")
        self.entry_apellido_materno.config(state="normal")
        self.entry_correo.config(state="normal")
        self.entry_estado.config(state="normal")
        self.entry_carrera.config(state="normal")
        
    def buscar_alumno(self):
        self.cargar_usuarios()
        self.entry_id.config(values=self.todos_los_usuarios)
        id_alumno = self.id_busqueda.get()
        if not id_alumno:
            messagebox.showerror("Error", "Ingrese un id a buscar")
            return
        
        if not id_alumno.isdigit():
            messagebox.showerror("Error", "El id debe ser un entero")
            return

        query = "SELECT alumno_id, usuario_id, carrera_id, estado, fecha_nacimiento FROM alumnos WHERE alumno_id = %s"
        result = self.db_connection.fetch_all(query, (id_alumno,))

        if not result:
            messagebox.showerror("Error", "El alumno no se encontró en la base de datos")
            return
        
        self.desbloquear_campos()
        alumno = result[0]
        
        self.entry_codigo.delete(0, END)
        self.entry_codigo.insert(0, alumno[0])
        self.entry_codigo.config(state="disabled")
        
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, alumno[1])
        if self.user_info['TIPO'].lower() == 'administrador':
            self.entry_id.config(state="readonly")
        else:
            self.entry_id.config(state="disabled")
            

        carrera_id = alumno[2]
        carrera_nombre = None
        for carrera in self.todas_las_carreras:
            if carrera[1] == carrera_id:
                carrera_nombre = carrera[0]
                break

        if not carrera_nombre:
            messagebox.showerror("Error", "No se pudo encontrar la carrera del alumno")
            self.cancelar_alumno()
            return
        
        nombres_carreras = [item[0] for item in self.todas_las_carreras]
        nombres_carreras.remove(carrera_nombre)
        self.entry_carrera.config(values=nombres_carreras)
        
        self.entry_carrera.delete(0, END)
        self.entry_carrera.insert(0, carrera_nombre)
        self.entry_carrera.config(state="readonly")
                
        self.entry_estado.delete(0, END)
        self.entry_estado.insert(0, alumno[3])
        self.entry_estado.config(state="readonly")
                
        fecha_nacimiento = alumno[4].date()
        self.entry_fecha_nacimiento.set_date(fecha_nacimiento)
        
        self.rellenar_datos_usuario(event=None)
                
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="normal")
        self.button_eliminar.config(state="normal")
        self.button_cancelar.config(state="normal")
    
    def crear_alumno(self):
        self.cargar_usuarios()
        self.entry_codigo.config(state="normal")
        self.entry_id.config(state="readonly")
        self.entry_carrera.config(state="readonly")
        self.entry_estado.config(state="readonly")
        
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="normal")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="normal")
        
        nombres_carreras = [item[0] for item in self.todas_las_carreras]
        self.entry_carrera.config(values=nombres_carreras)
        self.entry_id.config(values=self.todos_los_usuarios)
        
        self.entry_fecha_nacimiento.set_date(datetime.now())
        
        query = "SELECT MAX(alumno_id) FROM alumnos"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_codigo.delete(0, END)
        self.entry_codigo.insert(0, max_id)
        self.entry_codigo.config(state="disabled")  
        

    
    def guardar_alumno(self):
        id_usuario=self.entry_id.get()
        carrera_nombre = self.entry_carrera.get()
        estado = self.entry_estado.get()
        fecha_raw = self.entry_fecha_nacimiento.get_date()

        if not id_usuario or not carrera_nombre or not estado or not fecha_raw: 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return
        
        id_carrera = None
        for carrera in self.todas_las_carreras:
            if carrera[0] == carrera_nombre:
                id_carrera = carrera[1]
                break
            
        fecha_nacimiento = datetime.strftime(fecha_raw, '%Y-%m-%d %H:%M:%S')
            
        if not id_carrera:
            messagebox.showerror("Error", "No se pudo obtener la carrera para hacer la insercion")
            return

        query = "INSERT INTO alumnos (usuario_id, carrera_id, estado, fecha_nacimiento) VALUES (%s, %s, %s, %s)"
        self.db_connection.execute_query(query, (id_usuario, id_carrera, estado, fecha_nacimiento))
        
        messagebox.showinfo("Éxito", "Alumno creado con éxito.")
        self.cargar_usuarios()
        self.entry_id.config(values=self.todos_los_usuarios)
        self.cancelar_alumno()


    def actualizar_alumno(self):
        codigo_alumno = self.entry_codigo.get()
        usuario_id = self.entry_id.get()
        carrera_nombre = self.entry_carrera.get()
        estado = self.entry_estado.get()
        fecha_raw = self.entry_fecha_nacimiento.get_date()

        if not usuario_id or not carrera_nombre or not estado or not fecha_raw: 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return

        if not usuario_id.isdigit():
            messagebox.showerror("Error", "ID inválido")
            return
        
        if not carrera_nombre:
            messagebox.showerror("Error", "No se pudo obtener la carrera para hacer la actualizacion")
            return
        
        id_carrera = None
        for carrera in self.todas_las_carreras:
            if carrera[0] == carrera_nombre:
                id_carrera = carrera[1]
                break
            
        fecha_nacimiento = datetime.strftime(fecha_raw, '%Y-%m-%d %H:%M:%S')

        query = "UPDATE alumnos SET usuario_id = %s, carrera_id = %s, estado = %s, fecha_nacimiento = %s WHERE alumno_id = %s"
        self.db_connection.execute_query(query, (usuario_id, id_carrera, estado, fecha_nacimiento, codigo_alumno))
        
        messagebox.showinfo("Éxito", "Alumno actualizado con éxito.")
        self.cargar_usuarios()
        self.entry_id.config(values=self.todos_los_usuarios)
        self.cancelar_alumno()


    def eliminar_alumno(self):
        user_id = self.id_busqueda.get()
        if not user_id.isdigit():
            messagebox.showerror("Error", "ID de alumno inválido.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás segur@ de que deseas eliminar este alumno?"):
            query = "DELETE FROM alumnos WHERE alumno_id = %s"
            self.db_connection.execute_query(query, (user_id,))
            messagebox.showinfo("Éxito", "Alumno eliminado con éxito.")
            self.cargar_usuarios()
            self.entry_id.config(values=self.todos_los_usuarios)
            self.cancelar_alumno()
            
    def cancelar_alumno(self):
        self.id_busqueda.delete(0, END)
        for entry in [self.entry_codigo,  self.entry_id, self.entry_nombre, self.entry_apellido_paterno, self.entry_apellido_materno, self.entry_correo, self.entry_estado, self.entry_carrera]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
            
        self.entry_fecha_nacimiento.set_date(datetime.now())
        
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")
        

