import json
import os
from datetime import datetime
import requests

# --- Configurações dos Servidores ---
ZABBIX_URL = "http://192.168.254.80:8080/api_jsonrpc.php"
ZABBIX_USER = "Admin"  # Substitua pelo seu usuário do Zabbix
ZABBIX_PASS = "zabbix"  # Substitua pela sua senha do Zabbix

LIBRENMS_URL = "http://192.168.254.80:8000/api/v0"
LIBRENMS_TOKEN = "187c6bb55546da8ca383996ef98ca5ac"  # Gere o token no painel do LibreNMS

OUTPUT_FILE = "bh_cabines_assets.json"


def get_zabbix_data():
  """Autentica na API do Zabbix e busca hosts e problemas ativos."""
  data_summary = {"status": "error", "hosts": [], "problems": []}
  try:
    # 1. Autenticação (JSON-RPC)
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

    # 2. Buscar Hosts
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

    # 3. Buscar Alertas/Problemas Ativos
    problems_payload = {
        "jsonrpc": "2.0",
        "method": "problem.get",
        "params": {"output": "extend", "severities": [3, 4, 5]},  # Advertência, Média, Grave, Desastre
        "auth": auth_token,
        "id": 3,
    }
    prob_res = requests.post(ZABBIX_URL, json=problems_payload, timeout=10).json()
    if "result" in prob_res:
      data_summary["problems"] = prob_res["result"]

    data_summary["status"] = "success"
  except Exception as e:
    print(f"Erro ao conectar ao Zabbix: {e}")

  return data_summary


def get_librenms_data():
  """Busca o inventario de dispositivos e portas do LibreNMS via API REST."""
  data_summary = {"status": "error", "devices": [], "ports": []}
  headers = {"X-Auth-Token": LIBRENMS_TOKEN}

  try:
    # 1. Buscar Dispositivos (que utilizam SNMP porta 161, comunidade public)
    dev_res = requests.get(
        f"{LIBRENMS_URL}/devices", headers=headers, timeout=10
    )
    if dev_res.status_code == 200:
      data_summary["devices"] = dev_res.json().get("devices", [])

    # 2. Buscar Portas de Rede
    ports_res = requests.get(
        f"{LIBRENMS_URL}/ports", headers=headers, timeout=10
    )
    if ports_res.status_code == 200:
      data_summary["ports"] = ports_res.json().get("ports", [])

    data_summary["status"] = "success"
  except Exception as e:
    print(f"Erro ao conectar ao LibreNMS: {e}")

  return data_summary


def main():
  print(
      f"[{datetime.now()}] Iniciando coleta de dados para a BH Cabines..."
  )

  zabbix_data = get_zabbix_data()
  librenms_data = get_librenms_data()

  # Consolidação final dos dados
  payload = {
      "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "company": "BH Cabines",
      "zabbix": zabbix_data,
      "librenms": librenms_data,
  }

  with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=4)

  print(
      f"[{datetime.now()}] Dados consolidados e salvos com sucesso em"
      f" {OUTPUT_FILE}"
  )


if __name__ == "__main__":
  main()
