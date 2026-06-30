
import tkinter as tk
from tkinter import ttk, messagebox


class AppProductos:
    def __init__(self, root):
        self.root = root
        self.root.title("App de productos con clase")
        self.root.geometry("850x500")

        self.productos = []

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = ttk.Label(
            self.root,
            text="Gestión visual de productos",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=10)

        frame_formulario = ttk.LabelFrame(
            self.root,
            text="Formulario"
        )
        frame_formulario.pack(fill="x", padx=20, pady=10)

        ttk.Label(frame_formulario, text="SKU").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame_formulario, text="Nombre").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_formulario, text="Precio").grid(row=0, column=2, padx=5, pady=5)

        self.entry_sku = ttk.Entry(frame_formulario, width=15)
        self.entry_nombre = ttk.Entry(frame_formulario, width=30)
        self.entry_precio = ttk.Entry(frame_formulario, width=15)

        self.entry_sku.grid(row=1, column=0, padx=5, pady=5)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)
        self.entry_precio.grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(
            frame_formulario,
            text="Agregar",
            command=self.agregar_producto
        ).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(
            frame_formulario,
            text="Limpiar",
            command=self.limpiar_formulario
        ).grid(row=1, column=4, padx=5, pady=5)

        frame_tabla = ttk.LabelFrame(
            self.root,
            text="Productos"
        )
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("sku", "nombre", "precio")

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            self.tabla.heading(columna, text=columna.upper())
            self.tabla.column(columna, width=180)

        self.tabla.pack(fill="both", expand=True)

    def agregar_producto(self):
        sku = self.entry_sku.get().strip().upper()
        nombre = self.entry_nombre.get().strip()
        precio_texto = self.entry_precio.get().strip()

        if not sku or not nombre or not precio_texto:
            messagebox.showwarning("Datos incompletos", "Completa todos los campos.")
            return

        try:
            precio = float(precio_texto)

            if precio <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Precio inválido", "El precio debe ser mayor que cero.")
            return

        producto = {
            "sku": sku,
            "nombre": nombre,
            "precio": precio
        }

        self.productos.append(producto)

        self.tabla.insert(
            "",
            "end",
            values=(sku, nombre, precio)
        )

        self.limpiar_formulario()

    def limpiar_formulario(self):
        self.entry_sku.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)


def main():
    root = tk.Tk()
    app = AppProductos(root)
    root.mainloop()


if __name__ == "__main__":
    main()
