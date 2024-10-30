import tkinter as tk
from tkinter import messagebox
from .usuarios import UsuariosFrame
from .alumnos import AlumnosFrame
from .maestros import MaestrosFrame
from .materias import MateriasFrame
from .grupos import GruposFrame
from .horarios import HorariosFrame
from .carreras import CarrerasFrame
from .planeacion import PlaneacionFrame

class Menu:
    def __init__(self, user_info):
        self.user_info = user_info
        self.current_frame = None  # Para almacenar el frame actual

    def open_main_menu(self):
        self.menu_window = tk.Tk()
        self.menu_window.title("Menú Principal")
        self.menu_window.minsize(500, 250)

        # Contenedor principal
        self.container = tk.Frame(self.menu_window)
        self.container.pack(fill="both", expand=True)

        # Frame para el menú
        self.menu_frame = tk.Frame(self.container)
        self.menu_frame.pack(side="top", fill="x")

        # Etiqueta de bienvenida
        self.welcome_label = tk.Label(self.container, text=f'Hola {self.user_info["NOMBRE"]}', font=("Arial", 16))
        self.welcome_label.pack(pady=20)
        
        self.unwrapping_menu = tk.Menu()
        self.menu_window.config(menu=self.unwrapping_menu)

        # Crear botones para el menú
        self.create_menu_buttons()

        self.menu_window.mainloop()

    def create_menu_buttons(self):
        # Diccionario de acciones según el perfil del usuario
        profile_actions = {
            "administrador": ["Usuarios", "Alumnos", "Maestros", "Materias", "Grupos", "Horarios", "Carreras", "Planeacion"],
            "maestro": ["Maestros", "Grupos"],
            "alumno": ["Alumnos", "Horarios", "Planeacion"]
        }

        # Obtener las acciones permitidas según el perfil del usuario
        actions = profile_actions.get(self.user_info["TIPO"].lower())

        if actions:
            opciones_menu = tk.Menu(self.unwrapping_menu, tearoff=0)
            
            acc = 1
            for action in actions:
                opciones_menu.add_command(label=action, command=lambda a=action: self.handle_menu_action(a))
                acc+=1
            
            opciones_menu.add_separator()
            opciones_menu.add_command(label="Cerrar Sesión", command=lambda: self.handle_menu_action("Cerrar Sesion"))
            
            self.unwrapping_menu.add_cascade(label="Opciones", menu=opciones_menu)
        else:
            messagebox.showerror("Error", "Perfil de usuario no reconocido")
            self.menu_window.destroy()

    def handle_menu_action(self, action):
        if self.current_frame:
            self.current_frame.destroy()  # Eliminar el frame actual
        
        self.welcome_label.forget()

        if action == "Cerrar Sesion":
            self.menu_window.destroy()
            from .login import Login
            Login()
            return

        # Inicializa el frame correspondiente
        frame_class = {
            "Usuarios": UsuariosFrame, 
            "Alumnos": AlumnosFrame, 
            "Maestros": MaestrosFrame, 
            "Materias": MateriasFrame, 
            "Grupos": GruposFrame, 
            "Horarios": HorariosFrame, 
            "Carreras": CarrerasFrame, 
            "Planeacion": PlaneacionFrame
        }.get(action)
        
        if frame_class:
            self.current_frame = frame_class(self, self.container)
            self.current_frame.pack(fill="both", expand=True)  # Mostrar el nuevo frame

        