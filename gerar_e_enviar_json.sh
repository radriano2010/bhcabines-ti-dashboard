#!/bin/bash

# Diretório oficial do projeto
DIR="/home/ubuntu/bhcabines-ti-dashboard"
cd "$DIR" || exit 1

echo "A gerar métricas unificadas (Zabbix e LibreNMS)..."
python3 export_metrics.py

# Verifica se o ficheiro JSON foi gerado com sucesso
if [ ! -f "bh_cabines_assets.json" ]; then
    echo "Erro: O ficheiro bh_cabines_assets.json não foi gerado."
    exit 1
fi

# Adiciona todas as alterações ao Git
git add .

# Verifica se existem alterações pendentes para commit
if git diff-index --quiet HEAD --; then
    echo "Sem alterações novas para enviar."
else
    git commit -m "Auto-update inventario e categorias $(date '+%d/%m/%Y %H:%M:%S')"
    
    # Sincroniza com o remoto para evitar conflitos de versão
    git pull origin main --rebase
    
    # Faz o push e valida se ocorreu com sucesso
    if git push origin main; then
        echo "Atualizado e enviado para o GitHub com sucesso!"
    else
        echo "Erro: Falha ao enviar para o GitHub."
        exit 1
    fi
fi
