import sqlite3
import pandas as pd
from pathlib import Path 

RUTA = Path(__file__).parent / "modelo_relacional_ventas.db"
def consulta_db ():
    conexion = sqlite3.connect(RUTA)
    cursor = conexion.cursor()
    print("Tabla clientes")
    tabla_clientes = pd.read_sql_query("SELECT * FROM ventas", conexion)
    print(tabla_clientes)
def menu ():
    print("Bienvenido a la base de datos")
    print("1.- Consultar base de datos")
    opcion = int(input("Selecciona tu opción: "))
    if opcion == 1:
        consulta_db()
menu()
print(f"La ruta de la base de datos es: {RUTA.resolve()}")