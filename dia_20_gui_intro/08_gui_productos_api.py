
import tkinter as tk
from tkinter import ttk, messagebox
import requests


BASE_URL = "http://127.0.0.1:8000"


class ClienteAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def hacer_peticion(self, metodo, ruta, json_data=None, params=None):
        url = f"{self.base_url}{ruta}"

        try:
            respuesta = self.session.request(
                method=metodo,
                url=url,
                json=json_data,
                params=params,
                timeout=5
            )

            return respuesta

        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                "Error de conexión",
                "No se pudo conectar con la API.\n\n"
                "Verifica que la API esté encendida con:\n"
                "python -m uvicorn main:app --reload"
            )
            return None

        except requests.exceptions.Timeout:
            messagebox.showerror(
                "Tiempo agotado",
                "La API tardó demasiado en responder."
            )
            return None

    def validar_respuesta(self, respuesta):
        if respuesta is None:
            return None

        if 200 <= respuesta.status_code < 300:
            return respuesta.json()

        try:
            detalle = respuesta.json().get("detail", respuesta.json())
        except Exception:
            detalle = respuesta.text

        messagebox.showerror(
            f"Error HTTP {respuesta.status_code}",
            str(detalle)
        )

        return None

    def health(self):
        respuesta = self.hacer_peticion("GET", "/health")
        return self.validar_respuesta(respuesta)

    def listar_productos(self, solo_activos=False):
        respuesta = self.hacer_peticion(
            "GET",
            "/productos",
            params={"solo_activos": solo_activos}
        )

        return self.validar_respuesta(respuesta) or []


class GUIProductosAPI:
    def __init__(self, root):
        self.root = root
        self.root.title("Productos desde API")
        self.root.geometry("900x500")

        self.api = ClienteAPI(BASE_URL)

        self.crear_interfaz()
        self.verificar_api()

    def crear_interfaz(self):
        titulo = ttk.Label(
            self.root,
            text="Consulta de productos desde FastAPI",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=10)

        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(fill="x", padx=20, pady=10)

        ttk.Button(
            frame_botones,
            text="Verificar API",
            command=self.verificar_api
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_botones,
            text="Cargar productos",
            command=self.cargar_productos
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_botones,
            text="Limpiar tabla",
            command=self.limpiar_tabla
        ).pack(side="left", padx=5)

        frame_tabla = ttk.LabelFrame(
            self.root,
            text="Productos"
        )
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = (
            "sku",
            "nombre",
            "categoria",
            "precio",
            "stock",
            "activo"
        )

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            self.tabla.heading(columna, text=columna.upper())
            self.tabla.column(columna, width=130)

        self.tabla.pack(fill="both", expand=True)

    def verificar_api(self):
        respuesta = self.api.health()

        if respuesta:
            messagebox.showinfo(
                "API disponible",
                "La API respondió correctamente."
            )

    def limpiar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def cargar_productos(self):
        productos = self.api.listar_productos(solo_activos=False)

        self.limpiar_tabla()

        for producto in productos:
            activo = "Sí" if producto.get("activo") == 1 else "No"

            self.tabla.insert(
                "",
                "end",
                values=(
                    producto.get("sku"),
                    producto.get("nombre"),
                    producto.get("categoria"),
                    producto.get("precio"),
                    producto.get("stock"),
                    activo
                )
            )


def main():
    root = tk.Tk()
    app = GUIProductosAPI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
