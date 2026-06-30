
import tkinter as tk
from tkinter import ttk, messagebox


def limpiar_formulario():
    entrada_sku.delete(0, tk.END)
    entrada_nombre.delete(0, tk.END)
    entrada_categoria.delete(0, tk.END)
    entrada_precio.delete(0, tk.END)
    entrada_stock.delete(0, tk.END)


def registrar_producto():
    sku = entrada_sku.get().strip().upper()
    nombre = entrada_nombre.get().strip()
    categoria = entrada_categoria.get().strip()
    precio_texto = entrada_precio.get().strip()
    stock_texto = entrada_stock.get().strip()

    if not sku or not nombre or not categoria or not precio_texto or not stock_texto:
        messagebox.showwarning("Datos incompletos", "Todos los campos son obligatorios.")
        return

    try:
        precio = float(precio_texto)
        stock = int(stock_texto)

        if precio <= 0:
            raise ValueError

        if stock < 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Datos inválidos",
            "Precio debe ser mayor que cero y stock debe ser entero no negativo."
        )
        return

    messagebox.showinfo(
        "Producto capturado",
        f"{sku} - {nombre} - {categoria} - ${precio:.2f} - Stock: {stock}"
    )

    limpiar_formulario()


ventana = tk.Tk()
ventana.title("Formulario con grid")
ventana.geometry("700x300")

frame = ttk.LabelFrame(ventana, text="Datos del producto")
frame.pack(fill="x", padx=20, pady=20)

ttk.Label(frame, text="SKU").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Label(frame, text="Nombre").grid(row=0, column=1, padx=5, pady=5, sticky="w")
ttk.Label(frame, text="Categoría").grid(row=0, column=2, padx=5, pady=5, sticky="w")

entrada_sku = ttk.Entry(frame, width=15)
entrada_nombre = ttk.Entry(frame, width=25)
entrada_categoria = ttk.Entry(frame, width=20)

entrada_sku.grid(row=1, column=0, padx=5, pady=5)
entrada_nombre.grid(row=1, column=1, padx=5, pady=5)
entrada_categoria.grid(row=1, column=2, padx=5, pady=5)

ttk.Label(frame, text="Precio").grid(row=2, column=0, padx=5, pady=5, sticky="w")
ttk.Label(frame, text="Stock").grid(row=2, column=1, padx=5, pady=5, sticky="w")

entrada_precio = ttk.Entry(frame, width=15)
entrada_stock = ttk.Entry(frame, width=15)

entrada_precio.grid(row=3, column=0, padx=5, pady=5)
entrada_stock.grid(row=3, column=1, padx=5, pady=5)

boton_guardar = ttk.Button(
    frame,
    text="Registrar",
    command=registrar_producto
)

boton_limpiar = ttk.Button(
    frame,
    text="Limpiar",
    command=limpiar_formulario
)

boton_guardar.grid(row=4, column=0, padx=5, pady=15)
boton_limpiar.grid(row=4, column=1, padx=5, pady=15)

ventana.mainloop()
