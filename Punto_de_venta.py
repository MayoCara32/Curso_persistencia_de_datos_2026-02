from pathlib import Path
import sqlite3
from datetime import datetime


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

CARPETA_DATOS = Path("datos_punto_venta")
CARPETA_DATOS.mkdir(exist_ok=True)

RUTA_DB = CARPETA_DATOS / "punto_venta.db"


# ============================================================
# CONEXIÓN SEGURA A SQLITE
# ============================================================

def obtener_conexion():
    """
    Crea una conexión con SQLite.

    Buenas prácticas:
    - Activa llaves foráneas con PRAGMA foreign_keys = ON.
    - Usa row_factory para leer resultados por nombre de columna.
    """
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion


# ============================================================
# CREACIÓN DE TABLAS
# ============================================================

def crear_tablas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        telefono TEXT,
        ciudad TEXT DEFAULT 'No especificada'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio REAL NOT NULL CHECK(precio > 0),
        stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
        activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        total REAL NOT NULL DEFAULT 0 CHECK(total >= 0),

        FOREIGN KEY (id_cliente)
            REFERENCES clientes(id_cliente)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        cantidad INTEGER NOT NULL CHECK(cantidad > 0),
        precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
        subtotal REAL NOT NULL CHECK(subtotal >= 0),

        FOREIGN KEY (id_venta)
            REFERENCES ventas(id_venta)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,

        FOREIGN KEY (id_producto)
            REFERENCES productos(id_producto)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    )
    """)

    conexion.commit()
    conexion.close()


# ============================================================
# DATOS INICIALES
# ============================================================

def insertar_datos_iniciales():
    """
    Inserta datos de prueba.

    Se usa INSERT OR IGNORE para evitar duplicados si el programa
    se ejecuta varias veces.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    clientes = [
        ("Ana López", "ana@example.com", "555-111-2222", "CDMX"),
        ("Carlos Pérez", "carlos@example.com", "555-333-4444", "Guadalajara"),
        ("María Torres", "maria@example.com", None, "Monterrey")
    ]

    productos = [
        ("P001", "Mouse inalámbrico", "Accesorios", 249.90, 15, 1),
        ("P002", "Teclado mecánico", "Accesorios", 899.00, 8, 1),
        ("P003", "Monitor 24 pulgadas", "Pantallas", 3299.00, 4, 1),
        ("P004", "Cable HDMI", "Cables", 120.00, 20, 1),
        ("P005", "Memoria USB 64GB", "Almacenamiento", 150.00, 30, 1),
        ("P006", "Bocinas Bluetooth", "Audio", 699.00, 10, 1),
        ("P007", "Producto sin stock", "General", 100.00, 0, 1)
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO clientes (nombre, correo, telefono, ciudad)
    VALUES (?, ?, ?, ?)
    """, clientes)

    cursor.executemany("""
    INSERT OR IGNORE INTO productos (sku, nombre, categoria, precio, stock, activo)
    VALUES (?, ?, ?, ?, ?, ?)
    """, productos)

    conexion.commit()
    conexion.close()


# ============================================================
# UTILIDADES DE IMPRESIÓN
# ============================================================

def formatear_dinero(valor):
    return f"${valor:,.2f}"


def imprimir_tabla(filas, titulo=None):
    """
    Imprime una lista de sqlite3.Row como tabla simple en terminal.
    """
    if titulo:
        print("\n" + titulo)
        print("-" * len(titulo))

    if not filas:
        print("Sin registros.")
        return

    columnas = filas[0].keys()

    anchos = {}
    for columna in columnas:
        max_dato = max(len(str(fila[columna])) if fila[columna] is not None else 4 for fila in filas)
        anchos[columna] = max(len(columna), max_dato)

    encabezado = " | ".join(columna.ljust(anchos[columna]) for columna in columnas)
    separador = "-+-".join("-" * anchos[columna] for columna in columnas)

    print(encabezado)
    print(separador)

    for fila in filas:
        valores = []
        for columna in columnas:
            valor = fila[columna]
            if valor is None:
                valor = "NULL"
            valores.append(str(valor).ljust(anchos[columna]))
        print(" | ".join(valores))


def pausar():
    input("\nPresiona Enter para continuar...")


# ============================================================
# VALIDACIÓN DE ENTRADAS DEL USUARIO
# ============================================================

def pedir_texto(mensaje, obligatorio=True):
    while True:
        valor = input(mensaje).strip()

        if obligatorio and valor == "":
            print("Este campo no puede quedar vacío.")
            continue

        return valor


def pedir_entero(mensaje, minimo=None, maximo=None):
    while True:
        valor = input(mensaje).strip()

        try:
            numero = int(valor)

            if minimo is not None and numero < minimo:
                print(f"El número debe ser mayor o igual a {minimo}.")
                continue

            if maximo is not None and numero > maximo:
                print(f"El número debe ser menor o igual a {maximo}.")
                continue

            return numero

        except ValueError:
            print("Entrada inválida. Debes escribir un número entero.")


def confirmar(mensaje):
    while True:
        respuesta = input(mensaje + " (s/n): ").strip().lower()

        if respuesta in ["s", "si", "sí"]:
            return True

        if respuesta in ["n", "no"]:
            return False

        print("Respuesta inválida. Escribe s o n.")


# ============================================================
# CONSULTAS DE PRODUCTOS
# ============================================================

def listar_productos_activos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        id_producto,
        sku,
        nombre,
        categoria,
        precio,
        stock
    FROM productos
    WHERE activo = 1
    ORDER BY nombre
    """)

    productos = cursor.fetchall()
    conexion.close()

    imprimir_tabla(productos, "Productos activos")


