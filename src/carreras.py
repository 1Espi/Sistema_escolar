import tkinter as tk
import utilities.connection as connfile
from tkinter import END, messagebox, ttk

class CarrerasFrame(tk.Frame):
    def __init__(self, parent, container):
        super().__init__(container)
        self.parent = parent
        self.user_info = self.parent.user_info
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self, text="Carreras", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)