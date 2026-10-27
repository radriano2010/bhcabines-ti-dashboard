import json
from datetime import datetime
import requests

# ==========================================
# CONEXÃO COM A API DO LIBRENMS
# ==========================================
LIBRENMS_URL = "http://localhost/api/v0/devices"
API_TOKEN = "2e9fc5f782b2764de511e7daf6482751"  # <-- Insira aqui o seu token da API do LibreNMS

headers = {"X-Auth-Token": API_TOKEN}
lista_de_dispositivos = []

try:
    response = requests.get(LIBRENMS_URL, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        lista_de_dispositivos = data.get("devices", [])
        print(f"Total de dispositivos obtidos do LibreNMS: {len(lista_de_dispositivos)}")
    else:
        print(f"Erro ao contactar a API do LibreNMS: {response.status_code}")
except Exception as e:
    print(f"Erro de conexão com o LibreNMS: {e}")

server_list = []
workstation_list = []
printer_list = []
network_list = []
other_list = []

for device in lista_de_dispositivos:
    ip_addr = device.get("ip") or device.get("hostname")
    
    if ip_addr == "172.17.0.1":
        continue

    nome = device.get("display") or device.get("sysName") or device.get("hostname") or "Desconhecido"
    tipo_hardware = str(device.get("hardware", "")).lower()
    tipo_servico = str(device.get("type", "")).lower()
    
    item_info = {
        "name": nome,
        "ip": ip_addr
    }
    
    if "server" in tipo_servico or "linux" in tipo_hardware or "windows server" in tipo_hardware or "ubuntu" in nome.lower():
        server_list.append(item_info)
    elif "printer" in tipo_hardware or "impressora" in nome.lower() or "epson" in nome.lower() or "brother" in nome.lower():
        printer_list.append(item_info)
    elif "router" in tipo_hardware or "switch" in tipo_hardware or "rt" in nome.lower() or "router" in nome.lower():
        network_list.append(item_info)
    elif "workstation" in tipo_servico or "desktop" in tipo_hardware or "station" in tipo_servico:
        workstation_list.append(item_info)
    else:
        other_list.append(item_info)

# Montagem do dicionário final compatível com o index.html
dados_json = {
    "servers": len(server_list),
    "workstations": len(workstation_list),
    "printers": len(printer_list),
    "networks": len(network_list),
    "others": len(other_list),
    "server_list": server_list,
    "workstation_list": workstation_list,
    "printer_list": printer_list,
    "network_list": network_list,
    "other_list": other_list,
    "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
}

# Salvar no ficheiro bh_cabines_assets.json com suporte a UTF-8
with open("bh_cabines_assets.json", "w", encoding="utf-8") as f:
    json.dump(dados_json, f, ensure_ascii=False, indent=4)

print("Ficheiro bh_cabines_assets.json gerado com sucesso via LibreNMS!")
