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

# Adiciona todas as alterações (Python, HTML e JSON) ao Git
git add .

# Verifica se existem alterações pendentes para commit
if git diff-index --quiet HEAD --; then
    echo "Sem alterações novas para enviar."
else
    git commit -m "Auto-update inventario e categorias $(date '+%d/%m/%Y %H:%M:%S')"
    git push origin main
    echo "Atualizado e enviado para o GitHub com sucesso!"
fi