def buscar_producto_por_sku(sku):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        id_producto,
        sku,
        nombre,
        categoria,
        precio,
        stock,
        activo
    FROM productos
    WHERE sku = ?
    """, (sku,))

    producto = cursor.fetchone()
    conexion.close()

    return producto


def consultar_producto_interactivo():
    sku = pedir_texto("SKU del producto: ").upper()
    producto = buscar_producto_por_sku(sku)

    if producto is None:
        print("No existe un producto con ese SKU.")
        return

    imprimir_tabla([producto], "Producto encontrado")


# ============================================================
# CONSULTAS Y REGISTRO DE CLIENTES
# ============================================================

def listar_clientes():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        id_cliente,
        nombre,
        correo,
        telefono,
        ciudad
    FROM clientes
    ORDER BY id_cliente
    """)

    clientes = cursor.fetchall()
    conexion.close()

    imprimir_tabla(clientes, "Clientes registrados")


def obtener_cliente_por_id(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        id_cliente,
        nombre,
        correo
    FROM clientes
    WHERE id_cliente = ?
    """, (id_cliente,))

    cliente = cursor.fetchone()
    conexion.close()

    return cliente


def registrar_cliente():
    print("\nRegistro de cliente")
    print("-------------------")

    nombre = pedir_texto("Nombre: ")
    correo = pedir_texto("Correo: ")
    telefono = pedir_texto("Teléfono, opcional: ", obligatorio=False)
    ciudad = pedir_texto("Ciudad, opcional: ", obligatorio=False)

    if telefono == "":
        telefono = None

    if ciudad == "":
        ciudad = "No especificada"

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
        INSERT INTO clientes (nombre, correo, telefono, ciudad)
        VALUES (?, ?, ?, ?)
        """, (nombre, correo, telefono, ciudad))

        conexion.commit()

        id_cliente = cursor.lastrowid
        print(f"Cliente registrado correctamente. ID: {id_cliente}")

        return id_cliente

    except sqlite3.IntegrityError as error:
        conexion.rollback()
        print("No se pudo registrar el cliente.")
        print("Motivo:", error)
        return None

    finally:
        conexion.close()


def seleccionar_cliente():
    listar_clientes()

    while True:
        id_cliente = pedir_entero("Escribe el ID del cliente: ", minimo=1)
        cliente = obtener_cliente_por_id(id_cliente)

        if cliente is None:
            print("No existe un cliente con ese ID.")
            continue

        print(f"Cliente seleccionado: {cliente['nombre']} - {cliente['correo']}")
        return id_cliente


# ============================================================
# CARRITO DE COMPRA
# ============================================================

