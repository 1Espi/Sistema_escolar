import tkinter as tk
from tkinter import ttk, messagebox, END
from datetime import datetime, timedelta
from utilities.connection import MySQLConnection

class HorariosFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        self.setup_ui()

    def generar_horarios(self, inicio, fin, intervalo):
        horarios = []
        hora_actual = inicio
        while hora_actual <= fin:
            horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=intervalo)
        return horarios

    def setup_ui(self):
        title = tk.Label(self, text="Horarios", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self, text="Ingresar ID de horario:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = tk.Entry(self)
        self.id_entry.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(self, text="Buscar", command=self.buscar_horario).grid(row=1, column=2, padx=5)

        tk.Label(self, text="ID:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_id = tk.Entry(self, state="disabled")
        self.entry_id.grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(self, text="Día:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_dia = ttk.Combobox(self, values=["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"], state="disabled")
        self.entry_dia.grid(row=3, column=1, sticky="w", padx=5)

        hora_inicio_inicio = datetime.strptime("07:00", "%H:%M")
        hora_inicio_fin = datetime.strptime("19:00", "%H:%M")
        horarios_inicio = self.generar_horarios(hora_inicio_inicio, hora_inicio_fin, 60)

        tk.Label(self, text="Hora inicio:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_hora_inicio = ttk.Combobox(self, values=horarios_inicio, state="disabled")
        self.entry_hora_inicio.grid(row=4, column=1, sticky="w", padx=5)

        hora_fin_inicio = datetime.strptime("07:55", "%H:%M")
        hora_fin_fin = datetime.strptime("20:55", "%H:%M")
        horarios_fin = self.generar_horarios(hora_fin_inicio, hora_fin_fin, 60)

        tk.Label(self, text="Hora fin:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_hora_fin = ttk.Combobox(self, values=horarios_fin, state="disabled")
        self.entry_hora_fin.grid(row=5, column=1, sticky="w", padx=5)
        self.button_crear = tk.Button(self, text="Crear", command=self.crear_horario)
        self.button_crear.grid(row=6, column=0, sticky="ew", padx=5)

        self.button_guardar = tk.Button(self, text="Guardar", command=self.guardar_horario, state="disabled")
        self.button_guardar.grid(row=6, column=1, sticky="ew", padx=5)

        self.button_actualizar = tk.Button(self, text="Actualizar", command=self.actualizar_horario, state="disabled")
        self.button_actualizar.grid(row=6, column=2, sticky="ew", padx=5)

        self.button_eliminar = tk.Button(self, text="Eliminar", command=self.eliminar_horario, state="disabled")
        self.button_eliminar.grid(row=6, column=3, sticky="ew", padx=5)

        self.button_cancelar = tk.Button(self, text="Cancelar", command=self.limpiar_campos, state="disabled")
        self.button_cancelar.grid(row=6, column=4, sticky="ew", padx=5)
    def desbloquear_campos(self):
        self.entry_dia.config(state="readonly")
        self.entry_hora_inicio.config(state="normal")
        self.entry_hora_fin.config(state="normal")

    def crear_horario(self):
        self.desbloquear_campos()
        self.button_guardar.config(state="normal")
        self.button_cancelar.config(state="normal")
        self.button_crear.config(state="disabled")
        self.entry_id.config(state="normal") 
        query = "SELECT MAX(horario_id) FROM horarios"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, max_id)
        self.entry_id.config(state="disabled") 

    def guardar_horario(self):
        self.entry_id.config(state="normal")
        id = self.entry_id.get()
        dia = self.entry_dia.get()
        hora_inicio = self.entry_hora_inicio.get()
        hora_fin = self.entry_hora_fin.get()

        if not (dia and hora_inicio and hora_fin):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return

        query = "INSERT INTO horarios (horario_id, dia, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)"
        self.db_connection.execute_query(query, (id, dia, hora_inicio, hora_fin))
        
        messagebox.showinfo("Éxito", "Horario creado con éxito.")
        self.limpiar_campos()

    def buscar_horario(self):
        horario_id = self.id_entry.get()
        if not horario_id.isdigit():
            messagebox.showerror("Error", "ID de horario inválido.")
            return

        query = "SELECT horario_id, dia, hora_inicio, hora_fin FROM horarios WHERE horario_id = %s"
        result = self.db_connection.fetch_all(query, (horario_id,))

        if result:
            horario = result[0]
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, horario[0])
            self.entry_id.config(state="disabled")

            self.entry_dia.set(horario[1])
            self.entry_hora_inicio.config(state="normal")
            self.entry_hora_inicio.delete(0, END)
            self.entry_hora_inicio.insert(0, horario[2])

            self.entry_hora_fin.config(state="normal")
            self.entry_hora_fin.delete(0, END)
            self.entry_hora_fin.insert(0, horario[3])

            self.desbloquear_campos()
            self.button_actualizar.config(state="normal")
            self.button_eliminar.config(state="normal")
            self.button_cancelar.config(state="normal")
            self.button_crear.config(state="disabled")
        else:
            messagebox.showinfo("Información", "Horario no encontrado.")

    def actualizar_horario(self):
        horario_id = self.entry_id.get()
        dia = self.entry_dia.get()
        hora_inicio = self.entry_hora_inicio.get()
        hora_fin = self.entry_hora_fin.get()

        if not horario_id:
            messagebox.showerror("Error", "No se ha cargado ningún horario.")
            return
        if not (dia and hora_inicio and hora_fin):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return

        query = "UPDATE horarios SET dia = %s, hora_inicio = %s, hora_fin = %s WHERE horario_id = %s"
        self.db_connection.execute_query(query, (dia, hora_inicio, hora_fin, horario_id))
        
        messagebox.showinfo("Éxito", "Horario actualizado con éxito.")
        self.limpiar_campos()

    def eliminar_horario(self):
        horario_id = self.entry_id.get()
        if not horario_id:
            messagebox.showerror("Error", "No se ha cargado ningún horario.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este horario?"):
            query = "DELETE FROM horarios WHERE horario_id = %s"
            self.db_connection.execute_query(query, (horario_id,))
            messagebox.showinfo("Éxito", "Horario eliminado con éxito.")
            self.limpiar_campos()

    def limpiar_campos(self):
        self.id_entry.delete(0, END)
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, END)
        self.entry_id.config(state="disabled")
        self.entry_dia.set("")
        self.entry_hora_inicio.delete(0, END)
        self.entry_hora_inicio.config(state="disabled")
        self.entry_hora_fin.delete(0, END)
        self.entry_hora_fin.config(state="disabled")
        
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")
