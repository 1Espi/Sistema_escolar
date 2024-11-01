#aqui va la funcion para devolver la conexion mysql

from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class MySQLConnection:
    def __init__(self):
        # Obtener datos de conexión desde el archivo .env
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")

        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except Error as e:
            messagebox.showerror('Error', f'Falló la conexión a la base de datos\n{e}')

    def execute_query(self, query: str, params: tuple = None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
        except Error as e:
            messagebox.showerror('Error', f'No se pudo ejectuar la query\n{e}')

    def fetch_all(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            messagebox.showerror('Error', f'No se pudieron obtener los resultados de la query\n{e}')
            return None

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()