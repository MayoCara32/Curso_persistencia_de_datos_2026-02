
import tkinter as tk
from tkinter import messagebox


def registrar_producto():
    sku = entrada_sku.get().strip().upper()
    nombre = entrada_nombre.get().strip()
    precio_texto = entrada_precio.get().strip()

    if sku == "" or nombre == "" or precio_texto == "":
        messagebox.showwarning(
            "Datos incompletos",
            "Todos los campos son obligatorios."
        )
        return

    try:
        precio = float(precio_texto)

        if precio <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Precio inválido",
            "El precio debe ser un número mayor que cero."
        )
        return

    mensaje = (
        f"Producto capturado correctamente:\n\n"
        f"SKU: {sku}\n"
        f"Nombre: {nombre}\n"
        f"Precio: ${precio:.2f}"
    )

    messagebox.showinfo("Producto", mensaje)


ventana = tk.Tk()
ventana.title("Formulario básico")
ventana.geometry("500x350")

tk.Label(ventana, text="Registro básico de producto", font=("Arial", 14)).pack(pady=10)

tk.Label(ventana, text="SKU").pack()
entrada_sku = tk.Entry(ventana, width=30)
entrada_sku.pack(pady=5)

tk.Label(ventana, text="Nombre").pack()
entrada_nombre = tk.Entry(ventana, width=30)
entrada_nombre.pack(pady=5)

tk.Label(ventana, text="Precio").pack()
entrada_precio = tk.Entry(ventana, width=30)
entrada_precio.pack(pady=5)

boton_guardar = tk.Button(
    ventana,
    text="Registrar producto",
    command=registrar_producto
)

boton_guardar.pack(pady=20)

ventana.mainloop()