def mostrar_carrito(carrito):
    if not carrito:
        print("El carrito está vacío.")
        return

    print("\nCarrito actual")
    print("--------------")

    total = 0

    for index, item in enumerate(carrito, start=1):
        subtotal = item["cantidad"] * item["precio"]
        total += subtotal

        print(
            f"{index}. {item['sku']} | {item['nombre']} | "
            f"Cantidad: {item['cantidad']} | "
            f"Precio: {formatear_dinero(item['precio'])} | "
            f"Subtotal: {formatear_dinero(subtotal)}"
        )

    print(f"\nTotal actual: {formatear_dinero(total)}")


def agregar_producto_al_carrito(carrito):
    print("\nAgregar producto al carrito")
    print("---------------------------")

    listar_productos_activos()

    sku = pedir_texto("\nSKU del producto: ").upper()
    producto = buscar_producto_por_sku(sku)

    if producto is None:
        print("No existe un producto con ese SKU.")
        return carrito

    if producto["activo"] != 1:
        print("El producto no está activo.")
        return carrito

    if producto["stock"] <= 0:
        print("El producto no tiene stock disponible.")
        return carrito

    cantidad = pedir_entero("Cantidad a vender: ", minimo=1)

    cantidad_actual_en_carrito = 0

    for item in carrito:
        if item["id_producto"] == producto["id_producto"]:
            cantidad_actual_en_carrito = item["cantidad"]
            break

    nueva_cantidad_total = cantidad_actual_en_carrito + cantidad

    if nueva_cantidad_total > producto["stock"]:
        print(f"No hay stock suficiente. Stock disponible: {producto['stock']}")
        print(f"Cantidad ya en carrito: {cantidad_actual_en_carrito}")
        return carrito

    for item in carrito:
        if item["id_producto"] == producto["id_producto"]:
            item["cantidad"] = nueva_cantidad_total
            print("Cantidad actualizada en el carrito.")
            return carrito

    carrito.append({
        "id_producto": producto["id_producto"],
        "sku": producto["sku"],
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": cantidad
    })

    print("Producto agregado al carrito.")
    return carrito


def quitar_producto_del_carrito(carrito):
    if not carrito:
        print("El carrito está vacío.")
        return carrito

    mostrar_carrito(carrito)

    indice = pedir_entero("Número de producto a quitar: ", minimo=1, maximo=len(carrito))
    producto_quitado = carrito.pop(indice - 1)

    print(f"Producto quitado: {producto_quitado['nombre']}")
    return carrito


# ============================================================
# REGISTRO SEGURO DE VENTA
# ============================================================

