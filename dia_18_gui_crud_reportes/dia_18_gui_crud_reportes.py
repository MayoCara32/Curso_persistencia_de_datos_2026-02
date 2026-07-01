
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import requests
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


BASE_URL = "http://127.0.0.1:8000"



class ClienteAPI:
    """
    Cliente para consumir la API del sistema de ventas.

    La GUI no se conecta directamente a SQLite.
    La GUI se comunica con FastAPI usando requests.
    """

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

        except requests.exceptions.RequestException as error:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error al consumir la API:\n{error}"
            )
            return None

    def validar_respuesta(self, respuesta):
        if respuesta is None:
            return None

        if 200 <= respuesta.status_code < 300:
            try:
                return respuesta.json()
            except Exception:
                return None

        try:
            contenido = respuesta.json()

            if isinstance(contenido, dict):
                detalle = contenido.get("detail", contenido)
            else:
                detalle = contenido

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

    def crear_producto(self, producto):
        respuesta = self.hacer_peticion(
            "POST",
            "/productos",
            json_data=producto
        )
        return self.validar_respuesta(respuesta)

    def actualizar_producto(self, sku, datos):
        respuesta = self.hacer_peticion(
            "PUT",
            f"/productos/{sku}",
            json_data=datos
        )
        return self.validar_respuesta(respuesta)

    def desactivar_producto(self, sku):
        respuesta = self.hacer_peticion(
            "DELETE",
            f"/productos/{sku}"
        )
        return self.validar_respuesta(respuesta)

    def listar_clientes(self, solo_activos=False):
        respuesta = self.hacer_peticion(
            "GET",
            "/clientes",
            params={"solo_activos": solo_activos}
        )
        return self.validar_respuesta(respuesta) or []

    def crear_cliente(self, cliente):
        respuesta = self.hacer_peticion(
            "POST",
            "/clientes",
            json_data=cliente
        )
        return self.validar_respuesta(respuesta)

    def listar_ventas(self):
        respuesta = self.hacer_peticion("GET", "/ventas")
        return self.validar_respuesta(respuesta) or []

    def resumen_ventas(self):
        respuesta = self.hacer_peticion("GET", "/ventas/resumen")
        return self.validar_respuesta(respuesta)



