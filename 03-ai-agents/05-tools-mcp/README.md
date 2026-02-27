# 🔌 Módulo 5: Ferramentas e MCP

> **Goal:** O "USB-C" das aplicações de IA.  
> **Status:** O novo padrão industrial (Anthropic).

## 1. O Problema das Integrações
Atualmente, para conectar o Claude ao Google Drive, você precisa escrever código específico de integração.
Se você trocar o modelo para GPT-4, tem que reescrever.
Se trocar o Drive pelo Dropbox, tem que reescrever.

## 2. O que é MCP?
É um **Protocolo Aberto** que padroniza como IAs conversam com dados e ferramentas.
- **MCP Server:** O dono do dado (ex: GitHub, Slack, Postgres) expõe uma API MCP.
- **MCP Client:** O agente (ex: Claude Desktop, Cursor, seu App) consome a API.

## 3. Por que usar em 2025?
- **Desacoplamento:** Você escreve o conector "Postgres MCP" uma vez, e ele funciona com Claude, GPT-4, Llama 3, etc.
- **Segurança:** O protocolo gerencia permissões (o usuário precisa aprovar o acesso à tabela X).
- **Ecossistema:** Já existem servidores MCP prontos para Git, AWS, Linear, Notion.

## 🧠 Mental Model: "Drivers de Impressora"
Antigamente, cada word processor precisava saber falar com cada impressora. Era o caos.
O MCP é como o Driver Genérico de Impressora. O Word (Agente) manda imprimir, e o Driver (MCP Server) traduz para a HP, Canon ou Epson.

## ⏭️ Próximo Passo
Um agente é bom. Vários agentes são melhores?
Vá para **[Módulo 6: Multi-Agent Systems](../06-multi-agents)**.
