
import sqlite3
from datetime import datetime

from database import (
    consultar_todos,
    consultar_uno,
    ejecutar,
    ejecutar_varios,
    ejecutar_script,
    ejecutar_transaccion
)


SQL_CREAR_TABLAS = """
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    telefono TEXT,
    ciudad TEXT DEFAULT 'No especificada',
    activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL CHECK(precio > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
    activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS ventas (
    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    total REAL NOT NULL DEFAULT 0 CHECK(total >= 0),
    estado TEXT NOT NULL DEFAULT 'ACTIVA' CHECK(estado IN ('ACTIVA', 'CANCELADA')),

    FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

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
);
"""



CLIENTES_INICIALES = [
    ("Ana López", "ana@example.com", "555-111-2222", "CDMX"),
    ("Carlos Pérez", "carlos@example.com", "555-333-4444", "Guadalajara"),
    ("María Torres", "maria@example.com", None, "Monterrey"),
    ("Luis Romero", "luis@example.com", "555-888-9999", "Puebla")
]


PRODUCTOS_INICIALES = [
    ("P001", "Mouse inalámbrico", "Accesorios", 249.90, 15),
    ("P002", "Teclado mecánico", "Accesorios", 899.00, 8),
    ("P003", "Monitor 24 pulgadas", "Pantallas", 3299.00, 4),
    ("P004", "Cable HDMI", "Cables", 120.00, 20),
    ("P005", "Memoria USB 64GB", "Almacenamiento", 150.00, 30),
    ("P006", "Bocinas Bluetooth", "Audio", 699.00, 10)
]



def limpiar_texto(valor):
    if valor is None:
        return ""

    return str(valor).strip()


def normalizar_sku(sku):
    return limpiar_texto(sku).upper()


def normalizar_correo(correo):
    return limpiar_texto(correo).lower()


def validar_texto_obligatorio(valor, nombre_campo):
    valor_limpio = limpiar_texto(valor)

    if valor_limpio == "":
        raise ValueError(f"El campo {nombre_campo} no puede estar vacío.")

    return valor_limpio


def validar_precio(precio):
    try:
        precio = float(precio)
    except (TypeError, ValueError):
        raise ValueError("El precio debe ser numérico.")

    if precio <= 0:
        raise ValueError("El precio debe ser mayor que cero.")

    return precio


def validar_stock(stock):
    try:
        stock = int(stock)
    except (TypeError, ValueError):
        raise ValueError("El stock debe ser un número entero.")

    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")

    return stock


def validar_cantidad(cantidad):
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("La cantidad debe ser un número entero.")

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    return cantidad



def inicializar_base_datos():
    """
    Crea las tablas e inserta datos iniciales si no existen.
    """
    ejecutar_script(SQL_CREAR_TABLAS)

    ejecutar_varios("""
    INSERT OR IGNORE INTO clientes (nombre, correo, telefono, ciudad, activo)
    VALUES (?, ?, ?, ?, 1)
    """, CLIENTES_INICIALES)

    ejecutar_varios("""
    INSERT OR IGNORE INTO productos (sku, nombre, categoria, precio, stock, activo)
    VALUES (?, ?, ?, ?, ?, 1)
    """, PRODUCTOS_INICIALES)

    return {
        "ok": True,
        "mensaje": "Base de datos inicializada correctamente."
    }



def listar_productos(solo_activos=True):
    if solo_activos:
        return consultar_todos("""
        SELECT
            id_producto,
            sku,
            nombre,
            categoria,
            precio,
            stock,
            activo
        FROM productos
        WHERE activo = 1
        ORDER BY nombre
        """)

    return consultar_todos("""
    SELECT
        id_producto,
        sku,
        nombre,
        categoria,
        precio,
        stock,
        activo
    FROM productos
    ORDER BY nombre
    """)


