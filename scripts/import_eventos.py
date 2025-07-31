#script para postear los eventos de eventos csv, en Powershell/CMD en la carpeta scripts escribe:
#python import_eventos.py --csv eventos.csv --usuario TU_USUARIO --clave TU_CONTRASEÑA
#o si ya tienes un token directamente:
#python import_eventos.py --csv eventos.csv --token TU_TOKEN
import csv, requests, argparse
from datetime import datetime

def obtener_token(api, usuario, clave):
    r = requests.post(f"{api}/api/auth/token/", json={"username":usuario, "password":clave})
    r.raise_for_status()
    return r.json()["access"]

def main():
    p = argparse.ArgumentParser() #esto define los argmentos que recibe el script
    p.add_argument("--csv", required=True)
    p.add_argument("--api", default="http://127.0.0.1:8000")
    p.add_argument("--usuario")
    p.add_argument("--clave")
    p.add_argument("--token")
    args = p.parse_args()

    token = args.token or obtener_token(args.api, args.usuario, args.clave)
    cabeceras = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    publicados = fallidos = 0
    
    with open(args.csv, encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            titulo      = fila["título"]
            descripcion = fila["descripción"]
            dt = datetime.strptime(fila["fecha"], "%d-%m-%Y").replace(hour=12)
            evento = {"title": titulo, "description": descripcion, "date": dt.isoformat()}
            r = requests.post(f"{args.api}/api/events/", headers=cabeceras, json=evento) #formato listo para el POST de nuestra página c:
            if r.status_code == 201:
                publicados += 1
            else:
                fallidos += 1

    print(f"Publicados: {publicados}, Fallidos: {fallidos}")

if __name__ == "__main__":
    main()
