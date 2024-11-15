import tkinter as tk
import utilities.connection as connfile
from tkinter import END, messagebox, ttk
from datetime import timedelta
from utilities.connection import MySQLConnection 

class PlaneacionFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.db_connection = MySQLConnection()
        self.db_connection.connect()

        self.setup_ui()

    def setup_ui(self):

        # Canvas y scrollbar configurados con el tamaño inicial
        canvas = tk.Canvas(self, width=1050, bg='#FFFFFF')
        canvas.pack(side="left", fill="both", expand=True)
    
        # Barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configurar el canvas para que responda a la barra de scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Frame Body que contendrá los Text y estará dentro del canvas
        self.frame_body = tk.Frame(canvas, bd=0, relief=tk.SOLID, padx=0, pady=10, bg='#FFFFFF')
        canvas.create_window((0, 0), window=self.frame_body, anchor="nw")

        for col in range(6):
            self.frame_body.columnconfigure(col, weight=1)

        self.fill_items()

    def fill_items(self):
        query = """SELECT g.nombre AS 'grupo', h.dia, h.hora_inicio, hora_fin, s.nombre AS 'salon', 
                          u.nombre AS 'maestro', m.nombre AS 'materia' 
                   FROM grupos AS g 
                   INNER JOIN horarios AS h ON g.horario_id = h.horario_id 
                   INNER JOIN salones AS s ON g.salon_id = s.salon_id
                   INNER JOIN asignaciones AS a ON g.asignacion_id = a.asignacion_id
                   INNER JOIN maestros AS ma ON a.maestro_id = ma.maestro_id
                   INNER JOIN usuarios AS u ON ma.usuario_id = u.usuario_id
                   INNER JOIN materias AS m ON m.materia_id = a.materia_id;"""
        result = self.db_connection.fetch_all(query, ())
        index = 0
        fila = 0

        if result:
            for registro in result:
                if index == 6:
                    fila += 1
                    index = 0
                    self.frame_body.rowconfigure(fila, weight=1)

                grupo, dia, hora_inicio, hora_fin, salon, maestro, materia = registro
                hora_inicio_str = str(timedelta(seconds=hora_inicio.seconds))
                hora_fin_str = str(timedelta(seconds=hora_fin.seconds))

                registro_formateado = (
                    f"Grupo: {grupo}\n"
                    f"Salón: {salon}\n"
                    f"Materia: {materia}\n"
                    f"Maestro: {maestro}\n"
                    f"Horario: {dia} {hora_inicio_str} - {hora_fin_str}"
                )

                text_area = tk.Text(self.frame_body, wrap="word", height=9, width=20)
                text_area.insert("1.0", registro_formateado)
                text_area.grid(row=fila, column=index, sticky="nsew", padx=5, pady=5)
                
                text_area.bind("<Button-1>", self.on_click)

                index += 1

    def on_click(self, event):
        # Obtener el widget Text donde ocurrió el clic
        text_area = event.widget
        # Obtener el contenido completo del Text
        contenido = text_area.get("1.0", "end-1c")
        print(f"Contenido del Text clickeado:\n{contenido}")
