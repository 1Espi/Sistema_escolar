import tkinter as tk
from tkinter import ttk, messagebox, END
from utilities.connection import MySQLConnection
import re

class GruposFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        self.setup_ui()
        self.cargar_materias()
        self.cargar_maestros()
        self.cargar_salones()
        self.cargar_horarios()

    def setup_ui(self):
        title = tk.Label(self, text="Gestión de Grupos", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self, text="Buscar ID de Grupo:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.search_entry = tk.Entry(self)
        self.search_entry.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(self, text="Buscar", command=self.buscar_grupo).grid(row=1, column=2, padx=5)
        
        tk.Label(self, text="ID del Grupo:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_id = tk.Entry(self, state="disabled")
        self.entry_id.grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(self, text="Nombre del Grupo:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.grid(row=3, column=1, sticky="w", padx=5)

        tk.Label(self, text="Materia:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.combo_materia = ttk.Combobox(self, state="readonly")
        self.combo_materia.grid(row=4, column=1, sticky="w", padx=5)
        self.combo_materia.bind("<<ComboboxSelected>>", self.on_materia_select)


        tk.Label(self, text="Carrera:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_carrera = tk.Entry(self, state="disabled")
        self.entry_carrera.grid(row=5, column=1, sticky="w", padx=5)

        tk.Label(self, text="Semestre:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_semestre = tk.Entry(self, state="disabled")
        self.entry_semestre.grid(row=6, column=1, sticky="w", padx=5)

        tk.Label(self, text="Maestro:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.combo_maestro = ttk.Combobox(self, state="readonly")
        self.combo_maestro.grid(row=7, column=1, sticky="w", padx=5)
        self.combo_maestro.bind("<<ComboboxSelected>>", self.on_maestro_select)


        tk.Label(self, text="Salón:").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        self.combo_salon = ttk.Combobox(self, state="readonly")
        self.combo_salon.grid(row=8, column=1, sticky="w", padx=5)
        self.combo_salon.bind("<<ComboboxSelected>>", self.cargar_capacidad_salon)

        tk.Label(self, text="Horario:").grid(row=9, column=0, sticky="e", padx=5, pady=5)
        self.combo_horario = ttk.Combobox(self, state="readonly")
        self.combo_horario.grid(row=9, column=1, sticky="w", padx=5)

        tk.Label(self, text="Máx. Número de Alumnos:").grid(row=10, column=0, sticky="e", padx=5, pady=5)
        self.entry_max_alumnos = tk.Entry(self, state="disabled")
        self.entry_max_alumnos.grid(row=10, column=1, sticky="w", padx=5)

        self.button_crear = tk.Button(self, text="Crear", command=self.crear_grupo)
        self.button_crear.grid(row=11, column=0, sticky="ew", padx=5)

        self.button_guardar = tk.Button(self, text="Guardar", command=self.guardar_grupo, state="disabled")
        self.button_guardar.grid(row=11, column=1, sticky="ew", padx=5)

        self.button_actualizar = tk.Button(self, text="Actualizar", command=self.actualizar_grupo, state="disabled")
        self.button_actualizar.grid(row=11, column=2, sticky="ew", padx=5)

        self.button_eliminar = tk.Button(self, text="Eliminar", command=self.eliminar_grupo, state="disabled")
        self.button_eliminar.grid(row=11, column=3, sticky="ew", padx=5)
        
        self.button_cancelar = tk.Button(self, text="Cancelar", command=self.limpiar_campos, state="disabled")
        self.button_cancelar.grid(row=11, column=4, sticky="ew", padx=5)

    def cargar_materias(self):
        query = "SELECT nombre FROM materias"
        result = self.db_connection.fetch_all(query)

        if result:
            self.combo_materia['values'] = [row[0] for row in result]
        else:
            self.combo_materia['values'] = []

    def cargar_maestros(self, materia_id=None):
        if materia_id:
            query = """
                SELECT m.maestro_id, u.nombre
                FROM maestros m
                JOIN usuarios u ON m.usuario_id = u.usuario_id
                JOIN maestros_materias mm ON mm.maestro_id = m.maestro_id
                WHERE mm.materia_id = %s AND u.tipo = 'Maestro';
            """
            result = self.db_connection.fetch_all(query, (materia_id,))
        else:
            result = []

        if result:
            self.combo_maestro['values'] = [row[1] for row in result]
            self.maestros = {row[1]: row[0] for row in result}  # Diccionario maestro_nombre -> maestro_id
        else:
            self.combo_maestro['values'] = []
            self.maestros = {}

    def on_materia_select(self, event):
        materia_nombre = self.combo_materia.get()

        query = "SELECT materia_id FROM materias WHERE nombre = %s;"
        result = self.db_connection.fetch_all(query, (materia_nombre,))
        if result:
            self.combo_maestro.set("")

            materia_id = result[0][0]

            self.cargar_maestros(materia_id)

            self.cargar_datos_carrera_semestre(materia_nombre)
        else:
            self.cargar_maestros()
            self.entry_carrera.config(state="normal")
            self.entry_carrera.delete(0, END)
            self.entry_carrera.config(state="disabled")
            self.entry_semestre.config(state="normal")
            self.entry_semestre.delete(0, END)
            self.entry_semestre.config(state="disabled")

    # lógica de filtrar materias al seleccionar un maestro
    def on_maestro_select(self, event):
        # maestro_nombre = self.combo_maestro.get()
        # maestro_id = self.maestros.get(maestro_nombre)
        # if maestro_id:
        #     self.cargar_materias(maestro_id)
        # else:
        #     self.cargar_materias()
        pass  # No se realiza ninguna acción al seleccionar un maestro


    def cargar_salones(self):
        query = "SELECT nombre FROM salones"
        result = self.db_connection.fetch_all(query)
        if result:
            self.combo_salon['values'] = [row[0] for row in result]

    def cargar_horarios(self):
        query = "SELECT dia, hora_inicio, hora_fin FROM horarios"
        result = self.db_connection.fetch_all(query)
        if result:
            self.combo_horario['values'] = [f"{row[0]} - {row[1]} - {row[2]}" for row in result]

    def cargar_datos_carrera_semestre(self, materia_nombre):
        query = """
            SELECT c.nombre, m.semestre 
            FROM materias m 
            JOIN carreras c ON m.carrera_id = c.carrera_id 
            WHERE m.nombre = %s
        """
        result = self.db_connection.fetch_all(query, (materia_nombre,))
        if result:
            carrera, semestre = result[0]
        else:
            carrera, semestre = "", ""

        self.entry_carrera.config(state="normal")
        self.entry_carrera.delete(0, END)
        self.entry_carrera.insert(0, carrera)
        self.entry_carrera.config(state="disabled")
        
        self.entry_semestre.config(state="normal")
        self.entry_semestre.delete(0, END)
        self.entry_semestre.insert(0, semestre)
        self.entry_semestre.config(state="disabled")


    def cargar_capacidad_salon(self, event):
        salon = self.combo_salon.get()
        query = "SELECT capacidad FROM salones WHERE nombre = %s"
        result = self.db_connection.fetch_all(query, (salon,))
        if result:
            capacidad = result[0][0]
            self.entry_max_alumnos.config(state="normal")
            self.entry_max_alumnos.delete(0, END)
            self.entry_max_alumnos.insert(0, capacidad)
            self.entry_max_alumnos.config(state="disabled")
            
    def crear_grupo(self):
        self.button_guardar.config(state="normal")
        self.button_crear.config(state="disabled")
        query = "SELECT MAX(grupo_id) FROM grupos"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_id.config(state="normal")
        self.entry_id.insert(0, max_id)
        self.entry_id.config(state="disabled")

    def guardar_grupo(self):
        try:
            grupo_id = self.entry_id.get()
            nombre_grupo = self.entry_nombre.get()
            materia_nombre = self.combo_materia.get()
            maestro_nombre = self.combo_maestro.get()
            salon_nombre = self.combo_salon.get()
            horario_info = self.combo_horario.get()

            if not (grupo_id and nombre_grupo and materia_nombre and maestro_nombre and salon_nombre and horario_info):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return
            
            if not re.fullmatch(r"D\d{2}", nombre_grupo):
                messagebox.showerror("Error", "El nombre del grupo debe tener el formato 'DXX', donde XX son dos dígitos.")
                return

            query_materia = "SELECT materia_id FROM materias WHERE nombre = %s"
            materia_id = self.db_connection.fetch_all(query_materia, (materia_nombre,))
            query_maestro = """
                SELECT m.maestro_id 
                FROM maestros m 
                JOIN usuarios u ON m.usuario_id = u.usuario_id 
                WHERE u.nombre = %s
            """
            maestro_id = self.db_connection.fetch_all(query_maestro, (maestro_nombre,))

            if not materia_id or not maestro_id:
                messagebox.showerror("Error", "Error al obtener información de materia o maestro.")
                return

            horario_parts = horario_info.split(" - ")
            if len(horario_parts) != 3:
                messagebox.showerror("Error", "El formato del horario es incorrecto.")
                return
            dia, hora_inicio, hora_fin = horario_parts
            query_horario = """
                SELECT horario_id 
                FROM horarios 
                WHERE dia = %s AND hora_inicio = %s AND hora_fin = %s
            """
            horario_id = self.db_connection.fetch_all(query_horario, (dia, hora_inicio, hora_fin))
            if not horario_id:
                messagebox.showerror("Error", "Error al obtener información del horario.")
                return

            # Verificar si el maestro ya tiene un grupo en el mismo horario
            query_validacion = """
                SELECT g.grupo_id 
                FROM grupos g
                JOIN asignaciones a ON g.asignacion_id = a.asignacion_id
                JOIN horarios h ON g.horario_id = h.horario_id
                WHERE a.maestro_id = %s AND h.dia = %s AND h.hora_inicio = %s AND h.hora_fin = %s
            """
            resultado_validacion = self.db_connection.fetch_all(
                query_validacion, (maestro_id[0][0], dia, hora_inicio, hora_fin)
            )

            if resultado_validacion:
                messagebox.showerror(
                    "Error", f"El maestro {maestro_nombre} ya tiene asignado un grupo en este horario."
                )
                return

            query_asignacion = """
                INSERT INTO asignaciones (maestro_id, materia_id) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE asignacion_id = LAST_INSERT_ID(asignacion_id)
            """
            self.db_connection.execute_query(query_asignacion, (maestro_id[0][0], materia_id[0][0]))
            asignacion_id_query = "SELECT LAST_INSERT_ID()"
            asignacion_id = self.db_connection.fetch_all(asignacion_id_query)[0][0]

            query_salon = "SELECT salon_id FROM salones WHERE nombre = %s"
            salon_id = self.db_connection.fetch_all(query_salon, (salon_nombre,))
            if not salon_id:
                messagebox.showerror("Error", "Error al obtener información del salón.")
                return

            query_grupo = """
                INSERT INTO grupos (grupo_id, nombre, asignacion_id, salon_id, horario_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db_connection.execute_query(query_grupo, 
                                            (grupo_id, nombre_grupo, asignacion_id, salon_id[0][0], horario_id[0][0]))
            messagebox.showinfo("Éxito", "Grupo guardado correctamente.")
            self.limpiar_campos()
            self.button_guardar.config(state="disabled")
            self.button_crear.config(state="normal")

        except Exception as e:
            self.db_connection.connection.rollback()
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")





    def buscar_grupo(self):
        try:
            grupo_id = self.search_entry.get()
            if not grupo_id:
                messagebox.showerror("Error", "Por favor, ingresa el ID del grupo.")
                return

            query = """
                SELECT g.grupo_id, g.nombre, s.nombre AS salon, 
                    h.dia, h.hora_inicio, h.hora_fin, 
                    u.nombre AS maestro, m.nombre AS materia, 
                    c.nombre AS carrera, m.semestre, s.capacidad
                FROM grupos g
                JOIN salones s ON g.salon_id = s.salon_id
                JOIN horarios h ON g.horario_id = h.horario_id
                JOIN asignaciones a ON g.asignacion_id = a.asignacion_id
                JOIN maestros ma ON a.maestro_id = ma.maestro_id
                JOIN usuarios u ON ma.usuario_id = u.usuario_id
                JOIN materias m ON a.materia_id = m.materia_id
                JOIN carreras c ON m.carrera_id = c.carrera_id
                WHERE g.grupo_id = %s
            """
            resultado = self.db_connection.fetch_all(query, (grupo_id,))
            
            if not resultado:
                messagebox.showinfo("Información", "No se encontró ningún grupo con el ID proporcionado.")
                return
            
            # Mostrar información en los campos
            grupo = resultado[0]
            
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, 'end')
            self.entry_id.insert(0,grupo[0])
            self.entry_id.config(state="disabled")
            self.entry_nombre.delete(0, 'end')
            self.entry_nombre.insert(0, grupo[1])
            self.combo_salon.set(grupo[2])
            self.combo_horario.set(f"{grupo[3]} - {grupo[4]} - {grupo[5]}")
            self.combo_maestro.set(grupo[6])
            self.combo_materia.set(grupo[7])
            self.entry_carrera.config(state="normal")
            self.entry_carrera.delete(0, 'end')
            self.entry_carrera.insert(0, grupo[8])
            self.entry_carrera.config(state="disabled")
            self.entry_semestre.config(state="normal")
            self.entry_semestre.delete(0, 'end')
            self.entry_semestre.insert(0, grupo[9])
            self.entry_semestre.config(state="disabled")
            self.entry_max_alumnos.config(state="normal")
            self.entry_max_alumnos.delete(0, 'end')
            self.entry_max_alumnos.insert(0, grupo[10])
            self.entry_max_alumnos.config(state="disabled")
            self.button_actualizar.config(state="normal")
            self.button_cancelar.config(state="normal")
            self.button_crear.config(state="disabled")
            self.button_eliminar.config(state="normal")
            self.horario_inicial = self.combo_horario.get()  # Guarda el horario original

            messagebox.showinfo("Éxito", "Grupo encontrado y cargado.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al buscar el grupo: {str(e)}")

    def actualizar_grupo(self):
        try:
            self.entry_id.config(state="normal")
            grupo_id = self.entry_id.get()
            nombre_grupo = self.entry_nombre.get()
            materia_nombre = self.combo_materia.get()
            maestro_nombre = self.combo_maestro.get()
            salon_nombre = self.combo_salon.get()
            horario_info = self.combo_horario.get()

            if not (grupo_id and nombre_grupo and materia_nombre and maestro_nombre and salon_nombre and horario_info):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return
            # Validación del formato del nombre del grupo
            if not re.fullmatch(r"D\d{2}", nombre_grupo):
                messagebox.showerror("Error", "El nombre del grupo debe tener el formato 'DXX', donde XX son dos dígitos.")
                return

            query_materia = "SELECT materia_id FROM materias WHERE nombre = %s"
            materia_id = self.db_connection.fetch_all(query_materia, (materia_nombre,))
            query_maestro = """
                SELECT m.maestro_id 
                FROM maestros m 
                JOIN usuarios u ON m.usuario_id = u.usuario_id 
                WHERE u.nombre = %s
            """
            maestro_id = self.db_connection.fetch_all(query_maestro, (maestro_nombre,))

            if not materia_id or not maestro_id:
                messagebox.showerror("Error", "Error al obtener información de materia o maestro.")
                return

            query_asignacion = """
                SELECT asignacion_id 
                FROM grupos 
                WHERE grupo_id = %s
            """
            asignacion_id = self.db_connection.fetch_all(query_asignacion, (grupo_id,))
            if not asignacion_id:
                messagebox.showerror("Error", "No se encontró una asignación válida para el grupo.")
                return

            query_actualizar_asignacion = """
                UPDATE asignaciones
                SET maestro_id = %s, materia_id = %s
                WHERE asignacion_id = %s
            """
            self.db_connection.execute_query(query_actualizar_asignacion, 
                                            (maestro_id[0][0], materia_id[0][0], asignacion_id[0][0]))

            query_salon = "SELECT salon_id FROM salones WHERE nombre = %s"
            salon_id = self.db_connection.fetch_all(query_salon, (salon_nombre,))
            if not salon_id:
                messagebox.showerror("Error", "Error al obtener información del salón.")
                return

            # Validación del horario solo si cambió
            if horario_info != self.horario_inicial:
                horario_parts = horario_info.split(" - ")
                if len(horario_parts) != 3:
                    messagebox.showerror("Error", "El formato del horario es incorrecto.")
                    return
                dia, hora_inicio, hora_fin = horario_parts
                query_horario = """
                    SELECT horario_id 
                    FROM horarios 
                    WHERE dia = %s AND hora_inicio = %s AND hora_fin = %s
                """
                horario_id = self.db_connection.fetch_all(query_horario, (dia, hora_inicio, hora_fin))
                if not horario_id:
                    messagebox.showerror("Error", "Error al obtener información del horario.")
                    return

                query_validacion = """
                    SELECT g.grupo_id 
                    FROM grupos g
                    JOIN asignaciones a ON g.asignacion_id = a.asignacion_id
                    JOIN horarios h ON g.horario_id = h.horario_id
                    WHERE a.maestro_id = %s AND h.dia = %s AND h.hora_inicio = %s AND h.hora_fin = %s
                """
                resultado_validacion = self.db_connection.fetch_all(
                    query_validacion, (maestro_id[0][0], dia, hora_inicio, hora_fin)
                )

                if resultado_validacion:
                    messagebox.showerror(
                        "Error", f"El maestro {maestro_nombre} ya tiene asignado un grupo en este horario."
                    )
                    return
            else:
                # Si no cambió, usa el horario_id actual
                query_horario = """
                    SELECT horario_id 
                    FROM grupos 
                    WHERE grupo_id = %s
                """
                horario_id = self.db_connection.fetch_all(query_horario, (grupo_id,))
                if not horario_id:
                    messagebox.showerror("Error", "Error al obtener el horario actual.")
                    return

            query_grupo = """
                UPDATE grupos
                SET nombre = %s, asignacion_id = %s,
                    salon_id = %s, horario_id = %s
                WHERE grupo_id = %s
            """
            self.db_connection.execute_query(query_grupo, (nombre_grupo, asignacion_id[0][0], salon_id[0][0], horario_id[0][0], grupo_id))

            messagebox.showinfo("Éxito", "Grupo actualizado correctamente.")
            self.limpiar_campos()
            self.button_guardar.config(state="disabled")
            self.button_crear.config(state="normal")
        except Exception as e:
            self.db_connection.connection.rollback()
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def eliminar_grupo(self):
        try:
            grupo_id = self.entry_id.get()
            if not grupo_id:
                messagebox.showerror("Error", "Por favor, ingresa el ID del grupo.")
                return

            # Verificar si hay registros asociados en pre_registro
            query_preregistro = "SELECT COUNT(*) FROM pre_registro WHERE grupo_id = %s"
            registros_preregistro = self.db_connection.fetch_all(query_preregistro, (grupo_id,))

            # Verificar si hay registros asociados en inscripciones
            query_inscripciones = "SELECT COUNT(*) FROM inscripciones WHERE grupo_id = %s"
            registros_inscripciones = self.db_connection.fetch_all(query_inscripciones, (grupo_id,))

            # Mostrar mensajes según los casos
            if registros_preregistro[0][0] > 0:
                respuesta = messagebox.askyesno(
                    "Confirmar",
                    "Hay alumnos registrados en el pre-registro. ¿Estás seguro de eliminar el grupo?"
                )
                if not respuesta:
                    return

            if registros_inscripciones[0][0] > 0:
                respuesta = messagebox.askyesno(
                    "Confirmar",
                    "Hay alumnos inscritos formalmente en este grupo. ¿Estás seguro de eliminar el grupo?"
                )
                if not respuesta:
                    return

            # Confirmación general de eliminación si no hay casos previos
            respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este grupo?")
            if not respuesta:
                return

            # Eliminar el grupo
            query = "DELETE FROM grupos WHERE grupo_id = %s"
            self.db_connection.execute_query(query, (grupo_id,))
            self.db_connection.connection.commit()

            messagebox.showinfo("Éxito", "Grupo eliminado correctamente.")
            self.limpiar_campos()
            self.button_guardar.config(state="disabled")
            self.button_crear.config(state="normal")
        except Exception as e:
            self.db_connection.connection.rollback()
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el grupo: {str(e)}")


    def limpiar_campos(self):
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, END)
        self.entry_id.config(state="disabled")

        self.entry_nombre.delete(0, END)

        self.combo_materia.set("")
        self.combo_maestro.set("")
        self.combo_salon.set("")
        self.combo_horario.set("")

        self.entry_carrera.config(state="normal")
        self.entry_carrera.delete(0, END)
        self.entry_carrera.config(state="disabled")

        self.entry_semestre.config(state="normal")
        self.entry_semestre.delete(0, END)
        self.entry_semestre.config(state="disabled")

        self.entry_max_alumnos.config(state="normal")
        self.entry_max_alumnos.delete(0, END)
        self.entry_max_alumnos.config(state="disabled")

        self.button_guardar.config(state="disabled")
        self.button_crear.config(state="normal")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")

