
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

import services


app = FastAPI(
    title="API del Sistema de Ventas con SQLite",
    description="API conectada a SQLite para el curso Persistencia de Datos con Python.",
    version="2.0.0"
)


@app.on_event("startup")
def startup_event():
    services.inicializar_base_datos()



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


class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=1)
    correo: str = Field(min_length=1)
    telefono: Optional[str] = None
    ciudad: Optional[str] = "No especificada"


class ItemVenta(BaseModel):
    sku: str = Field(min_length=1)
    cantidad: int = Field(gt=0)


class VentaCrear(BaseModel):
    id_cliente: int = Field(gt=0)
    productos: List[ItemVenta]


def modelo_a_dict(modelo, exclude_unset=False):
    if hasattr(modelo, "model_dump"):
        return modelo.model_dump(exclude_unset=exclude_unset)

    return modelo.dict(exclude_unset=exclude_unset)



def manejar_resultado_servicio(resultado):
    """
    Convierte respuestas de services.py en respuestas HTTP.
    """
    if resultado.get("ok"):
        return resultado

    tipo_error = resultado.get("tipo_error")
    mensaje = resultado.get("mensaje", "Error en la operación.")

    if tipo_error == "no_encontrado":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=mensaje
        )

    if tipo_error == "conflicto":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje
        )

    if tipo_error == "validacion":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensaje
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=mensaje
    )



@app.get("/")
def inicio():
    return {
        "mensaje": "API conectada a SQLite funcionando.",
        "documentacion": "/docs",
        "version": "2.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "base_datos": "SQLite"
    }



@app.get("/productos")
def listar_productos(solo_activos: bool = True):
    return services.listar_productos(solo_activos=solo_activos)


@app.get("/productos/{sku}")
def obtener_producto(sku: str):
    producto = services.buscar_producto_por_sku(sku)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado."
        )

    return producto



@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCrear):
    datos_producto = modelo_a_dict(datos)

    resultado = services.registrar_producto(
        sku=datos_producto["sku"],
        nombre=datos_producto["nombre"],
        categoria=datos_producto["categoria"],
        precio=datos_producto["precio"],
        stock=datos_producto["stock"]
    )

    return manejar_resultado_servicio(resultado)


@app.put("/productos/{sku}")
def actualizar_producto(sku: str, datos: ProductoActualizar):
    datos_actualizar = modelo_a_dict(datos, exclude_unset=True)

    resultado = services.actualizar_producto(
        sku=sku,
        datos_actualizar=datos_actualizar
    )

    return manejar_resultado_servicio(resultado)


@app.delete("/productos/{sku}")
def desactivar_producto(sku: str):
    resultado = services.desactivar_producto(sku)

    return manejar_resultado_servicio(resultado)



@app.get("/clientes")
def listar_clientes(solo_activos: bool = True):
    return services.listar_clientes(solo_activos=solo_activos)


@app.get("/clientes/{id_cliente}")
def obtener_cliente(id_cliente: int):
    cliente = services.buscar_cliente_por_id(id_cliente)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado."
        )

    return cliente


@app.post("/clientes", status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCrear):
    datos_cliente = modelo_a_dict(datos)

    resultado = services.registrar_cliente(
        nombre=datos_cliente["nombre"],
        correo=datos_cliente["correo"],
        telefono=datos_cliente.get("telefono"),
        ciudad=datos_cliente.get("ciudad")
    )

    return manejar_resultado_servicio(resultado)



@app.post("/ventas", status_code=status.HTTP_201_CREATED)
def crear_venta(datos: VentaCrear):
    datos_venta = modelo_a_dict(datos)

    resultado = services.registrar_venta(
        id_cliente=datos_venta["id_cliente"],
        productos_vendidos=datos_venta["productos"]
    )

    return manejar_resultado_servicio(resultado)


@app.get("/ventas")
def listar_ventas():
    return services.listar_ventas()


@app.get("/ventas/resumen")
def resumen_ventas():
    return services.resumen_ventas()


@app.get("/ventas/{id_venta}/ticket")
def consultar_ticket(id_venta: int):
    ticket = services.consultar_ticket(id_venta)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada."
        )

    return ticket