def registrar_venta_en_bd(id_cliente, carrito):
    """
    Registra una venta completa.

    Buenas prácticas aplicadas:
    - Usa consultas parametrizadas.
    - Usa transacción.
    - Valida stock justo antes de vender.
    - Usa rollback si algo falla.
    - Usa FOREIGN KEY para proteger relaciones.
    - Actualiza stock con WHERE seguro.
    """
    if not carrito:
        print("No se puede registrar una venta sin productos.")
        return None

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN")

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO ventas (id_cliente, fecha, total)
        VALUES (?, ?, ?)
        """, (id_cliente, fecha, 0))

        id_venta = cursor.lastrowid
        total_venta = 0

        for item in carrito:
            id_producto = item["id_producto"]
            cantidad = item["cantidad"]

            cursor.execute("""
            SELECT
                precio,
                stock,
                activo
            FROM productos
            WHERE id_producto = ?
            """, (id_producto,))

            producto = cursor.fetchone()

            if producto is None:
                raise ValueError(f"El producto con ID {id_producto} ya no existe.")

            if producto["activo"] != 1:
                raise ValueError(f"El producto con ID {id_producto} ya no está activo.")

            if producto["stock"] < cantidad:
                raise ValueError(
                    f"Stock insuficiente para producto ID {id_producto}. "
                    f"Disponible: {producto['stock']}, solicitado: {cantidad}."
                )

            precio_actual = producto["precio"]
            subtotal = precio_actual * cantidad
            total_venta += subtotal

            cursor.execute("""
            INSERT INTO detalle_ventas (
                id_venta,
                id_producto,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
            """, (id_venta, id_producto, cantidad, precio_actual, subtotal))

            cursor.execute("""
            UPDATE productos
            SET stock = stock - ?
            WHERE id_producto = ?
              AND stock >= ?
              AND activo = 1
            """, (cantidad, id_producto, cantidad))

            if cursor.rowcount == 0:
                raise ValueError(f"No se pudo actualizar el stock del producto ID {id_producto}.")

        cursor.execute("""
        UPDATE ventas
        SET total = ?
        WHERE id_venta = ?
        """, (total_venta, id_venta))

        conexion.commit()

        print("\nVenta registrada correctamente.")
        print(f"ID venta: {id_venta}")
        print(f"Total: {formatear_dinero(total_venta)}")

        return id_venta

    except Exception as error:
        conexion.rollback()
        print("\nNo se pudo registrar la venta.")
        print("Se deshicieron todos los cambios.")
        print("Motivo:", error)
        return None

    finally:
        conexion.close()


# ============================================================
# TICKET Y REPORTES CON JOIN
# ============================================================

def consultar_ticket(id_venta):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        v.id_venta,
        v.fecha,
        c.nombre AS cliente,
        c.correo,
        p.sku,
        p.nombre AS producto,
        dv.cantidad,
        dv.precio_unitario,
        dv.subtotal,
        v.total AS total_venta
    FROM ventas v
    INNER JOIN clientes c
        ON v.id_cliente = c.id_cliente
    INNER JOIN detalle_ventas dv
        ON v.id_venta = dv.id_venta
    INNER JOIN productos p
        ON dv.id_producto = p.id_producto
    WHERE v.id_venta = ?
    ORDER BY dv.id_detalle
    """, (id_venta,))

    filas = cursor.fetchall()
    conexion.close()

    if not filas:
        print("No existe una venta con ese ID.")
        return

    print("\nTICKET DE VENTA")
    print("---------------")
    print(f"Venta: {filas[0]['id_venta']}")
    print(f"Fecha: {filas[0]['fecha']}")
    print(f"Cliente: {filas[0]['cliente']}")
    print(f"Correo: {filas[0]['correo']}")
    print()

    for fila in filas:
        print(
            f"{fila['sku']} | {fila['producto']} | "
            f"Cantidad: {fila['cantidad']} | "
            f"Precio: {formatear_dinero(fila['precio_unitario'])} | "
            f"Subtotal: {formatear_dinero(fila['subtotal'])}"
        )

    print("\nTotal:", formatear_dinero(filas[0]["total_venta"]))


def mostrar_reporte_completo_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        v.id_venta,
        v.fecha,
        c.nombre AS cliente,
        p.sku,
        p.nombre AS producto,
        dv.cantidad,
        dv.precio_unitario,
        dv.subtotal,
        v.total AS total_venta
    FROM ventas v
    INNER JOIN clientes c
        ON v.id_cliente = c.id_cliente
    INNER JOIN detalle_ventas dv
        ON v.id_venta = dv.id_venta
    INNER JOIN productos p
        ON dv.id_producto = p.id_producto
    ORDER BY v.id_venta, dv.id_detalle
    """)

    ventas = cursor.fetchall()
    conexion.close()

    imprimir_tabla(ventas, "Reporte completo de ventas")


def mostrar_reporte_total_por_cliente():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        c.id_cliente,
        c.nombre AS cliente,
        COUNT(v.id_venta) AS cantidad_ventas,
        COALESCE(SUM(v.total), 0) AS total_comprado
    FROM clientes c
    LEFT JOIN ventas v
        ON c.id_cliente = v.id_cliente
    GROUP BY c.id_cliente, c.nombre
    ORDER BY total_comprado DESC
    """)

    reporte = cursor.fetchall()
    conexion.close()

    imprimir_tabla(reporte, "Total comprado por cliente")


