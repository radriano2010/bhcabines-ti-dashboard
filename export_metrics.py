
import json
import os
from datetime import datetime, timedelta
import requests

# --- Configurações dos Servidores ---
ZABBIX_URL = "http://192.168.254.80:8080/api_jsonrpc.php"
ZABBIX_USER = "admin_novo"
ZABBIX_PASS = "zabbix"

LIBRENMS_URL = "http://192.168.254.80:8000/api/v0"
LIBRENMS_TOKEN = "187c6bb55546da8ca383996ef98ca5ac"

OUTPUT_FILE = "bh_cabines_assets.json"


def get_zabbix_data():
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
        print(f"Erro Zabbix: {e}")

    return data_summary


def get_librenms_data():
    devices_summary = {"status": "error", "devices": []}
    try:
        headers = {"X-Auth-Token": LIBRENMS_TOKEN}
        response = requests.get(f"{LIBRENMS_URL}/devices", headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            devices_summary["devices"] = result.get("devices", [])
            devices_summary["status"] = "success"
    except Exception as e:
        print(f"Erro LibreNMS: {e}")

    return devices_summary


def classify_and_add(name, ip, tipo, hardware, os_name, server_list, workstation_list, printer_list, network_list, other_list):
    name_lower = str(name).lower() if name else ""
    tipo_lower = str(tipo).lower() if tipo else ""
    hardware_lower = str(hardware).lower() if hardware else ""
    os_lower = str(os_name).lower() if os_name else ""
    ip_str = str(ip) if ip else ""

    device_info = {"name": name, "ip": ip}

    server_keys = ["server", "srv", "db", "database", "ubuntu", "debian", "centos", "windows server", "vm", "virtual", "guardian"]
    workstation_keys = ["workstation", "desktop", "pc", "client", "notebook", "laptop", "usuario"]
    printer_keys = ["printer", "laserjet", "mfc", "print", "epson", "brother", "hp", "xerox"]
    network_keys = ["switch", "router", "firewall", "gateway", "net", "ap", "access point", "roteador", "hub", "routerer106"]

    if any(k in name_lower or k in tipo_lower or k in hardware_lower or k in os_lower for k in server_keys):
        server_list.append(device_info)
    elif any(k in name_lower or k in tipo_lower or k in hardware_lower or k in os_lower for k in workstation_keys):
        workstation_list.append(device_info)
    elif any(k in name_lower or k in tipo_lower or k in hardware_lower for k in printer_keys):
        printer_list.append(device_info)
    elif any(k in name_lower or k in tipo_lower or k in hardware_lower for k in network_keys):
        network_list.append(device_info)
    elif ip_str.startswith("192.168.254."):
        network_list.append(device_info)
    else:
        other_list.append(device_info)


def main():
    print("Coletando dados...")
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
        
        classify_and_add(name, ip_addr, name, "", "", server_list, workstation_list, printer_list, network_list, other_list)

    horario_brasilia = datetime.utcnow() - timedelta(hours=3)

    dashboard_payload = {
        "last_update": horario_brasilia.strftime("%Y-%m-%d %H:%M:%S"),
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

    print("Concluído com sucesso!")


if __name__ == "__main__":
    main()
