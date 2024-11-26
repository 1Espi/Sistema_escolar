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

        # Etiquetas para los días de la semana (lunes a sábado)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        for col, dia in enumerate(dias):
            label = tk.Label(self.frame_body, text=dia, bg="#FFFFFF", fg="#000000", 
                            font=("Arial", 10, "bold"), anchor="center")
            label.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

        # Configurar las columnas de la cuadrícula
        for col in range(6):
            self.frame_body.columnconfigure(col, weight=1)

        # Ajustar las filas para los cuadros Text debajo de las etiquetas
        self.fill_items(start_row=1)

    def fill_items(self, start_row=0):
        usuario_id = self.user_info['ID']  # ID del alumno logeado

        query = "SELECT alumno_id FROM alumnos WHERE usuario_id = %s;"
        result = self.db_connection.fetch_one(query, (usuario_id,))
        if not result:
            messagebox.showerror("Error", "No se encontró el ID del alumno.")
            return
        
        alumno_id = result[0]

        query = """
            SELECT g.nombre AS 'grupo', h.dia, h.hora_inicio, h.hora_fin, s.nombre AS 'salon', 
                u.nombre AS 'maestro', m.nombre AS 'materia'
            FROM inscripciones AS i
            INNER JOIN grupos AS g ON i.grupo_id = g.grupo_id
            INNER JOIN horarios AS h ON g.horario_id = h.horario_id
            INNER JOIN salones AS s ON g.salon_id = s.salon_id
            INNER JOIN asignaciones AS a ON g.asignacion_id = a.asignacion_id
            INNER JOIN maestros AS ma ON a.maestro_id = ma.maestro_id
            INNER JOIN usuarios AS u ON ma.usuario_id = u.usuario_id
            INNER JOIN materias AS m ON m.materia_id = a.materia_id
            WHERE i.alumno_id = %s
            ORDER BY FIELD(h.dia, 'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado'), h.hora_inicio;
        """
        result = self.db_connection.fetch_all(query, (alumno_id,))

        # Mapeo de días a columnas
        dia_a_columna = {
            "Lunes": 0,
            "Martes": 1,
            "Miercoles": 2,
            "Jueves": 3,
            "Viernes": 4,
            "Sabado": 5
        }

        filas_por_dia = [start_row] * 6  # Controla la fila actual por cada día (columna)
        
        if result:
            for registro in result:
                grupo, dia, hora_inicio, hora_fin, salon, maestro, materia = registro
                hora_inicio_str = str(hora_inicio)
                hora_fin_str = str(hora_fin)

                registro_formateado = (
                    f"Grupo: {grupo}\n"
                    f"Salón: {salon}\n"
                    f"Materia: {materia}\n"
                    f"Maestro: {maestro}\n"
                    f"Horario: {dia} {hora_inicio_str} - {hora_fin_str}"
                )

                # Determinar columna basada en el día
                columna = dia_a_columna.get(dia, -1)
                if columna == -1:
                    continue  # Ignorar si el día no está mapeado

                # Crear el Text y colocarlo en la interfaz
                text_area = tk.Text(self.frame_body, wrap="word", height=9, width=20)
                text_area.insert("1.0", registro_formateado)
                text_area.grid(row=filas_por_dia[columna], column=columna, sticky="nsew", padx=5, pady=5)

                text_area.bind("<Button-1>", self.on_click)

                # Incrementar la fila del día correspondiente
                filas_por_dia[columna] += 1


    def on_click(self, event):
        # Obtener el widget Text donde ocurrió el clic
        text_area = event.widget
        # Obtener el contenido completo del Text
        contenido = text_area.get("1.0", "end-1c")
        
        # Extraer el nombre del grupo del contenido
        linea_grupo = next((line for line in contenido.split("\n") if line.startswith("Grupo:")), None)
        if not linea_grupo:
            messagebox.showerror("Error", "No se pudo encontrar el nombre del grupo en el contenido.")
            return

        grupo_nombre = linea_grupo.replace("Grupo:", "").strip()

        # Consulta para obtener los IDs de los alumnos inscritos al grupo
        query_inscripciones = """
            SELECT a.usuario_id, u.nombre 
            FROM inscripciones AS i
            INNER JOIN alumnos AS a ON i.alumno_id = a.alumno_id
            INNER JOIN usuarios AS u ON a.usuario_id = u.usuario_id
            INNER JOIN grupos AS g ON i.grupo_id = g.grupo_id
            WHERE g.nombre = %s;
        """
        
        result = self.db_connection.fetch_all(query_inscripciones, (grupo_nombre,))
        
        if not result:
            messagebox.showinfo("Información", f"No hay alumnos inscritos en el grupo {grupo_nombre}.")
            return

        # Formatear los nombres de los alumnos
        alumnos = [f"{usuario_id}: {nombre}" for usuario_id, nombre in result]
        alumnos_str = "\n".join(alumnos)

        # Mostrar los nombres de los alumnos inscritos
        messagebox.showinfo(f"Alumnos inscritos en {grupo_nombre}", alumnos_str)
