import tkinter as tk
import utilities.connection as connfile
from tkinter import END, messagebox, ttk

from utilities.connection import MySQLConnection

class CarrerasFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.db_connection = MySQLConnection()
        self.db_connection.connect()
        
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self, text="Carreras", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        #ENTRYS
        
        tk.Label(self, text="Buscar por id:").grid(row=1, column=1, padx=5)
        self.id_busqueda = tk.Entry(self, state="normal")
        self.id_busqueda.grid(row=1, column=2, padx=5, pady=20)
        self.button_busqueda = tk.Button(self, text="Buscar", command=self.buscar_carrera)
        self.button_busqueda.grid(row=1, column=3, padx=5)
        
        tk.Label(self, text="Id de carrera:").grid(row=2, column=1, padx=5)
        self.entry_id = tk.Entry(self, state="disabled")
        self.entry_id.grid(row=2, column=2, padx=5, pady=5)
        
        tk.Label(self, text="Nombre:").grid(row=3, column=1, padx=5)
        self.entry_nombre = tk.Entry(self, state="disabled")
        self.entry_nombre.grid(row=3, column=2, padx=5, pady=5)
        
        tk.Label(self, text="Descripción:").grid(row=4, column=1, padx=5)
        self.entry_descripcion = tk.Entry(self, state="disabled")
        self.entry_descripcion.grid(row=4, column=2, padx=5, pady=5)
        
        tk.Label(self, text="Semestres:").grid(row=5, column=1, padx=5)
        self.entry_semestres = tk.Entry(self, state="disabled")
        self.entry_semestres.grid(row=5, column=2, padx=5, pady=5)
        
        #BOTONES
        
        self.frame_botones = tk.Frame(self)
        self.frame_botones.grid(row=6, columnspan=100, pady=10)
        
        self.button_crear = tk.Button(self.frame_botones, text="Crear", command=self.crear_carrera)
        self.button_crear.grid(row=0, column=0, padx=5)
        
        self.button_guardar = tk.Button(self.frame_botones, text="Guardar", command=self.guardar_carrera, state="disabled")
        self.button_guardar.grid(row=0, column=1, padx=5)
        
        self.button_actualizar = tk.Button(self.frame_botones, text="Actualizar", command=self.actualizar_carrera, state="disabled")
        self.button_actualizar.grid(row=0, column=2, padx=5)
        
        self.button_eliminar = tk.Button(self.frame_botones, text="Eliminar", command=self.eliminar_carrera, state="disabled")
        self.button_eliminar.grid(row=0, column=3, padx=5)
    
        self.button_cancelar = tk.Button(self.frame_botones, text="Cancelar", command=self.cancelar_carrera, state="disabled")
        self.button_cancelar.grid(row=0, column=4, padx=5)
        
    def limpiar_campos(self):
        for entry in [self.entry_id, self.entry_nombre, self.entry_descripcion, self.entry_semestres]:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            
    def buscar_carrera(self):
        id = self.id_busqueda.get()
        if not id:
            messagebox.showerror("Error", "Ingrese un id a buscar")
            return
        
        if not id.isdigit():
            messagebox.showerror("Error", "El id a buscar tiene que ser un numero entero")
            return
        
        query = "SELECT carrera_id, nombre, descripcion, semestres FROM carreras WHERE carrera_id = %s"
        result = self.db_connection.fetch_all(query, (id,))
        
        if not result:
            messagebox.showerror("Error", "No se encontró la carrera en la base de datos")
            return
        
        self.limpiar_campos()
        self.entry_id.insert(0, result[0][0])
        self.entry_nombre.insert(0, result[0][1])
        self.entry_descripcion.insert(0, result[0][2])
        self.entry_semestres.insert(0, result[0][3])
        
        self.entry_id.config(state="disabled")
        
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="normal")
        self.button_eliminar.config(state="normal")
        self.button_cancelar.config(state="normal")
        
    def crear_carrera(self):
        self.limpiar_campos()
        
        self.button_crear.config(state="disabled")
        self.button_guardar.config(state="normal")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="normal")
        
        query = "SELECT MAX(carrera_id) FROM carreras"
        result = self.db_connection.fetch_all(query)
        max_id = result[0][0] + 1 if result[0][0] else 1
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, max_id)
        self.entry_id.config(state="disabled") 
        
    def guardar_carrera(self):
        id = self.entry_id.get()
        nombre = self.entry_nombre.get()
        descripcion = self.entry_descripcion.get()
        semestres = self.entry_semestres.get()
        
        if not id or not nombre or not descripcion or not semestres:
            messagebox.showerror("Error", "Todos los campos deben ser llenados")
            return
        
        if not semestres.isdigit():
            messagebox.showerror("Error", "Los semestres deben ser un numero entero")
            return
        
        query = "INSERT INTO carreras (carrera_id, nombre, descripcion, semestres) VALUES (%s, %s, %s, %s)"
        self.db_connection.execute_query(query, (id, nombre, descripcion, semestres))
        messagebox.showinfo("Exito", "Carrera ingresada correctamente")
        self.cancelar_carrera()
    
    def actualizar_carrera(self):
        id = self.entry_id.get()
        nombre = self.entry_nombre.get()
        descripcion = self.entry_descripcion.get()
        semestres = self.entry_semestres.get()
        
        if not id or not nombre or not descripcion or not semestres:
            messagebox.showerror("Error", "Todos los campos deben ser llenados")
            return
        
        query = "UPDATE carreras SET nombre = %s, descripcion = %s, semestres = %s WHERE carrera_id = %s"
        self.db_connection.execute_query(query, (nombre, descripcion, semestres, id))
        messagebox.showinfo("Exito", "Carrera actualizada correctamente")
        self.cancelar_carrera()
        
    def eliminar_carrera(self):
        id = self.entry_id.get()
        query = "DELETE FROM carreras WHERE carrera_id = %s"
        self.db_connection.execute_query(query, (id,))
        messagebox.showinfo("Exito", "Carrera eliminada correctamente")
        self.cancelar_carrera()
        
    def cancelar_carrera(self):
        for entry in [self.entry_id, self.entry_nombre, self.entry_descripcion, self.entry_semestres]:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.config(state="disabled")
        
        self.button_crear.config(state="normal")
        self.button_guardar.config(state="disabled")
        self.button_actualizar.config(state="disabled")
        self.button_eliminar.config(state="disabled")
        self.button_cancelar.config(state="disabled")