def mostrar_productos_sin_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        p.id_producto,
        p.sku,
        p.nombre,
        p.stock
    FROM productos p
    LEFT JOIN detalle_ventas dv
        ON p.id_producto = dv.id_producto
    WHERE dv.id_detalle IS NULL
    ORDER BY p.id_producto
    """)

    productos = cursor.fetchall()
    conexion.close()

    imprimir_tabla(productos, "Productos sin ventas")


# ============================================================
# PROCESO DE VENTA INTERACTIVO
# ============================================================

def crear_venta_interactiva():
    print("\nNUEVA VENTA")
    print("-----------")

    print("\nSelecciona una opción:")
    print("1. Usar cliente existente")
    print("2. Registrar cliente nuevo")

    opcion_cliente = pedir_entero("Opción: ", minimo=1, maximo=2)

    if opcion_cliente == 1:
        id_cliente = seleccionar_cliente()
    else:
        id_cliente = registrar_cliente()

        if id_cliente is None:
            print("No se puede continuar sin cliente.")
            return

    carrito = []

    while True:
        print("\nMENÚ DEL CARRITO")
        print("----------------")
        mostrar_carrito(carrito)

        print("\nOpciones:")
        print("1. Agregar producto")
        print("2. Quitar producto")
        print("3. Confirmar venta")
        print("4. Cancelar venta")

        opcion = pedir_entero("Opción: ", minimo=1, maximo=4)

        if opcion == 1:
            carrito = agregar_producto_al_carrito(carrito)

        elif opcion == 2:
            carrito = quitar_producto_del_carrito(carrito)

        elif opcion == 3:
            if not carrito:
                print("No puedes confirmar una venta sin productos.")
                continue

            mostrar_carrito(carrito)

            if confirmar("¿Confirmar venta?"):
                id_venta = registrar_venta_en_bd(id_cliente, carrito)

                if id_venta is not None:
                    consultar_ticket(id_venta)

                return

        elif opcion == 4:
            print("Venta cancelada. No se guardó nada.")
            return


# ============================================================
# VALIDACIÓN DE RELACIONES
# ============================================================

def mostrar_relaciones():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    print("\nEstado de llaves foráneas")
    print("-------------------------")

    cursor.execute("PRAGMA foreign_keys")
    estado = cursor.fetchone()[0]
    print(f"foreign_keys = {estado}")

    print("\nLlaves foráneas de ventas")
    cursor.execute("PRAGMA foreign_key_list(ventas)")
    imprimir_tabla(cursor.fetchall())

    print("\nLlaves foráneas de detalle_ventas")
    cursor.execute("PRAGMA foreign_key_list(detalle_ventas)")
    imprimir_tabla(cursor.fetchall())

    print("\nValidación PRAGMA foreign_key_check")
    cursor.execute("PRAGMA foreign_key_check")
    errores = cursor.fetchall()

    if not errores:
        print("No hay errores de integridad referencial.")
    else:
        imprimir_tabla(errores)

    conexion.close()


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

def menu_punto_venta():
    while True:
        print("\nPUNTO DE VENTA")
        print("==============")
        print("1. Ver productos disponibles")
        print("2. Buscar producto por SKU")
        print("3. Ver clientes")
        print("4. Registrar cliente")
        print("5. Crear venta")
        print("6. Consultar ticket")
        print("7. Reporte completo de ventas")
        print("8. Total comprado por cliente")
        print("9. Productos sin ventas")
        print("10. Ver relaciones y validación de llaves foráneas")
        print("11. Salir")

        opcion = pedir_entero("Selecciona una opción: ", minimo=1, maximo=11)

        if opcion == 1:
            listar_productos_activos()
            pausar()

        elif opcion == 2:
            consultar_producto_interactivo()
            pausar()

        elif opcion == 3:
            listar_clientes()
            pausar()

        elif opcion == 4:
            registrar_cliente()
            pausar()

        elif opcion == 5:
            crear_venta_interactiva()
            pausar()

        elif opcion == 6:
            id_venta = pedir_entero("ID de venta: ", minimo=1)
            consultar_ticket(id_venta)
            pausar()

        elif opcion == 7:
            mostrar_reporte_completo_ventas()
            pausar()

        elif opcion == 8:
            mostrar_reporte_total_por_cliente()
            pausar()

        elif opcion == 9:
            mostrar_productos_sin_ventas()
            pausar()

        elif opcion == 10:
            mostrar_relaciones()
            pausar()

        elif opcion == 11:
            print("Saliendo del punto de venta.")
            break


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

def main():
    print("Inicializando punto de venta...")
    print(f"Base de datos: {RUTA_DB.resolve()}")

    crear_tablas()
    insertar_datos_iniciales()

    menu_punto_venta()


if __name__ == "__main__":
    main()