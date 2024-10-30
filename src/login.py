import tkinter as tk
from tkinter import messagebox, ttk
import utilities.connection as connfile
from .menu import Menu

class Login:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Inicio de sesión")
        self.root.minsize(270, 170)

        frame = tk.Frame(self.root)
        frame.pack(pady=20, padx=20)

        tk.Label(frame, text="Correo:").grid(row=0, column=0, pady=5)
        self.entry_email = tk.Entry(frame)
        self.entry_email.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=5)
        self.entry_password = tk.Entry(frame, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)

        tk.Button(self.root, text="Acceder", command=self.login).pack(pady=10)

        # Variable para almacenar el perfil del usuario
        self.user_info = {}
        self.root.mainloop()

    def login(self):
        email = self.entry_email.get()
        input_password = self.entry_password.get()

        try:
            db = connfile.MySQLConnection()
            db.connect()

            # Obtener el usuario correspondiente al correo
            users = db.fetch_all("SELECT usuario_id, nombre, correo, tipo, contrasena FROM usuarios WHERE correo = %s", (email,))
            
            # Verificar si se encontró un usuario
            if users:
                user = users[0]  # Extraer el primer usuario encontrado
                stored_password = user[4]  # Índice 4 corresponde a la contraseña en la tupla
                
                # Verificar la contraseña
                if input_password == stored_password:
                    # Guardar la información del usuario
                    self.user_info['ID'] = user[0]
                    self.user_info['NOMBRE'] = user[1]
                    self.user_info['CORREO'] = user[2]
                    self.user_info['TIPO'] = user[3]
                    
                    # Cerrar la ventana de inicio de sesión
                    self.root.destroy()
                    
                    menu = Menu(self.user_info)
                    menu.open_main_menu()
                else:
                    messagebox.showerror("Error", "Contraseña incorrecta")
            else:
                messagebox.showerror("Error", "Usuario no encontrado")

            db.close_connection()

        except Exception as e:
            messagebox.showerror("Error de conexión", f"Ocurrió un error al iniciar sesión\n{e}")
