import tkinter as tk
import string
import utilities.connection as connfile
from tkinter import END, messagebox, ttk
from utilities.connection import MySQLConnection

class SalonesFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        self.alfabeto = list(string.ascii_uppercase) 
        self.setup_ui()

    def setup_ui(self):
        # Título
        title = tk.Label(self, text="Salones", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        # Etiquetas y Entrys
        tk.Label(self, text="Ingrese código salón:").grid(row=1, column=0, padx=5, sticky="e")
        self.entry_codigo = tk.Entry(self)
        self.entry_codigo.grid(row=1, column=1, padx=5, pady=5)

        self.button_buscar = tk.Button(self, text="Buscar",command=self.buscar_salon)
        self.button_buscar.grid(row=1, column=2, padx=5)

        tk.Label(self, text="ID:").grid(row=2, column=0, padx=5, sticky="e")
        self.entry_id = tk.Entry(self, state="disabled")
        self.entry_id.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="Nombre salón:").grid(row=3, column=0, padx=5, sticky="e")
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self, text="Edificio:").grid(row=4, column=0, padx=5, sticky="e")
        self.combobox_edificio = ttk.Combobox(self, state="readonly",values=self.alfabeto)
        self.combobox_edificio.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self, text="Capacidad:").grid(row=5, column=0, padx=5, sticky="e")
        self.entry_capacidad = tk.Entry(self)
        self.entry_capacidad.grid(row=5, column=1, padx=5, pady=5)

        # Botones
        self.frame_botones = tk.Frame(self)
        self.frame_botones.grid(row=6, column=0, columnspan=3, pady=10)

        self.button_nuevo = tk.Button(self.frame_botones, text="Nuevo",command=self.nuevo_salon)
        self.button_nuevo.grid(row=0, column=0, padx=5)

        self.button_guardar = tk.Button(self.frame_botones, text="Guardar", state="disabled", command=self.guardar_salon)
        self.button_guardar.grid(row=0, column=1, padx=5)

        self.button_cancelar = tk.Button(self.frame_botones, text="Cancelar", state="disabled",command=self.cancelar_accion)
        self.button_cancelar.grid(row=0, column=2, padx=5)

        self.button_editar = tk.Button(self.frame_botones, text="Editar", state="disabled",command=self.actualizar_salon)
        self.button_editar.grid(row=0, column=3, padx=5)

        self.button_baja = tk.Button(self.frame_botones, text="Baja", state="disabled",command=self.eliminar_salon)
        self.button_baja.grid(row=0, column=4, padx=5)

    def nuevo_salon(self):
        """Configura el formulario para crear un nuevo salón, mostrando el próximo ID disponible."""
        try:
            # Consulta el último ID registrado en la tabla de salones
            query = "SELECT MAX(salon_id) FROM salones"
            resultado = self.db_connection.fetch_all(query)
            next_id = (resultado[0][0] or 0) + 1  # Si no hay registros, comienza con 1

            # Mostrar el próximo ID en el campo de texto
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, next_id)
            self.entry_id.config(state="disabled")

                # Limpiar otros campos y habilitar para ingreso de datos
            self.limpiar_campos()
            self.habilitar_campos(True)

            # Cambiar el estado de los botones
            self.button_guardar.config(state="normal")
            self.button_cancelar.config(state="normal")
            self.button_nuevo.config(state="disabled")
            self.button_buscar.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo calcular el próximo ID: {e}")


    
    def limpiar_campos(self):
        self.entry_codigo.delete(0, END)
        self.entry_nombre.delete(0, END)
        self.combobox_edificio.set("")
        self.entry_capacidad.delete(0, END)

    
    def habilitar_campos(self, habilitar):
        state = "normal" if habilitar else "disabled"
        self.entry_codigo.config(state=state)
        self.entry_nombre.config(state=state)
        self.combobox_edificio.config(state="readonly" if habilitar else "disabled")
        self.entry_capacidad.config(state=state)


    
    def guardar_salon(self):
        """Guarda un nuevo salón en la base de datos."""
        nombre = self.entry_nombre.get().strip()
        edificio = self.combobox_edificio.get()
        capacidad = self.entry_capacidad.get().strip()

        # Validaciones de entrada
        if not nombre:
            messagebox.showerror("Error", "El nombre del salón es obligatorio.")
            return

        if not nombre.isdigit():
            messagebox.showerror("Error", "El nombre del salón debe ser un número.")
            return

        if not edificio:
            messagebox.showerror("Error", "Seleccione un edificio.")
            return

        if not capacidad:
            messagebox.showerror("Error", "La capacidad del salón es obligatoria.")
            return

        if not capacidad.isdigit() or int(capacidad) <= 0:
            messagebox.showerror("Error", "La capacidad debe ser un número entero positivo.")
            return

        # Crear el nombre completo del salón
        nombre_salon = f"{edificio}-{nombre}"

        # Validación de nombre único
        query_check = "SELECT COUNT(*) FROM salones WHERE nombre = %s"
        resultado_check = self.db_connection.fetch_all(query_check, (nombre_salon,))

        if resultado_check[0][0] > 0:
            messagebox.showerror("Error", "Ya existe un salón con ese nombre.")
            return

        # Insertar el salón en la base de datos
        query_insert = "INSERT INTO salones (nombre, capacidad) VALUES (%s, %s)"
        try:
            self.db_connection.execute_query(query_insert, (nombre_salon, capacidad))
            messagebox.showinfo("Éxito", "Salón creado con éxito.")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el salón: {e}")
    
    def actualizar_salon(self):
        """Actualiza la información de un salón en la base de datos."""
        nombre = self.entry_nombre.get().strip()
        edificio = self.combobox_edificio.get()
        capacidad = self.entry_capacidad.get().strip()
        salon_id = self.entry_codigo.get().strip()

        # Validaciones de entrada
        if not nombre:
            messagebox.showerror("Error", "El nombre del salón es obligatorio.")
            return

        if not nombre.isdigit():
            messagebox.showerror("Error", "El nombre del salón debe ser un número.")
            return

        if not edificio:
            messagebox.showerror("Error", "Seleccione un edificio.")
            return

        if not capacidad:
            messagebox.showerror("Error", "La capacidad del salón es obligatoria.")
            return

        if not capacidad.isdigit() or int(capacidad) <= 0:
            messagebox.showerror("Error", "La capacidad debe ser un número entero positivo.")
            return

        # Crear el nombre completo del salón
        nombre_salon = f"{edificio}-{nombre}"

        # Validación de nombre único (si el salón no es el mismo que el actual)
        query_check = "SELECT COUNT(*) FROM salones WHERE nombre = %s AND salon_id != %s"
        resultado_check = self.db_connection.fetch_all(query_check, (nombre_salon, salon_id))

        if resultado_check[0][0] > 0:
            messagebox.showerror("Error", "Ya existe un salón con ese nombre.")
            return

        # Actualizar el salón en la base de datos
        query_update = "UPDATE salones SET nombre = %s, capacidad = %s WHERE salon_id = %s"
        try:
            self.db_connection.execute_query(query_update, (nombre_salon, capacidad, salon_id))
            messagebox.showinfo("Éxito", "Salón actualizado con éxito.")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el salón: {e}")
    
    def buscar_salon(self):
        """Busca un salón por su código y carga la información en los campos correspondientes."""
        codigo = self.entry_codigo.get().strip()

        # Validación del código del salón
        if not codigo:
            messagebox.showerror("Error", "Ingrese el código del salón.")
            return

        # Consulta para obtener los detalles del salón
        query = "SELECT salon_id, nombre, capacidad FROM salones WHERE salon_id = %s"
        resultado = self.db_connection.fetch_all(query, (codigo,))

        if resultado:
            salon_id, nombre, capacidad = resultado[0]

            # Separar el edificio (primera palabra) y el nombre (el resto)
            edificio = nombre[0]  # Primer parte es el edificio
            nombre_salon = nombre[2:]  # El resto es el nombre del salón

            # Llenar los campos con los datos obtenidos
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, salon_id)
            self.entry_id.config(state="disabled")

            self.entry_nombre.delete(0, END)
            self.entry_nombre.insert(0, nombre_salon)

            self.combobox_edificio.set(edificio)

            self.entry_capacidad.delete(0, END)
            self.entry_capacidad.insert(0, capacidad)


                # Cambiar el estado de los botones
            self.button_buscar.config(state="disabled")
            self.button_guardar.config(state="disabled")
            self.button_nuevo.config(state="disabled")
            self.button_editar.config(state="normal")
            self.button_cancelar.config(state="normal")
            self.button_baja.config(state="normal")

        else:
            messagebox.showerror("Error", "No se encontró un salón con ese código.")

    def eliminar_salon(self):
        """Elimina un salón de la base de datos después de confirmar con el usuario."""
        salon_id = self.entry_id.get().strip()

        # Validar si se ha encontrado un salón
        if not salon_id:
            messagebox.showerror("Error", "No se ha encontrado un salón para eliminar.")
            return

        # Confirmación de eliminación
        confirmar = messagebox.askyesno("Confirmación", "¿Está seguro de que desea eliminar este salón? Esta acción no se puede deshacer.")
        if not confirmar:
            return  # Si el usuario cancela, no se hace nada

        try:
            # Consulta para eliminar el salón de la base de datos
            query = "DELETE FROM salones WHERE salon_id = %s"
            self.db_connection.execute_query(query, (salon_id,))

            # Mensaje de éxito
            messagebox.showinfo("Éxito", "El salón ha sido eliminado exitosamente.")

            # Limpiar los campos y restablecer la interfaz
            self.limpiar_campos()
            self.cancelar_accion()  # Volver al estado inicial

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el salón: {e}")



    def cancelar_accion(self):
        """Cancela la acción actual y vuelve al estado inicial."""
        # Limpiar campos
        self.limpiar_campos()

        # Cambiar el estado de los botones
        self.button_nuevo.config(state="normal")
        self.button_buscar.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_cancelar.config(state="disabled")
        self.button_editar.config(state="disabled")
        self.button_baja.config(state="disabled")
