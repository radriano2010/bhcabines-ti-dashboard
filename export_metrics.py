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
    """Autentica na API do Zabbix e busca hosts e problemas ativos."""
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
            "params": {"output": ["hostid", "host", "name", "status"]},
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
    """Busca dispositivos na API do LibreNMS, categoriza e extrai nome e IP."""
    devices_summary = {
        "status": "error", 
        "devices": [], 
        "servers": 0, 
        "workstations": 0, 
        "printers": 0, 
        "others": 0,
        "server_list": [],
        "workstation_list": [],
        "printer_list": [],
        "other_list": []
    }
    try:
        headers = {"X-Auth-Token": LIBRENMS_TOKEN}
        response = requests.get(f"{LIBRENMS_URL}/devices", headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            devices = result.get("devices", [])
            devices_summary["devices"] = devices
            
            servers_count = 0
            workstations_count = 0
            printers_count = 0
            others_count = 0

            server_list = []
            workstation_list = []
            printer_list = []
            other_list = []

            for device in devices:
                tipo = str(device.get("type", "")).lower()
                hardware = str(device.get("hardware", "")).lower()
                os_name = str(device.get("os", "")).lower()
                ip_addr = device.get("ip", "IP não retornado")
                
                # Pega o display, hostname ou sysName do LibreNMS
                hostname = device.get("display") or device.get("hostname") or device.get("sysName") or "Desconhecido"

                # Se o hostname retornado for igual ao IP, usa o sysName ou cria um rótulo limpo
                if hostname == ip_addr or not hostname:
                    sysname = device.get("sysName")
                    if sysname and sysname != ip_addr:
                        hostname = sysname
                    else:
                        hostname = f"Dispositivo ({ip_addr})"

                device_info = {"name": hostname, "ip": ip_addr}

                if "server" in tipo or "linux" in os_name or "windows server" in hardware or "server" in hardware:
                    servers_count += 1
                    server_list.append(device_info)
                elif "workstation" in tipo or "desktop" in os_name or "client" in hardware or "pc" in hardware:
                    workstations_count += 1
                    workstation_list.append(device_info)
                elif "printer" in tipo or "laserjet" in hardware or "mfc" in hardware or "print" in hardware:
                    printers_count += 1
                    printer_list.append(device_info)
                else:
                    others_count += 1
                    other_list.append(device_info)

            devices_summary["servers"] = servers_count
            devices_summary["workstations"] = workstations_count
            devices_summary["printers"] = printers_count
            devices_summary["others"] = others_count
            
            devices_summary["server_list"] = server_list
            devices_summary["workstation_list"] = workstation_list
            devices_summary["printer_list"] = printer_list
            devices_summary["other_list"] = other_list
            devices_summary["status"] = "success"
        else:
            print(f"Erro na API do LibreNMS: Código {response.status_code}")
    except Exception as e:
        print(f"Erro ao conectar com LibreNMS: {e}")

    return devices_summary


def main():
    print("Coletando dados do Zabbix e LibreNMS...")
    zabbix_data = get_zabbix_data()
    librenms_data = get_librenms_data()

    dashboard_payload = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "zabbix": zabbix_data,
        "librenms": librenms_data,
        "servers": librenms_data.get("servers", 0),
        "workstations": librenms_data.get("workstations", 0),
        "printers": librenms_data.get("printers", 0),
        "others": librenms_data.get("others", 0),
        "server_list": librenms_data.get("server_list", []),
        "workstation_list": librenms_data.get("workstation_list", []),
        "printer_list": librenms_data.get("printer_list", []),
        "other_list": librenms_data.get("other_list", []),
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, indent=4, ensure_ascii=False)

    print(f"Dados salvos com sucesso em {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

