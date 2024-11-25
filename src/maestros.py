import tkinter as tk
from tkinter import END, messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime
from utilities.connection import MySQLConnection

class MaestrosFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        
        self.todas_las_carreras = None
        self.materias_de_carrera = None
        self.todos_los_usuarios = None
        self.todas_las_materias = None
        
        self.lista_combo_materias = []
        
        self.lista_materias_seleccionadas = []
        
        self.setup_ui()
        self.cargar_carreras()
        self.cargar_usuarios()
        self.cargar_materias()

    def setup_ui(self):
        title = tk.Label(self, text="Maestros", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        #ENTRYS
        
        tk.Label(self, text="Buscar por código:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.id_busqueda = tk.Entry(self, state="normal")
        self.id_busqueda.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(self, text="Buscar", command=self.buscar_maestro).grid(row=1, column=2, padx=5, sticky='w')

        #ENTRYS DE LA IZQUIERDA
        tk.Label(self, text="Código de maestro:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_codigo = tk.Entry(self, state="disabled")
        self.entry_codigo.grid(row=2, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Id usuario:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
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
        ttk.Label(self, text="Grado de estudios:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.combo_grado_estudios = ttk.Combobox(self, values= ["Licenciatura", "Maestria", "Doctorado"], state="disabled")
        self.combo_grado_estudios.grid(row=2, column=3, sticky="w", padx=5)

        tk.Label(self, text="Carrera:").grid(row=3, column=2, sticky="e", padx=5, pady=5)
        self.combo_carrera = ttk.Combobox(self, state="disabled")
        self.combo_carrera.grid(row=3, column=3, sticky="w", padx=5)
        self.combo_carrera.bind("<<ComboboxSelected>>", self.cargar_materias_de_carrera)

        tk.Label(self, text="Materia:").grid(row=4, column=2, sticky="e", padx=5, pady=5)
        self.combo_materia = ttk.Combobox(self, state="disabled")
        self.combo_materia.grid(row=4, column=3, sticky="w", padx=5)
        self.combo_materia.bind("<<ComboboxSelected>>", lambda event: self.button_agregar_materia.config(state="normal"))
        
        #BOTON DE AGREGAR MATERIA
        self.button_agregar_materia = tk.Button(self, text="Agregar", command=self.agregar_materia, state="disabled")
        self.button_agregar_materia.grid(row=5, column=3, padx=5)
        
        tk.Label(self, text="Materias que imparte:").grid(row=2, column=4, sticky="s", padx=5, pady=5)
        
        self.frameTreeview = tk.Frame(self)
        self.frameTreeview.grid(row=3, column=4, rowspan=5, pady=10)

        self.tree_materias = ttk.Treeview(self.frameTreeview, columns=("nombre", "carrera"), show="headings")
        self.tree_materias.heading("nombre", text="Nombre")
        self.tree_materias.heading("carrera", text="Carrera")
        self.tree_materias.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #BOTON DE QUITAR MATERIA
        self.button_quitar_materia = tk.Button(self, text="Quitar", command=self.quitar_materia, state="disabled")
        self.button_quitar_materia.grid(row=6, column=3, padx=5)

        self.tree_materias.bind("<ButtonRelease-1>", self.seleccionar_materia)
        
        #BOTONES
        self.frame_botones = tk.Frame(self)
        self.frame_botones.grid(row=8, column=0, columnspan=100, pady=10)
        
        self.button_crear = tk.Button(self.frame_botones, text="Crear", command=self.crear_maestro)
        self.button_crear.grid(row=0, column=0, padx=5)
        
        self.button_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_maestro, state="disabled")
        self.button_guardar.grid(row=0, column=1, padx=5)
        
        self.button_actualizar = tk.Button(self.frame_botones, text="Actualizar", command=self.actualizar_maestro, state="disabled")
        self.button_actualizar.grid(row=0, column=2, padx=5)
        
        self.button_eliminar = tk.Button(self.frame_botones, text="Eliminar", command=self.eliminar_maestro, state="disabled")
        self.button_eliminar.grid(row=0, column=3, padx=5)
    
        self.button_cancelar = tk.Button(self.frame_botones, text="Cancelar", command=self.cancelar_maestro, state="disabled")
        self.button_cancelar.grid(row=0, column=4, padx=5)

    def limpiar_treeview(self):
        for item in self.tree_materias.get_children():
            self.tree_materias.delete(item)
    
    def cargar_carreras(self):
        query = "SELECT nombre, carrera_id FROM carreras"
        result = self.db_connection.fetch_all(query)
        self.todas_las_carreras = result.copy()
        
    def cargar_usuarios(self):
        self.todos_los_usuarios = None
        query = """
                    SELECT usuario_id 
                    FROM usuarios 
                    WHERE tipo = 'Maestro' 
                    AND usuario_id NOT IN (SELECT usuario_id FROM maestros)
                """
        result = self.db_connection.fetch_all(query)
        self.todos_los_usuarios = result.copy()
        
    def cargar_materias(self):
        query = "SELECT materia_id, carrera_id, nombre FROM materias"
        result = self.db_connection.fetch_all(query)
        self.todas_las_materias = result.copy()
        
    def cargar_materias_de_carrera(self, event):
        nombre_carrera = self.combo_carrera.get()
        
        self.combo_materia.set("")
        
        carrera = None
        for item in self.todas_las_carreras:
            if item[0] == nombre_carrera:
                carrera = item[1]
                break
            
        if not carrera:
            messagebox.showerror("Error", "No se encontró la carrera seleccionada")
            return
        
        query = "SELECT materia_id, nombre FROM materias WHERE carrera_id = %s"
        result = self.db_connection.fetch_all(query, (carrera,))
        self.materias_de_carrera = result.copy()
        
        self.lista_combo_materias = [
            item[1]
            for item in self.materias_de_carrera
            if item[1] not in {materia[0] for materia in self.lista_materias_seleccionadas}
        ]

        self.combo_materia.config(values=self.lista_combo_materias)
        
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

    def seleccionar_materia(self, event):
        seleccion = self.tree_materias.selection()
        if not seleccion:  # Verifica si no hay elementos seleccionados
            return  # Sale de la función si no hay selección

        item = seleccion[0]  # Obtén el primer ítem seleccionado
        values = self.tree_materias.item(item, "values")
        self.seleccionado = values[0]
        self.button_quitar_materia.config(state="normal")

    def agregar_materia(self):
        materia = self.combo_materia.get()
        carrera = self.combo_carrera.get()
        
        if not materia or not carrera:
            messagebox.showerror("Error", "Selecciona una materia y una carrera")
            return
        
        self.lista_materias_seleccionadas.append((materia, carrera))
        self.lista_combo_materias.remove(materia)
        self.combo_materia.config(values=self.lista_combo_materias)
        self.combo_materia.set("")
        
        self.tree_materias.insert("", "end", values=(materia, carrera))
    
    def quitar_materia(self):
        entry_carrera = self.combo_carrera.get()
        item = self.tree_materias.selection()[0]
        
        valores = self.tree_materias.item(item, "values")
        materia = valores[0]
        carrera = valores[1]
        
        self.lista_materias_seleccionadas.remove((materia, carrera))
        
        if entry_carrera == carrera:
            self.lista_combo_materias.append(materia)
            self.combo_materia.config(values=self.lista_combo_materias)
            
        self.tree_materias.delete(item)
        self.button_quitar_materia.config(state="disabled")

    def obtener_ids_de_materias(self, listado, maestro_id):

        carreras_dict = {nombre: carrera_id for nombre, carrera_id in self.todas_las_carreras}
        
        # Crear un listado de materia_id basado en los nombres de materia y carrera
        ids_materias = []
        for nombre_materia, nombre_carrera in listado:
            # Verifica si la carrera existe
            carrera_id = carreras_dict.get(nombre_carrera)
            if carrera_id:
                # Busca las materias con ese nombre y carrera_id
                for materia_id, materia_carrera_id, materia_nombre in self.todas_las_materias:
                    if materia_nombre == nombre_materia and materia_carrera_id == carrera_id:
                        ids_materias.append((maestro_id, materia_id))
                        break  
        
        return ids_materias

    def buscar_maestro(self):
        self.cargar_usuarios()
        self.entry_id.config(values=self.todos_los_usuarios)

        self.combo_carrera.set("")
        self.combo_materia.set("")
        self.combo_materia.config(values=[])
        
        id_maestro = self.id_busqueda.get()

        if not id_maestro:
            messagebox.showerror("Error", "Ingrese un id a buscar")
            return
        
        if not id_maestro.isdigit():
            messagebox.showerror("Error", "El id debe ser un entero")
            return

        query = "SELECT maestro_id, usuario_id, grado_estudios FROM maestros WHERE maestro_id = %s"
        result = self.db_connection.fetch_all(query, (id_maestro,))

        if not result:
            messagebox.showinfo("Información", "No se encontrón el maestro")
            return
        
        maestro = result[0]
        
        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, END)
        self.entry_codigo.insert(0, maestro[0])
        self.entry_codigo.config(state="disabled")
        
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, maestro[1])
        if self.user_info['TIPO'].lower() == 'administrador':
            self.entry_id.config(state="readonly")
        else:
            self.entry_id.config(state="disabled")
        
        self.rellenar_datos_usuario(None)
        
        self.combo_grado_estudios.set(maestro[2])
        
        if self.user_info['TIPO'].lower() == 'administrador':
            self.entry_id.config(state="readonly")
            self.combo_grado_estudios.config(state="readonly")
        else:
            self.entry_id.config(state="disabled")
            self.combo_grado_estudios.config(state="disabled")
            
            
        query = """
            SELECT 
                m.nombre AS materia_nombre,
                c.nombre AS carrera_nombre
            FROM 
                maestros_materias mm
            JOIN 
                materias m ON mm.materia_id = m.materia_id
            JOIN 
                carreras c ON m.carrera_id = c.carrera_id
            WHERE 
                mm.maestro_id = %s;
        """
        
        result = self.db_connection.fetch_all(query, (id_maestro,))
            
        self.lista_materias_seleccionadas = result.copy()
        
        self.limpiar_treeview()
        
        for item in result:
            self.tree_materias.insert("", "end", values=(item[0], item[1]))
            
        self.combo_carrera.config(state="readonly", values=[item[0] for item in self.todas_las_carreras])
        self.combo_materia.config(state="readonly")
            
        self.button_agregar_materia.config(state="disabled")
        self.button_quitar_materia.config(state="disabled")
                
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="normal")
        self.button_eliminar.config(state="normal")
        self.button_cancelar.config(state="normal")

    def crear_maestro(self):
        self.cargar_usuarios()
        self.entry_codigo.config(state="normal")
        self.entry_id.config(state="readonly")
        self.combo_grado_estudios.config(state="readonly")
        self.combo_materia.config(state="readonly")
        self.combo_carrera.config(state="readonly")
        
        self.button_agregar_materia.config(state="normal")
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="normal")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="normal")
        
        nombres_carreras = [item[0] for item in self.todas_las_carreras]
        self.combo_carrera.config(values=nombres_carreras)
        self.entry_id.config(values=self.todos_los_usuarios)
        
        query = "SELECT MAX(maestro_id) FROM maestros"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_codigo.delete(0, END)
        self.entry_codigo.insert(0, max_id)
        self.entry_codigo.config(state="disabled")  
        
    def guardar_maestro(self):
        maestro_id = self.entry_codigo.get()
        id_usuario=self.entry_id.get()
        grado_estudios = self.combo_grado_estudios.get()
        
        if not maestro_id or not id_usuario or not grado_estudios: 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return
        
        if self.tree_materias.get_children() == ():
            messagebox.showerror("Error", "Debes seleccionar al menos una materia.")
            return
        
        materia_carrera = []
        for item in self.tree_materias.get_children():
            fila = self.tree_materias.item(item, "values")
            materia_carrera.append(fila)
            
        maestros_materias = self.obtener_ids_de_materias(materia_carrera, maestro_id)
    
        query = "INSERT INTO maestros (maestro_id, usuario_id, grado_estudios) VALUES (%s, %s, %s)"
        self.db_connection.execute_query(query, (maestro_id, id_usuario, grado_estudios))
        
        query = "INSERT INTO maestros_materias (maestro_id, materia_id) VALUES (%s, %s)"
        self.db_connection.execute_many(query, maestros_materias)
        
        messagebox.showinfo("Éxito", "Maestro ingresado con éxito.")
        self.cargar_usuarios()
        self.entry_id.config(values=self.todos_los_usuarios)
        self.cancelar_maestro()
    
    def actualizar_maestro(self):
        maestro_id = self.entry_codigo.get()
        id_usuario=self.entry_id.get()
        grado_estudios = self.combo_grado_estudios.get()
        
        if not maestro_id or not id_usuario or not grado_estudios: 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return
        
        if self.tree_materias.get_children() == ():
            messagebox.showerror("Error", "Debes seleccionar al menos una materia.")
            return
        
        materia_carrera = []
        for item in self.tree_materias.get_children():
            fila = self.tree_materias.item(item, "values")
            materia_carrera.append(fila)
            
        maestros_materias = self.obtener_ids_de_materias(materia_carrera, maestro_id)
        
        materias = tuple([materia_id for _, materia_id in maestros_materias])
        
        query = "UPDATE maestros SET usuario_id = %s, grado_estudios = %s WHERE maestro_id = %s"
        self.db_connection.execute_query(query, (id_usuario, grado_estudios, maestro_id))
        
        materias_placeholder = ', '.join(str(materia_id) for materia_id in materias)

        query = f"""
            DELETE FROM maestros_materias
            WHERE maestro_id = %s
            AND materia_id NOT IN ({materias_placeholder});
        """

        self.db_connection.execute_query(query, (maestro_id,))
        
        query = "INSERT IGNORE INTO maestros_materias (maestro_id, materia_id) VALUES (%s, %s)"
        for id in materias:
            self.db_connection.execute_query(query, (maestro_id, id))
            
        query = f"""
            DELETE FROM asignaciones
            WHERE maestro_id = %s
            AND materia_id NOT IN ({materias_placeholder});
        """

        self.db_connection.execute_query(query, (maestro_id,))
        
        messagebox.showinfo("Éxito", "Maestro actualizado con éxito.")
        self.cancelar_maestro()
    
    def eliminar_maestro(self):
        maestro_id = self.entry_codigo.get()
        
        query = "DELETE FROM maestros WHERE maestro_id = %s"
        self.db_connection.execute_query(query, (maestro_id,))
        
        query = "DELETE FROM maestros_materias WHERE maestro_id = %s"
        self.db_connection.execute_query(query, (maestro_id,))

        self.lista_materias_seleccionadas = []

        messagebox.showinfo("Éxito", "Maestro eliminado con éxito.")
        self.cancelar_maestro()
    
    def cancelar_maestro(self):
        self.id_busqueda.delete(0, END)
        for entry in [self.entry_codigo,  self.entry_id, self.entry_nombre, self.entry_apellido_paterno, self.entry_apellido_materno, self.entry_correo, self.combo_grado_estudios, self.combo_carrera, self.combo_materia]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
            
        for item in self.tree_materias.get_children():
            self.tree_materias.delete(item)
            
        self.lista_materias_seleccionadas = []
            
        self.button_agregar_materia.config(state="disabled")
        self.button_quitar_materia.config(state="disabled")
        
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")


   