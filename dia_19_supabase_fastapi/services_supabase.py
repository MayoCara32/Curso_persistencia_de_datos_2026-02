
from supabase_client import supabase


def respuesta_ok(mensaje, **datos):
    respuesta = {
        "ok": True,
        "mensaje": mensaje
    }

    respuesta.update(datos)

    return respuesta


def respuesta_error(tipo_error, mensaje):
    return {
        "ok": False,
        "tipo_error": tipo_error,
        "mensaje": mensaje
    }


def limpiar_texto(valor):
    if valor is None:
        return ""

    return str(valor).strip()


def normalizar_sku(sku):
    return limpiar_texto(sku).upper()


def normalizar_correo(correo):
    return limpiar_texto(correo).lower()


def validar_texto_obligatorio(valor, nombre_campo):
    valor = limpiar_texto(valor)

    if valor == "":
        raise ValueError(f"El campo {nombre_campo} no puede estar vacío.")

    return valor


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
        raise ValueError("El stock debe ser entero.")

    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")

    return stock


# ---------------------------------------------------------
# PRODUCTOS
# ---------------------------------------------------------

def listar_productos(solo_activos=True):
    consulta = (
        supabase
        .table("productos")
        .select("*")
        .order("nombre")
    )

    if solo_activos:
        consulta = consulta.eq("activo", True)

    respuesta = consulta.execute()

    return respuesta.data


def buscar_producto_por_sku(sku):
    sku = normalizar_sku(sku)

    respuesta = (
        supabase
        .table("productos")
        .select("*")
        .eq("sku", sku)
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        return None

    return respuesta.data[0]


def registrar_producto(sku, nombre, categoria, precio, stock):
    try:
        sku = normalizar_sku(sku)
        nombre = validar_texto_obligatorio(nombre, "nombre")
        categoria = validar_texto_obligatorio(categoria, "categoría")
        precio = validar_precio(precio)
        stock = validar_stock(stock)

        existente = buscar_producto_por_sku(sku)

        if existente is not None:
            return respuesta_error(
                "conflicto",
                "Ya existe un producto con ese SKU."
            )

        nuevo_producto = {
            "sku": sku,
            "nombre": nombre,
            "categoria": categoria,
            "precio": precio,
            "stock": stock,
            "activo": True
        }

        respuesta = (
            supabase
            .table("productos")
            .insert(nuevo_producto)
            .execute()
        )

        producto = respuesta.data[0] if respuesta.data else nuevo_producto

        return respuesta_ok(
            "Producto registrado correctamente.",
            producto=producto
        )

    except ValueError as error:
        return respuesta_error("validacion", str(error))

    except Exception as error:
        return respuesta_error("base_datos", str(error))


def actualizar_producto(sku, datos_actualizar):
    try:
        sku = normalizar_sku(sku)

        producto = buscar_producto_por_sku(sku)

        if producto is None:
            return respuesta_error(
                "no_encontrado",
                "Producto no encontrado."
            )

        datos = {}

        if "nombre" in datos_actualizar and datos_actualizar["nombre"] is not None:
            datos["nombre"] = validar_texto_obligatorio(
                datos_actualizar["nombre"],
                "nombre"
            )

        if "categoria" in datos_actualizar and datos_actualizar["categoria"] is not None:
            datos["categoria"] = validar_texto_obligatorio(
                datos_actualizar["categoria"],
                "categoría"
            )

        if "precio" in datos_actualizar and datos_actualizar["precio"] is not None:
            datos["precio"] = validar_precio(datos_actualizar["precio"])

        if "stock" in datos_actualizar and datos_actualizar["stock"] is not None:
            datos["stock"] = validar_stock(datos_actualizar["stock"])

        if "activo" in datos_actualizar and datos_actualizar["activo"] is not None:
            datos["activo"] = bool(datos_actualizar["activo"])

        if not datos:
            return respuesta_error(
                "validacion",
                "No se enviaron datos para actualizar."
            )

        respuesta = (
            supabase
            .table("productos")
            .update(datos)
            .eq("sku", sku)
            .execute()
        )

        producto_actualizado = respuesta.data[0] if respuesta.data else buscar_producto_por_sku(sku)

        return respuesta_ok(
            "Producto actualizado correctamente.",
            producto=producto_actualizado
        )

    except ValueError as error:
        return respuesta_error("validacion", str(error))

    except Exception as error:
        return respuesta_error("base_datos", str(error))


def desactivar_producto(sku):
    sku = normalizar_sku(sku)

    producto = buscar_producto_por_sku(sku)

    if producto is None:
        return respuesta_error(
            "no_encontrado",
            "Producto no encontrado."
        )

    respuesta = (
        supabase
        .table("productos")
        .update({"activo": False})
        .eq("sku", sku)
        .execute()
    )

    producto_actualizado = respuesta.data[0] if respuesta.data else buscar_producto_por_sku(sku)

    return respuesta_ok(
        "Producto desactivado correctamente.",
        producto=producto_actualizado
    )


# ---------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------

def listar_clientes(solo_activos=True):
    consulta = (
        supabase
        .table("clientes")
        .select("*")
        .order("nombre")
    )

    if solo_activos:
        consulta = consulta.eq("activo", True)

    respuesta = consulta.execute()

    return respuesta.data


def buscar_cliente_por_id(id_cliente):
    respuesta = (
        supabase
        .table("clientes")
        .select("*")
        .eq("id_cliente", id_cliente)
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        return None

    return respuesta.data[0]


def registrar_cliente(nombre, correo, telefono=None, ciudad="No especificada"):
    try:
        nombre = validar_texto_obligatorio(nombre, "nombre")
        correo = normalizar_correo(correo)

        if correo == "":
            raise ValueError("El correo no puede estar vacío.")

        cliente = {
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "ciudad": ciudad or "No especificada",
            "activo": True
        }

        respuesta = (
            supabase
            .table("clientes")
            .insert(cliente)
            .execute()
        )

        cliente_insertado = respuesta.data[0] if respuesta.data else cliente

        return respuesta_ok(
            "Cliente registrado correctamente.",
            cliente=cliente_insertado
        )

    except ValueError as error:
        return respuesta_error("validacion", str(error))

    except Exception as error:
        mensaje = str(error)

        if "duplicate" in mensaje.lower() or "unique" in mensaje.lower():
            return respuesta_error(
                "conflicto",
                "Ya existe un cliente con ese correo."
            )

        return respuesta_error("base_datos", mensaje)


# ---------------------------------------------------------
# RESUMEN
# ---------------------------------------------------------

def resumen_general():
    productos = listar_productos(solo_activos=True)
    clientes = listar_clientes(solo_activos=True)

    valor_inventario = 0

    for producto in productos:
        precio = float(producto.get("precio", 0))
        stock = int(producto.get("stock", 0))
        valor_inventario += precio * stock

    return {
        "productos_activos": len(productos),
        "clientes_activos": len(clientes),
        "valor_inventario": valor_inventario
    }
