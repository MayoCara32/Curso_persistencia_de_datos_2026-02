
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "ventas.db"


def obtener_conexion():
    """
    Crea una conexión con SQLite.

    Buenas prácticas:
    - Crea la carpeta data si no existe.
    - Activa llaves foráneas.
    - Permite acceder a columnas por nombre.
    """
    DATA_DIR.mkdir(exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row

    return conexion


def consultar_todos(sql, parametros=()):
    """
    Ejecuta una consulta SELECT y devuelve varias filas como diccionarios.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(sql, parametros)
        filas = cursor.fetchall()
        return [dict(fila) for fila in filas]

    finally:
        conexion.close()


def consultar_uno(sql, parametros=()):
    """
    Ejecuta una consulta SELECT y devuelve una sola fila como diccionario.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(sql, parametros)
        fila = cursor.fetchone()

        if fila is None:
            return None

        return dict(fila)

    finally:
        conexion.close()


def ejecutar(sql, parametros=()):
    """
    Ejecuta INSERT, UPDATE o DELETE.

    Devuelve:
    - ultimo_id
    - filas_afectadas
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(sql, parametros)
        conexion.commit()

        return {
            "ultimo_id": cursor.lastrowid,
            "filas_afectadas": cursor.rowcount
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def ejecutar_varios(sql, lista_parametros):
    """
    Ejecuta una consulta varias veces.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.executemany(sql, lista_parametros)
        conexion.commit()

        return {
            "filas_afectadas": cursor.rowcount
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def ejecutar_script(sql_script):
    """
    Ejecuta un bloque grande de SQL.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.executescript(sql_script)
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def ejecutar_transaccion(funcion_operacion):
    """
    Ejecuta una operación compleja dentro de una transacción.

    La función recibida debe aceptar un cursor como argumento.

    Si todo sale bien:
        commit

    Si algo falla:
        rollback
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("BEGIN")
        resultado = funcion_operacion(cursor)
        conexion.commit()
        return resultado

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
