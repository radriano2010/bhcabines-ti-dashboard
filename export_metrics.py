# Exemplo da estrutura correta no export_metrics.py

ativos_processados = []

for device in lista_de_dispositivos:
    ip_addr = device.get("ip") or device.get("hostname")
    
    # 1. Ignorar o IP de gateway do Docker para evitar redundância
    if ip_addr == "172.17.0.1":
        continue
        
    # 2. Recolher e normalizar dados de nome e tipo
    nome = device.get("display") or device.get("sysName") or device.get("hostname") or "Desconhecido"
    tipo_hardware = str(device.get("hardware", "")).lower()
    tipo_servico = str(device.get("type", "")).lower()
    
    # 3. Lógica robusta de classificação por categorias
    if "server" in tipo_servico or "linux" in tipo_hardware or "windows server" in tipo_hardware or "ubuntu" in nome.lower():
        categoria = "Servidores"
    elif "printer" in tipo_hardware or "impressora" in nome.lower() or "epson" in nome.lower() or "brother" in nome.lower():
        categoria = "Impressoras"
    elif "router" in tipo_hardware or "switch" in tipo_hardware or "rt" in nome.lower() or "router" in nome.lower():
        categoria = "Rede / SW / RT"
    elif "workstation" in tipo_servico or "desktop" in tipo_hardware or "station" in tipo_servico:
        categoria = "Estações"
    else:
        # Se não cair em nenhuma categoria anterior, vai para Outros
        categoria = "Outros"
        
    # Adicionar o ativo devidamente categorizado
    ativos_processados.append({
        "nome": nome,
        "ip": ip_addr,
        "categoria": categoria
    })
    
