import tkinter as tk
from tkinter import ttk, messagebox, END
import re
from utilities.connection import MySQLConnection  
class UsuariosFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info  # Información del usuario logueado
        self.db_connection = MySQLConnection()  # Crear instancia de la conexión a MySQL
        self.db_connection.connect()  # Conectar a la base de datos
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self, text="Usuarios", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self, text="Ingresar código de usuario:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = tk.Entry(self, state="normal")
        self.id_entry.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(self, text="Buscar", command=self.buscar_usuario).grid(row=1, column=2, padx=5)

        # Labels y Entries individuales
        tk.Label(self, text="ID:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_id = tk.Entry(self, state="disabled")
        self.entry_id.grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(self, text="Nombre:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_nombre = tk.Entry(self, state="disabled")
        self.entry_nombre.grid(row=3, column=1, sticky="w", padx=5)

        tk.Label(self, text="Apellido Paterno:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_apellido_paterno = tk.Entry(self, state="disabled")
        self.entry_apellido_paterno.grid(row=4, column=1, sticky="w", padx=5)

        tk.Label(self, text="Apellido Materno:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_apellido_materno = tk.Entry(self, state="disabled")
        self.entry_apellido_materno.grid(row=5, column=1, sticky="w", padx=5)

        tk.Label(self, text="Email:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_email = tk.Entry(self, state="disabled")
        self.entry_email.grid(row=6, column=1, sticky="w", padx=5)

        tk.Label(self, text="Password:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.entry_password = tk.Entry(self, show="*", state="disabled")
        self.entry_password.grid(row=7, column=1, sticky="w", padx=5)

        tk.Label(self, text="Perfil:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        self.entry_perfil = ttk.Combobox(self, values=["Administrador", "Maestro", "Alumno"], state="disabled")
        self.entry_perfil.grid(row=8, column=1, sticky="w", padx=5)

        # Configurar la expansión de las columnas en la fila de los botones
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)

        self.button_crear = tk.Button(self, text="Crear", command=self.Crear_Usuario)
        self.button_crear.grid(row=9, column=0, sticky="ew", padx=5)

        self.button_guardar = tk.Button(self, text="Guardar", command=self.guardar_usuario, state="disabled")
        self.button_guardar.grid(row=9, column=1, sticky="ew", padx=5)

        self.button_actualizar = tk.Button(self, text="Actualizar", command=self.actualizar_usuario, state="disabled")
        self.button_actualizar.grid(row=9, column=2, sticky="ew", padx=5)

        self.button_eliminar = tk.Button(self, text="Eliminar", command=self.eliminar_usuario, state="disabled")
        self.button_eliminar.grid(row=9, column=3, sticky="ew", padx=5)

        self.button_cancelar = tk.Button(self, text="Cancelar", command=self.limpiar_campos, state="disabled")
        self.button_cancelar.grid(row=9, column=4, sticky="ew", padx=5)



    def desbloquear_campos(self):
        self.entry_id.config(state="normal")
        self.entry_nombre.config(state="normal")
        self.entry_apellido_paterno.config(state="normal")
        self.entry_apellido_materno.config(state="normal")
        self.entry_email.config(state="normal")
        self.entry_password.config(state="normal")
        self.entry_perfil.config(state="readonly")
        
    def Crear_Usuario(self):
        self.entry_id.config(state="normal")
        self.entry_nombre.config(state="normal")
        self.entry_apellido_paterno.config(state="normal")
        self.entry_apellido_materno.config(state="normal")
        self.entry_email.config(state="normal")
        self.entry_password.config(state="normal")
        self.entry_perfil.config(state="readonly")
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="normal")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="normal")
        
        query = "SELECT MAX(usuario_id) FROM usuarios"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, max_id)
        self.entry_id.config(state="disabled")  

    def validar_password(self, password):
        return len(password) >= 6 and re.search(r"[A-Z]", password) and re.search(r"\d", password) and re.search(r"\W", password)

    def buscar_usuario(self):
        user_id = self.id_entry.get()
        if not user_id.isdigit():
            messagebox.showerror("Error", "ID de usuario inválido.")
            return

        query = "SELECT usuario_id, nombre, correo, contrasena, tipo FROM usuarios WHERE usuario_id = %s"
        result = self.db_connection.fetch_all(query, (user_id,))

        if result:
            self.desbloquear_campos()
            usuario = result[0]
            full_name = usuario[1].split()
            
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, usuario[0])
            self.entry_id.config(state="disabled")

            self.entry_nombre.delete(0, END)
            self.entry_nombre.insert(0, full_name[0] if len(full_name) > 0 else "")
            self.entry_apellido_paterno.delete(0, END)
            self.entry_apellido_paterno.insert(0, full_name[1] if len(full_name) > 1 else "")
            self.entry_apellido_materno.delete(0, END)
            self.entry_apellido_materno.insert(0, full_name[2] if len(full_name) > 2 else "")

            self.entry_email.delete(0, END)
            self.entry_email.insert(0, usuario[2])

            self.entry_password.delete(0, END)
            self.entry_password.insert(0, usuario[3])
            self.entry_perfil.set(usuario[4])
            self.button_crear.config(state="disabled")
            self.button_guardar.config(state="disabled")
            self.button_actualizar.config(state="normal")
            self.button_eliminar.config(state="normal")
            self.button_cancelar.config(state="normal")
        else:
            messagebox.showinfo("Información", "Usuario no encontrado.")

    def guardar_usuario(self):
        self.entry_id.config(state="normal")
        id=self.entry_id.get()
        nombre = self.entry_nombre.get()
        apellido_paterno = self.entry_apellido_paterno.get()
        apellido_materno = self.entry_apellido_materno.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        perfil = self.entry_perfil.get()

        if not (id and nombre and apellido_paterno and apellido_materno and email and password and perfil): 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return
        if '@' not in email: 
            messagebox.showerror("Error", "Por favor, ingresa un correo electrónico válido.") 
            return
        if not self.validar_password(password):
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres, incluir una mayúscula, un número y un símbolo.")
            return
        

        nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"
        query = "INSERT INTO usuarios (usuario_id, nombre, correo, contrasena, tipo) VALUES (%s, %s, %s, %s, %s)"
        self.db_connection.execute_query(query, (id, nombre_completo, email, password, perfil))
        
        messagebox.showinfo("Éxito", "Usuario creado con éxito.")
        self.limpiar_campos()


    def actualizar_usuario(self):
        user_id = self.id_entry.get()
        nombre = self.entry_nombre.get()
        apellido_paterno = self.entry_apellido_paterno.get()
        apellido_materno = self.entry_apellido_materno.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        perfil = self.entry_perfil.get()

        if not user_id.isdigit():
            messagebox.showerror("Error", "ID inválido")
            return
        if not (nombre and apellido_paterno and apellido_materno and email and password and perfil): 
            messagebox.showerror("Error", "Todos los campos deben estar llenos.") 
            return
        if '@' not in email: 
            messagebox.showerror("Error", "Por favor, ingresa un correo electrónico válido.") 
            return
        if not self.validar_password(password):
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres, incluir una mayúscula, un número y un símbolo.")
            return

        nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"
        query = "UPDATE usuarios SET nombre = %s, correo = %s, contrasena = %s, tipo = %s WHERE usuario_id = %s"
        self.db_connection.execute_query(query, (nombre_completo, email, password, perfil, user_id))
        
        messagebox.showinfo("Éxito", "Usuario actualizado con éxito.")
        self.limpiar_campos()


    def eliminar_usuario(self):
        user_id = self.id_entry.get()
        if not user_id.isdigit():
            messagebox.showerror("Error", "ID de usuario inválido.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este usuario?"):
            query = "DELETE FROM usuarios WHERE usuario_id = %s"
            self.db_connection.execute_query(query, (user_id,))
            messagebox.showinfo("Éxito", "Usuario eliminado con éxito.")
            self.limpiar_campos()


    def limpiar_campos(self):
        self.id_entry.delete(0, END)
        for entry in [self.entry_id, self.entry_nombre, self.entry_apellido_paterno, self.entry_apellido_materno, self.entry_email, self.entry_password]:
            entry.config(state="normal")
            entry.delete(0, END)
            entry.config(state="disabled")
        self.entry_perfil.set("")
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")

