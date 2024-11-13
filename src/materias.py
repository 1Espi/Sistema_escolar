import tkinter as tk
import utilities.connection as connfile
from tkinter import END, messagebox, ttk
from utilities.connection import MySQLConnection


class MateriasFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        self.carreras = []
        # Cargar carreras y verificar si hay alguna
        if not self.cargar_carreras():
            messagebox.showerror("Error", "No se encontraron carreras. Agrega una carrera antes de gestionar materias.")
            self.destroy()  # Cierra el frame actual
            return

        self.setup_ui()

    def cargar_carreras(self):
            """Carga las carreras desde la base de datos y las almacena en la lista de carreras."""
            query = "SELECT carrera_id, nombre FROM carreras"
            try:
                resultados = self.db_connection.fetch_all(query)
                if resultados:
                    self.carreras = {f"{nombre} (ID: {carrera_id})": carrera_id for carrera_id, nombre in resultados}
                    return True
                else:
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las carreras: {e}")
                return False

    def setup_ui(self):
        title = tk.Label(self, text="Materias", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        # Campo ID de Materia
        tk.Label(self, text="ID de Materia:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_id = tk.Entry(self)
        self.entry_id.grid(row=1, column=1, sticky="w", padx=5)

        # Campo Nombre de la Materia
        tk.Label(self, text="Nombre:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.grid(row=2, column=1, sticky="w", padx=5)

        # Campo Descripción
        tk.Label(self, text="Descripción:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_descripcion = tk.Text(self, height=4, width=30)
        self.entry_descripcion.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        # Combobox para Carrera
        tk.Label(self, text="Carrera:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.combo_carrera = ttk.Combobox(self, state="readonly",values=list(self.carreras.keys()))  # Actualizar con datos reales
        self.combo_carrera.grid(row=4, column=1, sticky="w", padx=5)
        
        tk.Label(self, text="Semestre:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_semestre = tk.Entry(self)
        self.entry_semestre.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky='w')
        
        tk.Label(self, text="Creditos:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_creditos = tk.Entry(self)
        self.entry_creditos.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        # Botones
        self.button_crear = tk.Button(self, text="Crear", command=self.crear_materia)
        self.button_crear.grid(row=7, column=0, sticky="ew", padx=5)

        self.button_guardar = tk.Button(self, text="Guardar", command=self.guardar_materia, state="disabled")
        self.button_guardar.grid(row=7, column=1, sticky="ew", padx=5)

        self.button_actualizar = tk.Button(self, text="Actualizar",command=self.actualizar_materia, state="disabled")
        self.button_actualizar.grid(row=7, column=2, sticky="ew", padx=5)

        self.button_eliminar = tk.Button(self, text="Eliminar",command=self.eliminar_materia, state="disabled")
        self.button_eliminar.grid(row=7, column=3, sticky="ew", padx=5)

        self.button_cancelar = tk.Button(self, text="Cancelar",command=self.limpiar_campos, state="disabled")
        self.button_cancelar.grid(row=8, column=0, columnspan=4, sticky="ew", padx=5, pady=5)

        self.button_buscar = tk.Button(self, text="Buscar",command=self.buscar_materia_event)
        self.button_buscar.grid(row=7, column=4, rowspan=2, sticky="ew", padx=5, pady=5)

    def desbloquear_campos(self, desbloquear=True):
        """Habilita o deshabilita los campos de entrada."""
        estado = "readonly" if desbloquear else "disabled"
        self.entry_nombre.config(state="normal" if desbloquear else "disabled")
        self.entry_descripcion.config(state="normal" if desbloquear else "disabled")
        self.combo_carrera.config(state=estado)

    def crear_materia(self):
            """Prepara la interfaz para crear una nueva materia."""
            self.desbloquear_campos(True)
            self.button_guardar.config(state="normal")
            self.button_cancelar.config(state="normal")
            self.button_crear.config(state="disabled")
            self.button_buscar.config(state="disabled")
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, "Auto")  # Indica que el ID se generará automáticamente
            self.entry_id.config(state="disabled")
            self.entry_nombre.delete(0, END)
            self.entry_descripcion.delete('1.0', END)
            self.combo_carrera.set("")
            self.entry_semestre.delete(0, END)
            self.entry_creditos.delete(0, END)

    def guardar_materia(self):
        """Guarda una nueva materia en la base de datos."""
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get('1.0', END).strip()
        carrera_seleccionada = self.combo_carrera.get()
        semestre = self.entry_semestre.get()
        creditos = self.entry_creditos.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre de la materia es obligatorio.")
            return

        if not descripcion:
            messagebox.showerror("Error", "La descripción de la materia es obligatoria.")
            return

        if not carrera_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una carrera.")
            return
        
        if not semestre: 
            messagebox.showerror("Error", "Debe indicar un semestre.")
            return
        
        if not creditos: 
            messagebox.showerror("Error", "Debe indicar los creditos.")
            return
        
        if not creditos.isdigit():
            messagebox.showerror("Error", "Los creditos deben de ser un entero.")
            return

                # Validación de nombre único de materia
        query_check = "SELECT COUNT(*) FROM materias WHERE nombre = %s"
        resultado_check = self.db_connection.fetch_all(query_check, (nombre,))

        # Acceder al primer valor de la primera tupla (resultado_check[0][0])
        if resultado_check[0][0] > 0:
            messagebox.showerror("Error", "Ya existe una materia con ese nombre.")
            return


        carrera_id = self.carreras.get(carrera_seleccionada, None)

        query = "INSERT INTO materias (nombre, descripcion, carrera_id, semestre, creditos) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.db_connection.execute_query(query, (nombre, descripcion if descripcion else None, carrera_id, semestre, creditos))
            messagebox.showinfo("Éxito", "Materia creada con éxito.")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la materia: {e}")
    
    def buscar_materia_event(self):
        """Método auxiliar para capturar el evento de búsqueda, por ejemplo, al presionar Enter."""
        materia_id = self.entry_id.get()
        if materia_id.isdigit():
            self.buscar_materia(materia_id)
        else:
            messagebox.showerror("Error", "ID de materia inválido.")

    def buscar_materia(self, materia_id):
        """Busca una materia por su ID y carga sus datos en la interfaz."""
        query = "SELECT materia_id, nombre, descripcion, carrera_id, semestre, creditos FROM materias WHERE materia_id = %s"
        try:
            resultado = self.db_connection.fetch_all(query, (materia_id,))
            if resultado:
                self.desbloquear_campos(True)
                materia = resultado[0]
                self.entry_id.config(state="normal")
                self.entry_id.delete(0, END)
                self.entry_id.insert(0, materia[0])
                self.entry_id.config(state="disabled")

                self.entry_nombre.delete(0, END)
                self.entry_nombre.insert(0, materia[1])
                

                self.entry_descripcion.delete('1.0', END)
                if materia[2]:
                    self.entry_descripcion.insert('1.0', materia[2])

                # Buscar el nombre de la carrera correspondiente
                carrera_nombre = next((nombre for nombre, id_ in self.carreras.items() if id_ == materia[3]), "")

                # Verificar si se encuentra el nombre de la carrera
                if carrera_nombre:
                    self.combo_carrera.set(carrera_nombre)
                else:
                    # Si no se encuentra, mostrar un mensaje de error o manejarlo
                    messagebox.showerror("Error", "Carrera no encontrada para la materia.")
                    
                self.entry_semestre.delete(0, END)    
                self.entry_semestre.insert(0, materia[4])
                
                self.entry_creditos.delete(0, END)    
                self.entry_creditos.insert(0, materia[5])
                
                self.button_actualizar.config(state="normal")
                self.button_eliminar.config(state="normal")
                self.button_cancelar.config(state="normal")
                self.button_crear.config(state="disabled")
            else:
                messagebox.showinfo("Información", "Materia no encontrada.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar la materia: {e}")

    
    
    def actualizar_materia(self):
        """Actualiza los datos de una materia existente en la base de datos."""
        materia_id = self.entry_id.get()
        nombre = self.entry_nombre.get().strip()
        descripcion = self.entry_descripcion.get('1.0', END).strip()
        carrera_seleccionada = self.combo_carrera.get()
        semestre = self.entry_semestre.get()
        creditos = self.entry_creditos.get()

        if not materia_id:
            messagebox.showerror("Error", "No se ha cargado ninguna materia para actualizar.")
            return

        if not nombre:
            messagebox.showerror("Error", "El nombre de la materia es obligatorio.")
            return

        if not descripcion:
            messagebox.showerror("Error", "La descripción de la materia es obligatoria.")
            return

        if not carrera_seleccionada:
            messagebox.showerror("Error", "Debe seleccionar una carrera.")
            return
        
        if not semestre:
            messagebox.showerror("Error", "Debe especificar un semestre.")
            return
        
        if not creditos:
            messagebox.showerror("Error", "Debe asignar creditos.")
            return
        
        if not creditos.isdigit():
            messagebox.showerror("Error", "Los creditos deben de ser un entero.")
            return
        
        # Verificación de que no haya una materia con el mismo nombre
        query_check = "SELECT COUNT(*) FROM materias WHERE nombre = %s AND materia_id != %s"
        resultado_check = self.db_connection.fetch_all(query_check, (nombre, materia_id))

        # Acceder al primer valor de la primera tupla (resultado_check[0][0])
        if resultado_check[0][0] > 0:
            messagebox.showerror("Error", "Ya existe una materia con ese nombre.")
            return


        carrera_id = self.carreras.get(carrera_seleccionada, None)

        query = "UPDATE materias SET nombre = %s, descripcion = %s, carrera_id = %s, semestre = %s, creditos = %s WHERE materia_id = %s"
        try:
            self.db_connection.execute_query(query, (nombre, descripcion if descripcion else None, carrera_id, semestre, creditos, materia_id))
            messagebox.showinfo("Éxito", "Materia actualizada con éxito.")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la materia: {e}")


    def eliminar_materia(self):
        """Elimina una materia de la base de datos."""
        materia_id = self.entry_id.get()
        if not materia_id:
            messagebox.showerror("Error", "No se ha cargado ninguna materia para eliminar.")
            return

        confirmacion = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta materia?")
        if not confirmacion:
            return

        query = "DELETE FROM materias WHERE materia_id = %s"
        try:
            self.db_connection.execute_query(query, (materia_id,))
            messagebox.showinfo("Éxito", "Materia eliminada con éxito.")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la materia: {e}")

    def limpiar_campos(self):
        """Limpia todos los campos de la interfaz y restablece los botones."""
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, END)

        self.entry_nombre.delete(0, END)
        self.entry_descripcion.delete('1.0', END)
        self.combo_carrera.set("")
        self.entry_semestre.delete(0, END)
        self.entry_creditos.delete(0, END)

        self.desbloquear_campos(False)

        self.button_crear.config(state="normal")
        self.button_buscar.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")