class SistemaVentasGUI:
    """
    Interfaz gráfica del sistema de ventas.

    Esta clase controla:
    - Ventana principal
    - Pestañas
    - Formularios
    - Tablas
    - Reportes
    - Gráficas
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ventas - GUI CRUD + Reportes")
        self.root.geometry("1200x750")

        self.api = ClienteAPI(BASE_URL)
        self.df_reporte_actual = pd.DataFrame()
        self.canvas_grafica = None

        self.crear_estilos()
        self.crear_interfaz()

        self.verificar_api()
        self.cargar_productos()
        self.cargar_clientes()

    def crear_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TButton", padding=6)
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Titulo.TLabel", font=("Arial", 15, "bold"))

    def crear_interfaz(self):
        titulo = ttk.Label(
            self.root,
            text="Sistema de Ventas con FastAPI, Tkinter, pandas y matplotlib",
            style="Titulo.TLabel"
        )
        titulo.pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_productos = ttk.Frame(self.notebook)
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_reportes = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_productos, text="Productos")
        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_reportes, text="Reportes")

        self.crear_tab_productos()
        self.crear_tab_clientes()
        self.crear_tab_reportes()

    def verificar_api(self):
        resultado = self.api.health()

        if resultado:
            messagebox.showinfo(
                "API disponible",
                "La API respondió correctamente."
            )

    def limpiar_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)


    # ---------------------------------------------------------
    # PESTAÑA PRODUCTOS
    # ---------------------------------------------------------

    def crear_tab_productos(self):
        frame_form = ttk.LabelFrame(
            self.tab_productos,
            text="Formulario de producto"
        )
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="SKU").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Nombre").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Categoría").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Precio").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Stock").grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.entry_sku = ttk.Entry(frame_form, width=15)
        self.entry_nombre = ttk.Entry(frame_form, width=25)
        self.entry_categoria = ttk.Entry(frame_form, width=20)
        self.entry_precio = ttk.Entry(frame_form, width=12)
        self.entry_stock = ttk.Entry(frame_form, width=10)

        self.entry_sku.grid(row=1, column=0, padx=5, pady=5)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)
        self.entry_categoria.grid(row=1, column=2, padx=5, pady=5)
        self.entry_precio.grid(row=1, column=3, padx=5, pady=5)
        self.entry_stock.grid(row=1, column=4, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Crear",
            command=self.crear_producto
        ).grid(row=1, column=5, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Actualizar",
            command=self.actualizar_producto
        ).grid(row=1, column=6, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Desactivar",
            command=self.desactivar_producto
        ).grid(row=1, column=7, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Limpiar",
            command=self.limpiar_formulario_producto
        ).grid(row=1, column=8, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Refrescar",
            command=self.cargar_productos
        ).grid(row=1, column=9, padx=5, pady=5)

        frame_tabla = ttk.LabelFrame(
            self.tab_productos,
            text="Productos registrados"
        )
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("sku", "nombre", "categoria", "precio", "stock", "activo")

        self.tree_productos = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            self.tree_productos.heading(columna, text=columna.upper())
            self.tree_productos.column(columna, width=140)

        self.tree_productos.pack(fill="both", expand=True)

        self.tree_productos.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_producto
        )


    def obtener_datos_producto_formulario(self):
        sku = self.entry_sku.get().strip().upper()
        nombre = self.entry_nombre.get().strip()
        categoria = self.entry_categoria.get().strip()
        precio_texto = self.entry_precio.get().strip()
        stock_texto = self.entry_stock.get().strip()

        if not sku or not nombre or not categoria or not precio_texto or not stock_texto:
            messagebox.showwarning(
                "Datos incompletos",
                "Todos los campos del producto son obligatorios."
            )
            return None

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
                "El precio debe ser mayor que cero y el stock debe ser entero no negativo."
            )
            return None

        return {
            "sku": sku,
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "stock": stock
        }

    def cargar_productos(self):
        productos = self.api.listar_productos(solo_activos=False)

        self.limpiar_treeview(self.tree_productos)

        for producto in productos:
            activo = "Sí" if producto.get("activo") == 1 else "No"

            self.tree_productos.insert(
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

    def crear_producto(self):
        producto = self.obtener_datos_producto_formulario()

        if producto is None:
            return

        resultado = self.api.crear_producto(producto)

        if resultado:
            messagebox.showinfo(
                "Producto creado",
                "El producto fue creado correctamente."
            )
            self.limpiar_formulario_producto()
            self.cargar_productos()

    def actualizar_producto(self):
        sku = self.entry_sku.get().strip().upper()

        if not sku:
            messagebox.showwarning(
                "SKU requerido",
                "Selecciona o escribe el SKU del producto a actualizar."
            )
            return

        datos = {}

        nombre = self.entry_nombre.get().strip()
        categoria = self.entry_categoria.get().strip()
        precio_texto = self.entry_precio.get().strip()
        stock_texto = self.entry_stock.get().strip()

        if nombre:
            datos["nombre"] = nombre

        if categoria:
            datos["categoria"] = categoria

        if precio_texto:
            try:
                precio = float(precio_texto)

                if precio <= 0:
                    raise ValueError

                datos["precio"] = precio

            except ValueError:
                messagebox.showerror(
                    "Precio inválido",
                    "El precio debe ser mayor que cero."
                )
                return

        if stock_texto:
            try:
                stock = int(stock_texto)

                if stock < 0:
                    raise ValueError

                datos["stock"] = stock

            except ValueError:
                messagebox.showerror(
                    "Stock inválido",
                    "El stock debe ser entero no negativo."
                )
                return

        if not datos:
            messagebox.showwarning(
                "Sin datos",
                "No se indicó ningún dato para actualizar."
            )
            return

        resultado = self.api.actualizar_producto(sku, datos)

        if resultado:
            messagebox.showinfo(
                "Producto actualizado",
                "El producto fue actualizado correctamente."
            )
            self.cargar_productos()

    def desactivar_producto(self):
        sku = self.entry_sku.get().strip().upper()

        if not sku:
            messagebox.showwarning(
                "SKU requerido",
                "Selecciona o escribe el SKU del producto a desactivar."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar desactivación",
            f"¿Deseas desactivar el producto {sku}?"
        )

        if not confirmar:
            return

        resultado = self.api.desactivar_producto(sku)

        if resultado:
            messagebox.showinfo(
                "Producto desactivado",
                "El producto fue desactivado correctamente."
            )
            self.cargar_productos()

    def seleccionar_producto(self, event):
        seleccion = self.tree_productos.selection()

        if not seleccion:
            return

        valores = self.tree_productos.item(seleccion[0], "values")

        self.limpiar_formulario_producto()

        self.entry_sku.insert(0, valores[0])
        self.entry_nombre.insert(0, valores[1])
        self.entry_categoria.insert(0, valores[2])
        self.entry_precio.insert(0, valores[3])
        self.entry_stock.insert(0, valores[4])

    def limpiar_formulario_producto(self):
        self.entry_sku.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)


    # ---------------------------------------------------------
    # PESTAÑA CLIENTES
    # ---------------------------------------------------------

    def crear_tab_clientes(self):
        frame_form = ttk.LabelFrame(
            self.tab_clientes,
            text="Formulario de cliente"
        )
        frame_form.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_form, text="Nombre").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Correo").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Teléfono").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(frame_form, text="Ciudad").grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.entry_cliente_nombre = ttk.Entry(frame_form, width=25)
        self.entry_cliente_correo = ttk.Entry(frame_form, width=25)
        self.entry_cliente_telefono = ttk.Entry(frame_form, width=20)
        self.entry_cliente_ciudad = ttk.Entry(frame_form, width=20)

        self.entry_cliente_nombre.grid(row=1, column=0, padx=5, pady=5)
        self.entry_cliente_correo.grid(row=1, column=1, padx=5, pady=5)
        self.entry_cliente_telefono.grid(row=1, column=2, padx=5, pady=5)
        self.entry_cliente_ciudad.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Crear cliente",
            command=self.crear_cliente
        ).grid(row=1, column=4, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Limpiar",
            command=self.limpiar_formulario_cliente
        ).grid(row=1, column=5, padx=5, pady=5)

        ttk.Button(
            frame_form,
            text="Refrescar",
            command=self.cargar_clientes
        ).grid(row=1, column=6, padx=5, pady=5)

        frame_tabla = ttk.LabelFrame(
            self.tab_clientes,
            text="Clientes registrados"
        )
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("id_cliente", "nombre", "correo", "telefono", "ciudad", "activo")

        self.tree_clientes = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            self.tree_clientes.heading(columna, text=columna.upper())
            self.tree_clientes.column(columna, width=150)

        self.tree_clientes.pack(fill="both", expand=True)

    def cargar_clientes(self):
        clientes = self.api.listar_clientes(solo_activos=False)

        self.limpiar_treeview(self.tree_clientes)

        for cliente in clientes:
            activo = "Sí" if cliente.get("activo") == 1 else "No"

            self.tree_clientes.insert(
                "",
                "end",
                values=(
                    cliente.get("id_cliente"),
                    cliente.get("nombre"),
                    cliente.get("correo"),
                    cliente.get("telefono"),
                    cliente.get("ciudad"),
                    activo
                )
            )

    def crear_cliente(self):
        nombre = self.entry_cliente_nombre.get().strip()
        correo = self.entry_cliente_correo.get().strip()
        telefono = self.entry_cliente_telefono.get().strip()
        ciudad = self.entry_cliente_ciudad.get().strip()

        if not nombre or not correo:
            messagebox.showwarning(
                "Datos incompletos",
                "Nombre y correo son obligatorios."
            )
            return

        cliente = {
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono if telefono else None,
            "ciudad": ciudad if ciudad else "No especificada"
        }

        resultado = self.api.crear_cliente(cliente)

        if resultado:
            messagebox.showinfo(
                "Cliente creado",
                "El cliente fue registrado correctamente."
            )
            self.limpiar_formulario_cliente()
            self.cargar_clientes()

    def limpiar_formulario_cliente(self):
        self.entry_cliente_nombre.delete(0, tk.END)
        self.entry_cliente_correo.delete(0, tk.END)
        self.entry_cliente_telefono.delete(0, tk.END)
        self.entry_cliente_ciudad.delete(0, tk.END)


    # ---------------------------------------------------------
    # PESTAÑA REPORTES
    # ---------------------------------------------------------

    def crear_tab_reportes(self):
        frame_controles = ttk.LabelFrame(
            self.tab_reportes,
            text="Generación de reportes"
        )
        frame_controles.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_controles, text="Tipo de reporte").grid(row=0, column=0, padx=5, pady=5)

        self.combo_reporte = ttk.Combobox(
            frame_controles,
            width=35,
            state="readonly",
            values=[
                "Productos con bajo stock",
                "Valor de inventario",
                "Ventas por cliente",
                "Ventas por día",
                "Resumen general"
            ]
        )

        self.combo_reporte.grid(row=0, column=1, padx=5, pady=5)
        self.combo_reporte.current(0)

        ttk.Label(frame_controles, text="Umbral bajo stock").grid(row=0, column=2, padx=5, pady=5)

        self.entry_umbral_stock = ttk.Entry(frame_controles, width=10)
        self.entry_umbral_stock.insert(0, "5")
        self.entry_umbral_stock.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(
            frame_controles,
            text="Generar reporte",
            command=self.generar_reporte
        ).grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(
            frame_controles,
            text="Exportar CSV",
            command=self.exportar_reporte_csv
        ).grid(row=0, column=5, padx=5, pady=5)

        frame_tabla = ttk.LabelFrame(
            self.tab_reportes,
            text="Tabla del reporte"
        )
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_reporte = ttk.Treeview(
            frame_tabla,
            show="headings"
        )

        self.tree_reporte.pack(fill="both", expand=True)

        frame_grafica = ttk.LabelFrame(
            self.tab_reportes,
            text="Gráfica"
        )
        frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_grafica = frame_grafica


    def obtener_df_productos(self):
        productos = self.api.listar_productos(solo_activos=False)
        df = pd.DataFrame(productos)

        if df.empty:
            return df

        df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
        df["stock"] = pd.to_numeric(df["stock"], errors="coerce")
        df["activo"] = pd.to_numeric(df["activo"], errors="coerce")

        return df

    def obtener_df_clientes(self):
        clientes = self.api.listar_clientes(solo_activos=False)
        df = pd.DataFrame(clientes)

        if df.empty:
            return df

        df["activo"] = pd.to_numeric(df["activo"], errors="coerce")

        return df

    def obtener_df_ventas(self):
        ventas = self.api.listar_ventas()
        df = pd.DataFrame(ventas)

        if df.empty:
            return df

        df["total"] = pd.to_numeric(df["total"], errors="coerce")
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

        return df


    def generar_productos_bajo_stock(self):
        df = self.obtener_df_productos()

        if df.empty:
            return df

        try:
            umbral = int(self.entry_umbral_stock.get().strip())
        except ValueError:
            messagebox.showerror(
                "Umbral inválido",
                "El umbral de bajo stock debe ser un número entero."
            )
            return pd.DataFrame()

        reporte = df[
            (df["activo"] == 1) &
            (df["stock"] <= umbral)
        ].copy()

        reporte = reporte[
            ["sku", "nombre", "categoria", "precio", "stock", "activo"]
        ].sort_values("stock", ascending=True)

        return reporte

    def generar_valor_inventario(self):
        df = self.obtener_df_productos()

        if df.empty:
            return df

        activos = df[df["activo"] == 1].copy()

        activos["valor_inventario"] = activos["precio"] * activos["stock"]

        reporte = activos[
            ["sku", "nombre", "categoria", "precio", "stock", "valor_inventario"]
        ].sort_values("valor_inventario", ascending=False)

        return reporte

    def generar_ventas_por_cliente(self):
        df = self.obtener_df_ventas()

        if df.empty:
            return df

        ventas_activas = df[df["estado"] == "ACTIVA"].copy()

        reporte = (
            ventas_activas
            .groupby("cliente", as_index=False)
            .agg(
                cantidad_ventas=("id_venta", "count"),
                total_comprado=("total", "sum")
            )
            .sort_values("total_comprado", ascending=False)
        )

        return reporte

    def generar_ventas_por_dia(self):
        df = self.obtener_df_ventas()

        if df.empty:
            return df

        ventas_activas = df[df["estado"] == "ACTIVA"].copy()
        ventas_activas["dia"] = ventas_activas["fecha"].dt.date

        reporte = (
            ventas_activas
            .groupby("dia", as_index=False)
            .agg(
                cantidad_ventas=("id_venta", "count"),
                total_vendido=("total", "sum")
            )
            .sort_values("dia")
        )

        return reporte

    def generar_resumen_general(self):
        productos = self.obtener_df_productos()
        clientes = self.obtener_df_clientes()
        ventas = self.obtener_df_ventas()

        if productos.empty:
            productos_activos = 0
            valor_inventario = 0
        else:
            productos_activos_df = productos[productos["activo"] == 1]
            productos_activos = len(productos_activos_df)
            valor_inventario = (
                productos_activos_df["precio"] * productos_activos_df["stock"]
            ).sum()

        if clientes.empty:
            clientes_activos = 0
        else:
            clientes_activos = len(clientes[clientes["activo"] == 1])

        if ventas.empty:
            ventas_activas = 0
            ingresos_totales = 0
        else:
            ventas_activas_df = ventas[ventas["estado"] == "ACTIVA"]
            ventas_activas = len(ventas_activas_df)
            ingresos_totales = ventas_activas_df["total"].sum()

        resumen = {
            "productos_activos": productos_activos,
            "clientes_activos": clientes_activos,
            "ventas_activas": ventas_activas,
            "ingresos_totales": ingresos_totales,
            "valor_inventario": valor_inventario
        }

        return pd.DataFrame([resumen])


    def mostrar_dataframe_en_treeview(self, df):
        self.limpiar_treeview(self.tree_reporte)

        self.tree_reporte["columns"] = list(df.columns)

        for columna in df.columns:
            self.tree_reporte.heading(columna, text=columna.upper())
            self.tree_reporte.column(columna, width=150)

        for _, fila in df.iterrows():
            valores = []

            for valor in fila:
                if pd.isna(valor):
                    valores.append("")
                elif isinstance(valor, float):
                    valores.append(round(valor, 2))
                else:
                    valores.append(valor)

            self.tree_reporte.insert("", "end", values=valores)

    def generar_reporte(self):
        tipo = self.combo_reporte.get()

        if tipo == "Productos con bajo stock":
            df = self.generar_productos_bajo_stock()

        elif tipo == "Valor de inventario":
            df = self.generar_valor_inventario()

        elif tipo == "Ventas por cliente":
            df = self.generar_ventas_por_cliente()

        elif tipo == "Ventas por día":
            df = self.generar_ventas_por_dia()

        elif tipo == "Resumen general":
            df = self.generar_resumen_general()

        else:
            messagebox.showwarning(
                "Reporte no válido",
                "Selecciona un tipo de reporte."
            )
            return

        self.df_reporte_actual = df

        if df.empty:
            messagebox.showinfo(
                "Sin datos",
                "El reporte no contiene datos para mostrar."
            )
            self.mostrar_dataframe_en_treeview(pd.DataFrame())
            self.limpiar_grafica()
            return

        self.mostrar_dataframe_en_treeview(df)
        self.graficar_reporte(tipo, df)


    def limpiar_grafica(self):
        if self.canvas_grafica is not None:
            self.canvas_grafica.get_tk_widget().destroy()
            self.canvas_grafica = None

    def graficar_reporte(self, tipo, df):
        self.limpiar_grafica()

        figura = Figure(figsize=(8, 4), dpi=100)
        ax = figura.add_subplot(111)

        if tipo == "Productos con bajo stock":
            if "nombre" in df.columns and "stock" in df.columns:
                ax.bar(df["nombre"], df["stock"])
                ax.set_title("Productos con bajo stock")
                ax.set_xlabel("Producto")
                ax.set_ylabel("Stock")

        elif tipo == "Valor de inventario":
            if "nombre" in df.columns and "valor_inventario" in df.columns:
                ax.bar(df["nombre"], df["valor_inventario"])
                ax.set_title("Valor de inventario por producto")
                ax.set_xlabel("Producto")
                ax.set_ylabel("Valor de inventario")

        elif tipo == "Ventas por cliente":
            if "cliente" in df.columns and "total_comprado" in df.columns:
                ax.bar(df["cliente"], df["total_comprado"])
                ax.set_title("Ventas por cliente")
                ax.set_xlabel("Cliente")
                ax.set_ylabel("Total comprado")

        elif tipo == "Ventas por día":
            if "dia" in df.columns and "total_vendido" in df.columns:
                ax.plot(df["dia"].astype(str), df["total_vendido"], marker="o")
                ax.set_title("Ventas por día")
                ax.set_xlabel("Día")
                ax.set_ylabel("Total vendido")

        elif tipo == "Resumen general":
            columnas_numericas = [
                col for col in df.columns
                if pd.api.types.is_numeric_dtype(df[col])
            ]

            valores = [df[col].iloc[0] for col in columnas_numericas]

            ax.bar(columnas_numericas, valores)
            ax.set_title("Resumen general")
            ax.set_xlabel("Indicador")
            ax.set_ylabel("Valor")

        ax.tick_params(axis="x", rotation=45)
        figura.tight_layout()

        self.canvas_grafica = FigureCanvasTkAgg(
            figura,
            master=self.frame_grafica
        )

        self.canvas_grafica.draw()
        self.canvas_grafica.get_tk_widget().pack(fill="both", expand=True)


    def exportar_reporte_csv(self):
        if self.df_reporte_actual.empty:
            messagebox.showwarning(
                "Sin reporte",
                "Primero genera un reporte antes de exportar."
            )
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte CSV",
            defaultextension=".csv",
            filetypes=[
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        self.df_reporte_actual.to_csv(
            ruta,
            index=False,
            encoding="utf-8-sig"
        )

        messagebox.showinfo(
            "Reporte exportado",
            f"El reporte fue guardado correctamente en:\n{ruta}"
        )



def main():
    root = tk.Tk()
    app = SistemaVentasGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
