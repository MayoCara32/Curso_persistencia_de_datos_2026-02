
import tkinter as tk
from tkinter import messagebox


def saludar():
    messagebox.showinfo(
        "Saludo",
        "Hola, acabas de ejecutar una función desde un botón."
    )


ventana = tk.Tk()
ventana.title("Botones y eventos")
ventana.geometry("500x300")

titulo = tk.Label(
    ventana,
    text="Ejemplo de botón con evento",
    font=("Arial", 14)
)

titulo.pack(pady=20)

boton = tk.Button(
    ventana,
    text="Dar clic",
    command=saludar
)

boton.pack(pady=20)

ventana.mainloop()
