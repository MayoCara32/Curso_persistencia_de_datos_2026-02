
import tkinter as tk


ventana = tk.Tk()
ventana.title("Mi primera interfaz gráfica")
ventana.geometry("500x300")

etiqueta = tk.Label(
    ventana,
    text="Hola, esta es mi primera ventana con Tkinter",
    font=("Arial", 14)
)

etiqueta.pack(pady=40)

ventana.mainloop()
