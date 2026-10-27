#!/bin/bash
DIR="/home/ubuntu/bhcabines-ti-dashboard"
cd "$DIR" || exit 1

# Garante que puxamos a versão mais atual do GitHub antes de gerar
git pull origin main --rebase

echo "A gerar métricas unificadas (Zabbix e LibreNMS)..."
python3 export_metrics.py

if [ ! -f "bh_cabines_assets.json" ]; then
    echo "Erro: O ficheiro bh_cabines_assets.json não foi gerado."
    exit 1
fi

git add bh_cabines_assets.json export_metrics.py gerar_e_enviar_json.sh

if git diff-index --quiet HEAD --; then
    echo "Sem alterações novas para enviar."
else
    git commit -m "Auto-update inventario e categorias $(date '+%d/%m/%Y %H:%M:%S')"
    if git push origin main; then
        echo "Atualizado e enviado para o GitHub com sucesso!"
    else
        echo "Erro: Falha ao enviar para o GitHub."
        exit 1
    fi
fi
