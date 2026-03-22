# Módulo 06: Middlewares e Human-in-the-Loop (HITL)

> **Objetivo:** Automação Assistida, Resiliência e Controle de Custos.
> **Status:** O diferencial para rodar IAs empresariais em Produção.

Este módulo demonstra o uso avançado da arquitetura de **Middlewares de Agente do LangChain** acoplada ao LangGraph para injetar resiliência, compressão de memória e supervisão humana cirúrgica.

---

## 📚 Patterns e Documentação Oficial

Para se aprofundar nos bastidores das técnicas demonstradas nos scripts `01`, `02` e `03`, aqui estão os links para as referências diretas dos [Middlewares Embutidos (Built-in)](https://docs.langchain.com/oss/python/langchain/middleware/built-in) e também do LangGraph:

1. **[Summarization Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#summarization)**
   - **Projeto: `01_summarization_example.py`**
   - Mecanismo que escuta o tamanho do pacote subindo para a LLM. Quando limites de histórico são batidos, as mensagens mais antigas são ejetadas e substituídas por um sumário cirúrgico encapsulado numa The `SystemMessage`. Isso abaixa radicalmente seus custos de API com conversas longas e previne o esgotamento do Context Window.

2. **[Model Fallback Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in#model-fallback)**
   - **Projeto: `02_modelfallback_example.py`**
   - Uma camada de resiliência (try/catch automático transposto à LLM). Sem ele, seu sistema fica dependente de um provedor; com ele, falhas como "NotFound", 502 Bad Gateway e Rate Limits do modelo original engatilham perfeitamente um modelo substituto na mesa hora, de forma invisível.

3. **[Human In The Loop Middleware (HITL)](https://docs.langchain.com/oss/python/langchain/middleware/built-in#human-in-the-loop)**
   - **Projeto: `03_email_agent.py`**
   - Para ações irreversíveis (processar cartão financeiro, emitir e-mails para clientes em nome da empresa). Assessorado pela função base `interrupt()`, o middleware barra o processamento do LLM e lança à Interface/Terminal os metadados da Tool para o Operador Humano dizer sim, não ou **editar**.
   - *Nota de Arquitetura Base:* Você pode entender como o `interrupt` funciona puramente no fluxo nativo lendo o **[Exemplo Completo de Interrupts do LangGraph](https://docs.langchain.com/oss/python/langgraph/interrupts#full-example-1)**.

---

## 🛠️ Passo a Passo: Assistente Pessoal de Gmail (`03_email_agent.py`)

A cereja do bolo deste módulo! O script integra o seu agente diretamente aos serviços GMAIL usando abstrações base de Python (`imaplib` e `smtplib`) e submete os rascunhos automatizados à aprovação via Terminal.

### Como clonar os testes na sua máquina local:

**1. Crie uma "Senha de App" (obrigatório)**
Como proteção padrão, scripts e códigos via Python nunca conseguem acesso usando sua senha normal de Gmail. Você precisa de um token secundário de bypass.
* Abra a [Segurança da sua Conta Google](https://myaccount.google.com/apppasswords?pli=1&rapt=AEjHL4OuC44Cyn5A54Y5n1RiF40k5MrtmfZWpYoRlMClxqE0WfITM0NBshLBRvCI145SRBrapLr_9TxYl8c7p8fNB5juN6TdSLTagb68QoT9MG-D5UZAq4Y).
* Garanta que a sua **Verificação em Duas Etapas** esteja ATIVADA!
* No menu (ou barra de pesquisa), encontre **Senhas de Aplicativo (App Passwords)**.
* Escolha qualquer nome para o novo App e clique em gerar. O Google fornecerá **16 letras amarelas**.
* Junte todas as letras em uma string única (ex: `zxyqmnbkaowfiute`).

**2. Configure o Arquivo de Variáveis (`.env`)**
Adicione o trecho a seguir no seu arquivo `.env` na raiz do projeto `ai-engineer-roadmap`:

```env
# Seu remetente principal (que o robô controlará)
GMAIL_USER="seu_email_principal@gmail.com"

# As 16 letrinhas grudadas que você acabou de gerar (substitui sua senha real)
GMAIL_APP_PASSWORD="suasenhaloucade16digitos"

# E-Mail do seu contato/conta secundária que será testada
TARGET_SENDER="email_secundario_hotm_ou_gmail_para_receber@hotmail.com"

# Não se esqueça (O Agente precisa de inteligência)
OPENAI_API_KEY="sk-proj-...." 
```

**3. Execute a Orquestração do E-mail e o Modo Edição HITL**
Envie um e-mail do seu `TARGET_SENDER` para sua caixa postal do Gmail. E então rode o script:

```bash
uv run python ./03-ai-agents/06-human-in-the-loop/03_email_agent.py
```
Quando ele interceptar sua caixa postal, trará o resumo do rascunho. Aperte `3` para ver como você intercepta, troca as palavras da Ferramenta de envio pela linha de comando, e manda o e-mail modificado adiante!

---

## ⏭️ Próximos Passos
Dominada a arte de intervir nos agentes em produção e prepará-los contra quedas financeiras, estamos prontos para evoluir as integrações de Ferramentas com as conexões **MCP (Model Context Protocol)** no próximo bloco!
