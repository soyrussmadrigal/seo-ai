import requests

# Config
BASE_URL = "http://127.0.0.1:8000"
DAYS = 30

# 1. Extraer datos de Search Console
print(f"🔄 Extrayendo datos de los últimos {DAYS} días...")
resp = requests.get(f"{BASE_URL}/extraer-datos", params={"days": DAYS})
if resp.status_code != 200:
    print("❌ Error al extraer datos:", resp.text)
    exit(1)

json_data = resp.json()
if json_data["status"] != "success":
    print("❌ Fallo al extraer datos:", json_data["message"])
    exit(1)

data = json_data["data"]
print(f"✅ Datos extraídos: {len(data)} registros")

# 2. Enviar a /save_history
print("📤 Guardando en base de datos...")
resp = requests.post(f"{BASE_URL}/save_history", json=data)
if resp.status_code != 200:
    print("❌ Error al guardar:", resp.text)
    exit(1)

print("✅ Guardado exitosamente:", resp.json())
