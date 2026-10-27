# Exemplo de ajuste na estruturação do JSON final no export_metrics.py

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
    
    # Lógica de classificação
    item_info = {"name": nome, "ip": ip_addr}
    
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

# Salvar no arquivo bh_cabines_assets.json...
# 3. Execute o script para gerar o novo JSON limpo
python3 export_metrics.py

# 4. Adicione, faça o commit e envie diretamente
git add export_metrics.py bh_cabines_assets.json
git commit -m "feat: atualiza script e json corretamente"
git push origin main


