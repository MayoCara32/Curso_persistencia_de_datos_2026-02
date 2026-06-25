
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional


app = FastAPI(
    title="API del Sistema de Ventas",
    description="Primera API del curso Persistencia de Datos y SQL con Python.",
    version="1.0.0"
)


productos = [
    {
        "id_producto": 1,
        "sku": "P001",
        "nombre": "Mouse inalámbrico",
        "categoria": "Accesorios",
        "precio": 249.90,
        "stock": 15,
        "activo": True
    },
    {
        "id_producto": 2,
        "sku": "P002",
        "nombre": "Teclado mecánico",
        "categoria": "Accesorios",
        "precio": 899.00,
        "stock": 8,
        "activo": True
    },
    {
        "id_producto": 3,
        "sku": "P003",
        "nombre": "Monitor 24 pulgadas",
        "categoria": "Pantallas",
        "precio": 3299.00,
        "stock": 4,
        "activo": True
    },
    {
        "id_producto": 4,
        "sku": "P004",
        "nombre": "Cable HDMI",
        "categoria": "Cables",
        "precio": 120.00,
        "stock": 20,
        "activo": True
    }
]


clientes = [
    {
        "id_cliente": 1,
        "nombre": "Ana López",
        "correo": "ana@example.com",
        "ciudad": "CDMX",
        "activo": True
    },
    {
        "id_cliente": 2,
        "nombre": "Carlos Pérez",
        "correo": "carlos@example.com",
        "ciudad": "Guadalajara",
        "activo": True
    }
]


class ProductoCrear(BaseModel):
    sku: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    categoria: str = Field(min_length=1)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductoActualizar(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None


def modelo_a_dict(modelo, exclude_unset=False):
    """
    Convierte un modelo de Pydantic a diccionario.

    Funciona con Pydantic v1 y v2.
    """
    if hasattr(modelo, "model_dump"):
        return modelo.model_dump(exclude_unset=exclude_unset)

    return modelo.dict(exclude_unset=exclude_unset)


def normalizar_sku(sku):
    return sku.strip().upper()


def buscar_producto_por_sku(sku):
    sku = normalizar_sku(sku)

    for producto in productos:
        if producto["sku"] == sku:
            return producto

    return None


def obtener_siguiente_id_producto():
    if not productos:
        return 1

    return max(producto["id_producto"] for producto in productos) + 1


@app.get("/")
def inicio():
    return {
        "mensaje": "API del sistema de ventas funcionando.",
        "documentacion": "/docs",
        "endpoints_principales": [
            "GET /productos",
            "GET /productos/{sku}",
            "POST /productos",
            "PUT /productos/{sku}",
            "DELETE /productos/{sku}"
        ]
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "servicio": "API sistema de ventas"
    }


@app.get("/productos")
def listar_productos(solo_activos: bool = True):
    if solo_activos:
        return [
            producto
            for producto in productos
            if producto["activo"] is True
        ]

    return productos


@app.get("/productos/{sku}")
def obtener_producto(sku: str):
    producto = buscar_producto_por_sku(sku)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    return producto


@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCrear):
    datos_producto = modelo_a_dict(datos)
    sku = normalizar_sku(datos_producto["sku"])

    producto_existente = buscar_producto_por_sku(sku)

    if producto_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese SKU."
        )

    nuevo_producto = {
        "id_producto": obtener_siguiente_id_producto(),
        "sku": sku,
        "nombre": datos_producto["nombre"].strip(),
        "categoria": datos_producto["categoria"].strip(),
        "precio": datos_producto["precio"],
        "stock": datos_producto["stock"],
        "activo": True
    }

    productos.append(nuevo_producto)

    return {
        "mensaje": "Producto creado correctamente.",
        "producto": nuevo_producto
    }


@app.put("/productos/{sku}")
def actualizar_producto(sku: str, datos: ProductoActualizar):
    producto = buscar_producto_por_sku(sku)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    datos_actualizar = modelo_a_dict(datos, exclude_unset=True)

    if not datos_actualizar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron datos para actualizar."
        )

    for campo, valor in datos_actualizar.items():
        if isinstance(valor, str):
            valor = valor.strip()

            if valor == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El campo {campo} no puede quedar vacío."
                )

        producto[campo] = valor

    return {
        "mensaje": "Producto actualizado correctamente.",
        "producto": producto
    }


@app.delete("/productos/{sku}")
def desactivar_producto(sku: str):
    producto = buscar_producto_por_sku(sku)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    if producto["activo"] is False:
        return {
            "mensaje": "El producto ya estaba inactivo.",
            "producto": producto
        }

    producto["activo"] = False

    return {
        "mensaje": "Producto desactivado correctamente.",
        "producto": producto
    }


@app.get("/clientes")
def listar_clientes():
    return [
        cliente
        for cliente in clientes
        if cliente["activo"] is True
    ]


@app.get("/ventas/resumen")
def resumen_ventas():
    return {
        "mensaje": "Este endpoint será conectado con SQLite en la siguiente clase.",
        "total_ventas": 0,
        "total_ingresos": 0
    }
