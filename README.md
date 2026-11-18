# bhcabines-ti-dashboard
Visão Geral da Arquitetura do Projeto

+---------------------------------------------------------------------------------+
|                         SERVIDOR UBUNTU LOCAL (BH CABINES)                      |
|                                                                                 |
|  [Ativos de Rede / TI] ---> [ Zabbix / LibreNMS ]                               |
|                                     |                                           |
|                                     v                                           |
|                             [ Grafana / APIs ]                                  |
|                                     |                                           |
|                         (Script de Coleta/Export)                               |
+---------------------------------------------------------------------------------+
                                      |
                           (Push via Git / REST API)
                                      v
+---------------------------------------------------------------------------------+
|                            GITHUB (REPOSITÓRIO & PAGES)                         |
|                                                                                 |
|  - Código-Fonte (React / Vue / HTML Dashboard)                                  |
|  - GitHub Actions (Build & Deploy Automático)                                   |
|  - Dashboard / Site Público ou Interno da BH Cabines                            |
+---------------------------------------------------------------------------------+


bhcabines-ti-dashboard/
├── .github/
│   └── workflows/          # Pipelines CI/CD (GitHub Actions)
├── docs/                   # Documentação da infraestrutura
├── scripts/                # Scripts Python/Shell para rodar no Ubuntu (coleta de métricas via API)
├── src/                    # Código-fonte da aplicação web (Dashboard/Frontend)
│   ├── assets/             # Logos da BH Cabines, ícones
│   ├── components/         # Componentes do Dashboard (Tabelas de Ativos, Status, Gráficos)
│   └── data/               # Arquivos JSON/Mock exportados para visualização estática
└── README.md               # Documentação geral do projeto
Etapa 2: Coleta de Dados no Servidor Ubuntu

Para exibir esses dados em um site hospedado no GitHub sem expor diretamente as portas do seu servidor local para a internet:

    Script de Exportação de Métricas (Python / Bash):

        Crie um script no seu servidor Ubuntu que consulte periodicamente as APIs do Zabbix API (para status de hosts e alertas) e do LibreNMS API (para inventário de rede/portas).

        Gere um arquivo JSON consolidado (ex: assets_summary.json).

    Envio Automático para o Repositório:

        O script no Ubuntu pode fazer um git commit + git push automatizado via Cron Job para a branch de dados do repositório, ou usar Webhooks.

📊 Etapa 3: Integração com Grafana

Para exibir os gráficos do Grafana no dashboard:

    Opção A (Embed/Iframe): Habilitar a funcionalidade de Embed Anonymous no grafana.ini para incorporar painéis diretamente no dashboard web.

    Opção B (Snapshot API): Usar a API do Grafana no servidor Ubuntu para capturar imagens (renderização PNG) dos painéis e enviá-las para a interface.

🛠️ Próximos Passos Recomendados

Para começarmos a colocar a mão na massa, podemos focar na parte em que você quer dar o primeiro passo:

    Estrutura do Repositório e Frontend: Criar um template base do dashboard web em HTML/JS/CSS ou React com a identidade da BH Cabines.

    Scripts de Integração: Escrever os scripts de conexão com as APIs do Zabbix/LibreNMS no servidor Ubuntu.

    Automação GitHub Actions: Configurar o deploy automático do site via GitHub Pages.
__________________________________________________________________________________________________________________________________________________

Token do LIbrenms : 

3423a1646ac316b8280317f3c901f357 
__________________________________________________________________________________________________________________________________________

CHAVE SSH 

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN54hl0/adZM4c1gE2hCDv6smeW9h/D78Oh1PPz3Y+/C bhcabines-ubuntu-server

______________________________________________________________________________________________________________________________________________
bash de atualização

./atualizar_dashboard.sh

