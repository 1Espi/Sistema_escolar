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
        
        self.lista_combo_disponibles = []
        self.lista_combo_seleccionadas = []
        
        self.setup_ui()
        self.cargar_usuarios()
        self.cargar_carreras()
        
        if self.user_info['TIPO'].lower() == 'alumno':
            query = "SELECT alumno_id FROM alumnos WHERE usuario_id = %s"
            result = self.db_connection.fetch_all(query, (self.user_info['ID'],))
            if not result:
                messagebox.showerror("Error", "No se encontró información de alumno asociada a este usuario")
                return
            self.id_busqueda.insert(0, result[0][0])
            self.cancelar_alumno()

    def setup_ui(self):
        title = tk.Label(self, text="Alumnos", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        self.id_busqueda = tk.Entry(self, state="normal")
        
        if self.user_info['TIPO'].lower() == 'administrador':
            tk.Label(self, text="Buscar por código:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
            
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
        self.entry_fecha_nacimiento.config(state="disabled")
        self.entry_fecha_nacimiento.grid(row=3, column=3, sticky="w", padx=5)
        self.entry_fecha_nacimiento.set_date(datetime.now())

        ttk.Label(self, text="Carrera:").grid(row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_carrera = ttk.Combobox(self, state="disabled")
        self.entry_carrera.grid(row=4, column=3, sticky="w", padx=5)
        self.entry_carrera.bind("<<ComboboxSelected>>", self.cargar_grupos)
        
        ttk.Label(self, text="Pre Registro:").grid(row=5, column=3, sticky="s", padx=5, pady=5)
        
        ttk.Label(self, text="Grupos:").grid(row=6, column=2, sticky="e", padx=5, pady=5)
        self.combo_materias_disponibles = ttk.Combobox(self, state="disabled")
        self.combo_materias_disponibles.grid(row=6, column=3, sticky="w", padx=5)
        self.combo_materias_disponibles.bind("<<ComboboxSelected>>", self.trigger_combo_disponibles)
        
        self.button_agregar = tk.Button(self, text="Agregar", command=self.agregar_grupo, state="disabled")
        self.button_agregar.grid(row=6, column=4, padx=5)
        
        ttk.Label(self, text="Seleccionados:").grid(row=7, column=2, sticky="e", padx=5, pady=5)
        self.combo_materias_seleccionadas = ttk.Combobox(self, state="disabled")
        self.combo_materias_seleccionadas.grid(row=7, column=3, sticky="w", padx=5)
        self.combo_materias_seleccionadas.bind("<<ComboboxSelected>>", self.trigger_combo_seleccionadas)

        self.button_quitar = tk.Button(self, text="Quitar", command=self.quitar_grupo, state="disabled")
        self.button_quitar.grid(row=7, column=4, padx=5)
        

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
        self.button_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_alumno, state="disabled")
        self.button_eliminar = tk.Button(self.frame_botones, text="Eliminar", command=self.eliminar_alumno, state="disabled")
        self.button_actualizar = tk.Button(self.frame_botones, text="Actualizar", command=self.actualizar_alumno, state="disabled")
        self.button_cancelar = tk.Button(self.frame_botones, text="Cancelar", command=self.cancelar_alumno, state="disabled")
        
        if self.user_info['TIPO'].lower() == 'administrador': 
            #BOTON QUE CONTROLA EL FLUJO DEL PREREGISTRO
            self.btn_preregistro = tk.Button(self.frame_botones, text="Activar Prerregistro",command=self.activar_prerregistro)
            self.btn_preregistro.grid(row=0, column=5, padx=5)
  
            self.button_crear.grid(row=0, column=0, padx=5)
            
            self.button_guardar.grid(row=0, column=1, padx=5)
            
            self.button_eliminar.grid(row=0, column=3, padx=5)

        
        self.button_actualizar.grid(row=0, column=2, padx=5)
    
        self.button_cancelar.grid(row=0, column=4, padx=5)

    #METODOS PARA CARGAR DATOS
    
    def trigger_combo_disponibles(self, event):
        self.button_agregar.config(state="normal")
        
    def trigger_combo_seleccionadas(self, event):
        self.button_quitar.config(state="normal")

    def activar_prerregistro(self):
        try:
            # Consulta para verificar si el prerregistro ya existe
            query = "SELECT estado FROM acciones WHERE descripcion = 'pre_registro'"
            registro = self.db_connection.fetch_one(query)

            if registro:  # Si el registro ya existe
                if registro[0] == 'activo':
                    # Prerregistro activo, preguntar si desea cerrarlo
                    respuesta = messagebox.askyesno("Prerregistro Activo", 
                                                    "El prerregistro ya está activo. ¿Desea cerrarlo?")
                    if respuesta:
                        # Cerrar el prerregistro
                        update_query = "UPDATE acciones SET estado = 'cerrado' WHERE descripcion = 'pre_registro'"
                        self.db_connection.execute_query(update_query)
                        self.generarInscripcionesEnBaseAlPreregistro()
                        messagebox.showinfo("Prerregistro", "El prerregistro se ha cerrado exitosamente.")
                else:
                    # Prerregistro inactivo, preguntar si desea activarlo
                    respuesta = messagebox.askyesno("Prerregistro Inactivo", 
                                                    "El prerregistro está inactivo. ¿Desea activarlo?")
                    if respuesta:
                        update_query = "UPDATE acciones SET estado = 'activo' WHERE descripcion = 'pre_registro'"
                        self.db_connection.execute_query(update_query)
                        messagebox.showinfo("Prerregistro", "El prerregistro se ha activado exitosamente.")
            else:
                # Si no existe un registro de 'pre_registro', crearlo y activarlo
                insert_query = "INSERT INTO acciones (descripcion, estado) VALUES ('pre_registro', 'activo')"
                self.db_connection.execute_query(insert_query)
                messagebox.showinfo("Prerregistro", "El prerregistro se ha creado y activado exitosamente.")

        except Exception as e:
            # Manejo de errores
            messagebox.showerror("Error", f"Error al gestionar el prerregistro: {e}")


    def generarInscripcionesEnBaseAlPreregistro(self):
        try:
            # Obtener los registros del pre_registro
            query_preregistro = "SELECT alumno_id, grupo_id FROM pre_registro"
            registros = self.db_connection.fetch_all(query_preregistro)

            if not registros:
                messagebox.showinfo("Prerregistro", "No hay registros en el pre_registro para procesar.")
                return

            for registro in registros:
                alumno_id = registro[0]  # Usar el índice para obtener alumno_id
                grupo_id = registro[1]  # Usar el índice para obtener grupo_id

                # Verificar si el grupo tiene un salón asignado
                query_grupo = "SELECT salon_id FROM grupos WHERE grupo_id = %s"
                grupo = self.db_connection.fetch_one(query_grupo, (grupo_id,))
                
                if not grupo or grupo[0] is None:  # Usar el índice para verificar salon_id
                    messagebox.showwarning("Prerregistro", f"El grupo {grupo_id} no tiene un salón asignado.")
                    continue

                salon_id = grupo[0]  # Usar el índice para obtener salon_id

                # Verificar si hay espacio disponible en el salón
                query_salon = "SELECT capacidad FROM salones WHERE salon_id = %s"
                salon = self.db_connection.fetch_one(query_salon, (salon_id,))

                if not salon or salon[0] <= 0:  # Usar el índice para verificar capacidad
                    messagebox.showwarning("Prerregistro", f"No hay espacio disponible en el salón con el ID {salon_id}.")
                    continue

                # Generar inscripción
                insert_inscripcion = """
                    INSERT INTO inscripciones (alumno_id, grupo_id) 
                    VALUES (%s, %s)
                """
                self.db_connection.execute_query(insert_inscripcion, (alumno_id, grupo_id))

                # Restar espacio en el salón
                update_salon = "UPDATE salones SET capacidad = capacidad - 1 WHERE salon_id = %s"
                self.db_connection.execute_query(update_salon, (salon_id,))

            # Eliminar registros del pre_registro después de procesarlos
            delete_preregistro = "DELETE FROM pre_registro"
            self.db_connection.execute_query(delete_preregistro)

            messagebox.showinfo("Prerregistro", "Las inscripciones se han generado exitosamente.")

        except Exception as e:
            # Manejo de errores
            messagebox.showerror("Error", f"Error al generar las inscripciones: {e}")



    def agregar_grupo(self):
        if self.combo_materias_disponibles.get() == "":
            messagebox.showerror("Error", "No se ha seleccionado ningun grupo")
            return
        self.combo_materias_disponibles.get()
        self.lista_combo_seleccionadas.append(self.combo_materias_disponibles.get())
        self.combo_materias_seleccionadas.config(values=self.lista_combo_seleccionadas)
        self.lista_combo_disponibles.remove(self.combo_materias_disponibles.get())
        self.combo_materias_disponibles.config(values=self.lista_combo_disponibles)
        self.combo_materias_disponibles.set("")
        self.button_agregar.config(state="disabled")
    
    def quitar_grupo(self):
        if self.combo_materias_seleccionadas.get() == "":
            messagebox.showerror("Error", "No se ha seleccionado ningun grupo")
            return
        self.combo_materias_seleccionadas.get()
        self.lista_combo_disponibles.append(self.combo_materias_seleccionadas.get())
        self.combo_materias_disponibles.config(values=self.lista_combo_disponibles)
        self.lista_combo_seleccionadas.remove(self.combo_materias_seleccionadas.get())
        self.combo_materias_seleccionadas.config(values=self.lista_combo_seleccionadas)
        self.combo_materias_seleccionadas.set("")
        self.button_quitar.config(state="disabled")

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
        
    def cargar_grupos(self, event):
        carrera_nombre = self.entry_carrera.get()
        carrera_id = None
        for carrera in self.todas_las_carreras:
            if carrera[0] == carrera_nombre:
                carrera_id = carrera[1]
                break
            
        if not carrera_id:
            messagebox.showerror("Error", "No se pudo seleccionar la carrera")
            return
        
        query = """
            SELECT 
                m.nombre, 
                g.grupo_id 
            FROM 
                grupos g
            JOIN 
                asignaciones a ON g.asignacion_id = a.asignacion_id
            JOIN 
                materias m ON a.materia_id = m.materia_id
            WHERE 
                m.carrera_id = %s;
            """
        result = self.db_connection.fetch_all(query, (carrera_id,))
        
        if not result:
            messagebox.showwarning("Advertencia", "La carrera no tiene grupos creados")
            return
        
        self.lista_combo_disponibles = []
        for grupo in result:
            if f"{grupo[0]} (ID:{grupo[1]})" not in self.lista_combo_seleccionadas:
                self.lista_combo_disponibles.append(f"{grupo[0]} (ID:{grupo[1]})")
        self.combo_materias_disponibles.config(values=self.lista_combo_disponibles)


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
        
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, END)

        for entry in [self.entry_id, self.entry_carrera, self.entry_estado]:
            entry.config(state="readonly")
            entry.delete(0, END)
            
        self.entry_fecha_nacimiento.set_date(datetime.now())
        
    def desbloquear_preregistro(self):
        query = "SELECT estado FROM acciones WHERE descripcion = 'pre_registro'"
        result = self.db_connection.fetch_all(query)
        if not result:
            return
        if result[0][0] != 'activo':
            return
        
        self.combo_materias_disponibles.config(state="readonly")
        self.combo_materias_seleccionadas.config(state="readonly")
        
        self.cargar_grupos(event=None)

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
        self.entry_fecha_nacimiento.config(state="normal")
        
        query = "SELECT grupo_id FROM pre_registro WHERE alumno_id = %s"
        result = self.db_connection.fetch_all(query, (id_alumno,))
        
        for grupo in result:
            query = """
                SELECT 
                    m.nombre, 
                    g.grupo_id 
                FROM 
                    grupos g
                JOIN 
                    asignaciones a ON g.asignacion_id = a.asignacion_id
                JOIN 
                    materias m ON a.materia_id = m.materia_id
                WHERE 
                    g.grupo_id = %s;
                """
            result = self.db_connection.fetch_all(query, (grupo[0],))
            if not result:
                continue
            self.lista_combo_seleccionadas.append(f"{result[0][0]} (ID:{result[0][1]})")
        
        self.combo_materias_seleccionadas.config(values=self.lista_combo_seleccionadas)
        
        self.rellenar_datos_usuario(event=None)
        self.desbloquear_preregistro()
                
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="normal")
        self.button_eliminar.config(state="normal")
        self.button_cancelar.config(state="normal")
    
    def crear_alumno(self):
        self.cargar_usuarios()
        self.entry_codigo.config(state="normal")
        self.entry_id.config(state="readonly")
        self.entry_carrera.config(state="readonly" if self.user_info['TIPO'].lower() == 'administrador' else "disabled")
        self.entry_fecha_nacimiento.config(state="normal")
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
        id_alumno = self.entry_codigo.get()
        id_usuario=self.entry_id.get()
        carrera_nombre = self.entry_carrera.get()
        estado = self.entry_estado.get()
        fecha_raw = self.entry_fecha_nacimiento.get_date()

        if not id_alumno or not id_usuario or not carrera_nombre or not estado or not fecha_raw: 
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

        query = "INSERT INTO alumnos (alumno_id, usuario_id, carrera_id, estado, fecha_nacimiento) VALUES (%s, %s, %s, %s, %s)"
        self.db_connection.execute_query(query, (id_alumno, id_usuario, id_carrera, estado, fecha_nacimiento))
        
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
        
        ids_grupos = [re.search(r'\(ID:(\d+)\)', grupo).group(1) for grupo in self.lista_combo_seleccionadas]
        
        grupos_placeholder = ",".join([str(id) for id in ids_grupos])

        query = None
        if grupos_placeholder:
            query = f"""
                DELETE FROM pre_registro
                WHERE alumno_id = %s
                AND grupo_id NOT IN ({grupos_placeholder});
            """
        else:
            query = "DELETE FROM pre_registro WHERE alumno_id = %s"

        self.db_connection.execute_query(query, (codigo_alumno,))
        
        query = "INSERT IGNORE INTO pre_registro (alumno_id, grupo_id) VALUES (%s, %s)"
        for id in ids_grupos:
            self.db_connection.execute_query(query, (codigo_alumno, id))
        
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
        for entry in [self.entry_codigo,  self.entry_id, self.entry_nombre, self.entry_apellido_paterno, self.entry_apellido_materno, self.entry_correo, self.entry_estado, self.entry_carrera]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
            
        self.entry_fecha_nacimiento.set_date(datetime.now())
        self.entry_fecha_nacimiento.config(state="disabled")
        
        
        self.combo_materias_disponibles.set("")
        self.combo_materias_seleccionadas.set("")
        self.lista_combo_disponibles = []
        self.lista_combo_seleccionadas = []
        self.combo_materias_disponibles.config(state="disabled", values=[])
        self.combo_materias_seleccionadas.config(state="disabled", values=[])
        
        self.button_agregar.config(state="disabled")
        self.button_quitar.config(state="disabled")
        
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")
        
        if self.user_info['TIPO'].lower() == 'alumno':
            self.buscar_alumno()
            self.entry_estado.config(state="disabled")
            self.entry_fecha_nacimiento.config(state="disabled")
            self.entry_carrera.config(state="disabled")
        

