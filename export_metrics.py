import json
from datetime import datetime
import requests
import socket
import ipaddress

# ==========================================
# CONEXÃO COM A API DO LIBRENMS
# ==========================================
LIBRENMS_URL = "http://192.168.254.80:8000/api/v0/devices"
API_TOKEN = "3423a1646ac316b8280317f3c901f357"

headers = {"X-Auth-Token": API_TOKEN}
lista_de_dispositivos = []

def parse_ip(raw_ip):
    """Converte IPs retornados em formato binário, inteiro ou string para x.x.x.x"""
    if not raw_ip:
        return "Desconhecido"
    if isinstance(raw_ip, bytes):
        try:
            return socket.inet_ntoa(raw_ip)
        except:
            return str(raw_ip)
    if isinstance(raw_ip, str) and len(raw_ip) == 4 and not any(c.isdigit() for c in raw_ip):
        try:
            return socket.inet_ntoa(raw_ip.encode('latin1'))
        except:
            pass
    if isinstance(raw_ip, int):
        try:
            return str(ipaddress.IPv4Address(raw_ip))
        except:
            pass
    return str(raw_ip)

try:
    response = requests.get(LIBRENMS_URL, headers=headers, timeout=10)
    print(f"Status Code da API: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        lista_de_dispositivos = data.get("devices", [])
        print(f"Total de dispositivos obtidos do LibreNMS: {len(lista_de_dispositivos)}")
    else:
        print(f"Erro ao contactar a API do LibreNMS: {response.status_code} - Resposta: {response.text}")
except Exception as e:
    print(f"Erro de conexão com o LibreNMS: {e}")

server_list = []
workstation_list = []
printer_list = []
network_list = []
other_list = []

for device in lista_de_dispositivos:
    raw_ip = device.get("ip") or device.get("hostname")
    ip_addr = parse_ip(raw_ip)
    
    if ip_addr in ["172.17.0.1", "127.0.0.1", "Desconhecido"]:
        if ip_addr == "172.17.0.1":
            continue

    nome = device.get("display") or device.get("sysName") or device.get("hostname") or "Desconhecido"
    nome_lower = nome.lower()
    tipo_hardware = str(device.get("hardware", "")).lower()
    tipo_servico = str(device.get("type", "")).lower()
    
    item_info = {
        "name": nome,
        "ip": ip_addr
    }
    
    # ==========================================
    # REGRAS DE CLASSIFICAÇÃO REFINADAS
    # ==========================================
    if any(k in tipo_servico or k in tipo_hardware for k in ["windows server", "linux-server", "enterprise server"]) or ("server" in nome_lower and not any(sub in nome_lower for sub in ["user", "station", "pc"])):
        server_list.append(item_info)
    elif any(k in tipo_hardware or k in nome_lower for k in ["printer", "impressora", "epson", "brother", "hp"]):
        printer_list.append(item_info)
    elif any(k in tipo_hardware or k in tipo_servico or k in nome_lower for k in ["router", "switch", "rt", "firewall", "gateway"]):
        network_list.append(item_info)
    elif any(k in tipo_servico or k in tipo_hardware or k in nome_lower for k in ["workstation", "desktop", "station", "pc", "notebook", "client"]) or any(nome_lower.startswith(prefix) for prefix in ["adm", "tele", "station", "pc", "user"]):
        workstation_list.append(item_info)
    else:
        workstation_list.append(item_info)

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