def buscar_producto_por_sku(sku):
    sku = normalizar_sku(sku)

    return consultar_uno("""
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



def registrar_producto(sku, nombre, categoria, precio, stock):
    try:
        sku = normalizar_sku(sku)
        nombre = validar_texto_obligatorio(nombre, "nombre")
        categoria = validar_texto_obligatorio(categoria, "categoría")
        precio = validar_precio(precio)
        stock = validar_stock(stock)

        resultado = ejecutar("""
        INSERT INTO productos (sku, nombre, categoria, precio, stock, activo)
        VALUES (?, ?, ?, ?, ?, 1)
        """, (sku, nombre, categoria, precio, stock))

        producto = buscar_producto_por_sku(sku)

        return {
            "ok": True,
            "mensaje": "Producto registrado correctamente.",
            "producto": producto,
            "id_producto": resultado["ultimo_id"]
        }

    except sqlite3.IntegrityError:
        return {
            "ok": False,
            "tipo_error": "conflicto",
            "mensaje": "Ya existe un producto con ese SKU."
        }

    except ValueError as error:
        return {
            "ok": False,
            "tipo_error": "validacion",
            "mensaje": str(error)
        }


def actualizar_producto(sku, datos_actualizar):
    sku = normalizar_sku(sku)

    producto = buscar_producto_por_sku(sku)

    if producto is None:
        return {
            "ok": False,
            "tipo_error": "no_encontrado",
            "mensaje": "Producto no encontrado."
        }

    campos = []
    valores = []

    if "nombre" in datos_actualizar and datos_actualizar["nombre"] is not None:
        nombre = validar_texto_obligatorio(datos_actualizar["nombre"], "nombre")
        campos.append("nombre = ?")
        valores.append(nombre)

    if "categoria" in datos_actualizar and datos_actualizar["categoria"] is not None:
        categoria = validar_texto_obligatorio(datos_actualizar["categoria"], "categoría")
        campos.append("categoria = ?")
        valores.append(categoria)

    if "precio" in datos_actualizar and datos_actualizar["precio"] is not None:
        precio = validar_precio(datos_actualizar["precio"])
        campos.append("precio = ?")
        valores.append(precio)

    if "stock" in datos_actualizar and datos_actualizar["stock"] is not None:
        stock = validar_stock(datos_actualizar["stock"])
        campos.append("stock = ?")
        valores.append(stock)

    if "activo" in datos_actualizar and datos_actualizar["activo"] is not None:
        activo = 1 if datos_actualizar["activo"] else 0
        campos.append("activo = ?")
        valores.append(activo)

    if not campos:
        return {
            "ok": False,
            "tipo_error": "validacion",
            "mensaje": "No se enviaron datos para actualizar."
        }

    valores.append(sku)

    sql = f"""
    UPDATE productos
    SET {", ".join(campos)}
    WHERE sku = ?
    """

    ejecutar(sql, tuple(valores))

    producto_actualizado = buscar_producto_por_sku(sku)

    return {
        "ok": True,
        "mensaje": "Producto actualizado correctamente.",
        "producto": producto_actualizado
    }


def desactivar_producto(sku):
    sku = normalizar_sku(sku)

    producto = buscar_producto_por_sku(sku)

    if producto is None:
        return {
            "ok": False,
            "tipo_error": "no_encontrado",
            "mensaje": "Producto no encontrado."
        }

    if producto["activo"] == 0:
        return {
            "ok": True,
            "mensaje": "El producto ya estaba inactivo.",
            "producto": producto
        }

    ejecutar("""
    UPDATE productos
    SET activo = 0
    WHERE sku = ?
    """, (sku,))

    producto_actualizado = buscar_producto_por_sku(sku)

    return {
        "ok": True,
        "mensaje": "Producto desactivado correctamente.",
        "producto": producto_actualizado
    }



def listar_clientes(solo_activos=True):
    if solo_activos:
        return consultar_todos("""
        SELECT
            id_cliente,
            nombre,
            correo,
            telefono,
            ciudad,
            activo
        FROM clientes
        WHERE activo = 1
        ORDER BY nombre
        """)

    return consultar_todos("""
    SELECT
        id_cliente,
        nombre,
        correo,
        telefono,
        ciudad,
        activo
    FROM clientes
    ORDER BY nombre
    """)


def buscar_cliente_por_id(id_cliente):
    return consultar_uno("""
    SELECT
        id_cliente,
        nombre,
        correo,
        telefono,
        ciudad,
        activo
    FROM clientes
    WHERE id_cliente = ?
    """, (id_cliente,))


def registrar_cliente(nombre, correo, telefono=None, ciudad="No especificada"):
    try:
        nombre = validar_texto_obligatorio(nombre, "nombre")
        correo = normalizar_correo(correo)

        if correo == "":
            raise ValueError("El correo no puede estar vacío.")

        telefono = None if telefono is None else limpiar_texto(telefono)
        ciudad = limpiar_texto(ciudad) or "No especificada"

        resultado = ejecutar("""
        INSERT INTO clientes (nombre, correo, telefono, ciudad, activo)
        VALUES (?, ?, ?, ?, 1)
        """, (nombre, correo, telefono, ciudad))

        cliente = buscar_cliente_por_id(resultado["ultimo_id"])

        return {
            "ok": True,
            "mensaje": "Cliente registrado correctamente.",
            "cliente": cliente,
            "id_cliente": resultado["ultimo_id"]
        }

    except sqlite3.IntegrityError:
        return {
            "ok": False,
            "tipo_error": "conflicto",
            "mensaje": "Ya existe un cliente con ese correo."
        }

    except ValueError as error:
        return {
            "ok": False,
            "tipo_error": "validacion",
            "mensaje": str(error)
        }



def registrar_venta(id_cliente, productos_vendidos):
    """
    Registra una venta completa.

    productos_vendidos:
    [
        {"sku": "P001", "cantidad": 2},
        {"sku": "P002", "cantidad": 1}
    ]
    """

    def operacion(cursor):
        cliente = buscar_cliente_por_id(id_cliente)

        if cliente is None:
            raise ValueError("No existe el cliente indicado.")

        if cliente["activo"] != 1:
            raise ValueError("El cliente está inactivo.")

        if not productos_vendidos:
            raise ValueError("No se puede registrar una venta sin productos.")

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO ventas (id_cliente, fecha, total, estado)
        VALUES (?, ?, 0, 'ACTIVA')
        """, (id_cliente, fecha))

        id_venta = cursor.lastrowid
        total_venta = 0

        for item in productos_vendidos:
            sku = normalizar_sku(item.get("sku"))
            cantidad = validar_cantidad(item.get("cantidad"))

            cursor.execute("""
            SELECT
                id_producto,
                sku,
                nombre,
                precio,
                stock,
                activo
            FROM productos
            WHERE sku = ?
            """, (sku,))

            producto = cursor.fetchone()

            if producto is None:
                raise ValueError(f"No existe el producto con SKU {sku}.")

            if producto["activo"] != 1:
                raise ValueError(f"El producto {sku} está inactivo.")

            if producto["stock"] < cantidad:
                raise ValueError(
                    f"Stock insuficiente para {sku}. "
                    f"Disponible: {producto['stock']}, solicitado: {cantidad}."
                )

            precio_unitario = producto["precio"]
            subtotal = precio_unitario * cantidad
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
            """, (
                id_venta,
                producto["id_producto"],
                cantidad,
                precio_unitario,
                subtotal
            ))

            cursor.execute("""
            UPDATE productos
            SET stock = stock - ?
            WHERE id_producto = ?
              AND stock >= ?
              AND activo = 1
            """, (
                cantidad,
                producto["id_producto"],
                cantidad
            ))

            if cursor.rowcount == 0:
                raise ValueError(f"No se pudo actualizar stock para {sku}.")

        cursor.execute("""
        UPDATE ventas
        SET total = ?
        WHERE id_venta = ?
        """, (total_venta, id_venta))

        return {
            "id_venta": id_venta,
            "total": total_venta
        }

    try:
        resultado = ejecutar_transaccion(operacion)

        return {
            "ok": True,
            "mensaje": "Venta registrada correctamente.",
            "id_venta": resultado["id_venta"],
            "total": resultado["total"]
        }

    except ValueError as error:
        return {
            "ok": False,
            "tipo_error": "validacion",
            "mensaje": str(error)
        }

    except sqlite3.IntegrityError:
        return {
            "ok": False,
            "tipo_error": "base_datos",
            "mensaje": "La venta viola una restricción de la base de datos."
        }



def consultar_ticket(id_venta):
    return consultar_todos("""
    SELECT
        v.id_venta,
        v.fecha,
        v.estado,
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


def listar_ventas():
    return consultar_todos("""
    SELECT
        v.id_venta,
        v.fecha,
        v.estado,
        c.nombre AS cliente,
        v.total
    FROM ventas v
    INNER JOIN clientes c
        ON v.id_cliente = c.id_cliente
    ORDER BY v.id_venta DESC
    """)


def resumen_ventas():
    resumen = consultar_uno("""
    SELECT
        COUNT(*) AS cantidad_ventas,
        COALESCE(SUM(total), 0) AS total_ingresos
    FROM ventas
    WHERE estado = 'ACTIVA'
    """)

    return resumen
