
import tkinter as tk
from tkinter import ttk


productos = [
    {
        "sku": "P001",
        "nombre": "Mouse inalámbrico",
        "categoria": "Accesorios",
        "precio": 249.90,
        "stock": 15
    },
    {
        "sku": "P002",
        "nombre": "Teclado mecánico",
        "categoria": "Accesorios",
        "precio": 899.00,
        "stock": 8
    },
    {
        "sku": "P003",
        "nombre": "Monitor 24 pulgadas",
        "categoria": "Pantallas",
        "precio": 3299.00,
        "stock": 4
    }
]


ventana = tk.Tk()
ventana.title("Tabla con Treeview")
ventana.geometry("800x400")

titulo = ttk.Label(
    ventana,
    text="Productos registrados",
    font=("Arial", 14, "bold")
)

titulo.pack(pady=10)

columnas = ("sku", "nombre", "categoria", "precio", "stock")

tabla = ttk.Treeview(
    ventana,
    columns=columnas,
    show="headings"
)

for columna in columnas:
    tabla.heading(columna, text=columna.upper())
    tabla.column(columna, width=140)

tabla.pack(fill="both", expand=True, padx=20, pady=20)

for producto in productos:
    tabla.insert(
        "",
        "end",
        values=(
            producto["sku"],
            producto["nombre"],
            producto["categoria"],
            producto["precio"],
            producto["stock"]
        )
    )

ventana.mainloop()
