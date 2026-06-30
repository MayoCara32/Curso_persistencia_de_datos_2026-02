
import requests
import json


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
            print("No se pudo conectar con la API.")
            return None

        except requests.exceptions.Timeout:
            print("La API tardó demasiado en responder.")
            return None

    def validar_respuesta(self, respuesta):
        if respuesta is None:
            return None

        if 200 <= respuesta.status_code < 300:
            return respuesta.json()

        print("Error HTTP:", respuesta.status_code)

        try:
            print(json.dumps(respuesta.json(), indent=4, ensure_ascii=False))
        except Exception:
            print(respuesta.text)

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

        return self.validar_respuesta(respuesta)


def main():
    api = ClienteAPI("http://127.0.0.1:8000")

    print("Probando conexión con API...")
    print(api.health())

    print("\nConsultando productos...")
    productos = api.listar_productos(solo_activos=False)

    print(json.dumps(productos, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
