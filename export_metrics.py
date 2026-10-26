import json
import os
from datetime import datetime
import requests

# --- Configurações dos Servidores ---
ZABBIX_URL = "http://192.168.254.80:8080/api_jsonrpc.php"
ZABBIX_USER = "admin_novo"
ZABBIX_PASS = "zabbix"

LIBRENMS_URL = "http://192.168.254.80:8000/api/v0"
LIBRENMS_TOKEN = "187c6bb55546da8ca383996ef98ca5ac"

OUTPUT_FILE = "bh_cabines_assets.json"


def get_zabbix_data():
    """Autentica na API do Zabbix e busca hosts."""
    data_summary = {"status": "error", "hosts": [], "problems": []}
    try:
        auth_payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"username": ZABBIX_USER, "password": ZABBIX_PASS},
            "id": 1,
        }
        response = requests.post(ZABBIX_URL, json=auth_payload, timeout=10)
        result = response.json()

        if "result" not in result:
            print("Erro na autenticação do Zabbix.")
            return data_summary

        auth_token = result["result"]

        hosts_payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host", "name", "status"],
                "selectInterfaces": ["ip"]
            },
            "auth": auth_token,
            "id": 2,
        }
        hosts_res = requests.post(ZABBIX_URL, json=hosts_payload, timeout=10).json()
        
        if "result" in hosts_res:
            data_summary["hosts"] = hosts_res["result"]

        data_summary["status"] = "success"
    except Exception as e:
        print(f"Erro ao conectar com Zabbix: {e}")

    return data_summary


def get_librenms_data():
    """Busca dispositivos na API do LibreNMS."""
    devices_summary = {"status": "error", "devices": []}
    try:
        headers = {"X-Auth-Token": LIBRENMS_TOKEN}
        response = requests.get(f"{LIBRENMS_URL}/devices", headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            devices_summary["devices"] = result.get("devices", [])
            devices_summary["status"] = "success"
        else:
            print(f"Erro na API do LibreNMS: Código {response.status_code}")
    except Exception as e:
        print(f"Erro ao conectar com LibreNMS: {e}")

    return devices_summary


def classify_and_add(name, ip, tipo, hardware, os_name, server_list, workstation_list, printer_list, network_list, other_list):
    """Classifica o dispositivo nas respetivas categorias."""
    name_lower = str(name).lower()
    tipo_lower = str(tipo).lower()
    hardware_lower = str(hardware).lower()
    os_lower = str(os_name).lower()

    device_info = {"name": name, "ip": ip}

    if "server" in tipo_lower or "linux" in os_lower or "windows server" in hardware_lower or "server" in hardware_lower or "srv" in name_lower or "db" in name_lower:
        server_list.append(device_info)
    elif "workstation" in tipo_lower or "desktop" in os_lower or "client" in hardware_lower or "pc" in hardware_lower or "desktop" in name_lower:
        workstation_list.append(device_info)
    elif "printer" in tipo_lower or "laserjet" in hardware_lower or "mfc" in hardware_lower or "print" in hardware_lower or "printer" in name_lower:
        printer_list.append(device_info)
    elif "switch" in tipo_lower or "router" in tipo_lower or "firewall" in tipo_lower or "network" in tipo_lower or "gateway" in hardware_lower or "router" in hardware_lower or "switch" in hardware_lower or "net" in name_lower:
        network_list.append(device_info)
    else:
        other_list.append(device_info)


def main():
    print("Coletando dados do Zabbix e LibreNMS...")
    zabbix_data = get_zabbix_data()
    librenms_data = get_librenms_data()

    server_list = []
    workstation_list = []
    printer_list = []
    network_list = []
    other_list = []

    for device in librenms_data.get("devices", []):
        ip_addr = device.get("ip", "IP não retornado")
        hostname = device.get("display") or device.get("hostname") or device.get("sysName")
        if not hostname or hostname == ip_addr:
            hostname = device.get("sysName") or f"Dispositivo ({ip_addr})"
        
        tipo = device.get("type", "")
        hardware = device.get("hardware", "")
        os_name = device.get("os", "")

        classify_and_add(hostname, ip_addr, tipo, hardware, os_name, server_list, workstation_list, printer_list, network_list, other_list)

    for host in zabbix_data.get("hosts", []):
        name = host.get("name") or host.get("host", "Desconhecido")
        interfaces = host.get("interfaces", [])
        ip_addr = interfaces[0].get("ip") if interfaces else "IP não retornado"
        
        classify_and_add(name, ip_addr, "", "", "", server_list, workstation_list, printer_list, network_list, other_list)

    dashboard_payload = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "zabbix": zabbix_data,
        "librenms": librenms_data,
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
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=4, ensure_ascii=False)

    print(f"Dados consolidados salvos com sucesso em {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
