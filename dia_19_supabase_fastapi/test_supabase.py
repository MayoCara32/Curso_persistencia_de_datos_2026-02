
from supabase_client import supabase


def main():
    respuesta = (
        supabase
        .table("productos")
        .select("*")
        .limit(5)
        .execute()
    )

    print("Datos recibidos:")
    print(respuesta.data)


if __name__ == "__main__":
    main()
