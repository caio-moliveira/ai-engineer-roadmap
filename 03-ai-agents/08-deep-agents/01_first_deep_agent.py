"""
01_first_deep_agent.py
======================
Seu Primeiro Deep Agent — Assistente de Help Desk de TI

Objetivo: mostrar como o create_deep_agent() abstrai toda a infraestrutura de um
agente LangGraph em poucas linhas. Sem StateGraph, sem checkpointer manual,
sem configuração de memória, sem gerenciamento de tools loop.

Conceitos demonstrados:
  1. create_deep_agent() com ferramentas customizadas
  2. StateBackend padrão — memória efêmera, porém persistente dentro da thread
  3. thread_id: o agente "lembra" de toda a conversa com o mesmo usuário
  4. Ferramentas de filesystem embutidas (ls, write_file, read_file, grep...)
  5. Loop de conversa multi-turn no terminal

Caso de uso real: agente interno de suporte de TI de uma empresa
"""

import os
from dotenv import load_dotenv
from langchain.tools import tool
from deepagents import create_deep_agent
import pprint   

load_dotenv()

# ---------------------------------------------------------------------------
# 1. BANCO DE DADOS SIMULADO
#    Em produção: substitua por chamadas reais ao seu sistema de tickets
#    (Jira, ServiceNow, Zendesk, etc.)
# ---------------------------------------------------------------------------

_tickets: dict = {}
_ticket_counter = 1

_base_conhecimento = {
    "vpn": (
        "Para resetar a VPN: abra o Cisco Anyconnect → Preferences → Reset. "
        "Se persistir após 2 tentativas, encaminhe para a equipe de redes (ramal 4200)."
    ),
    "senha": (
        "Acesse portal.empresa.com/reset com seu email corporativo. "
        "Se o portal não carregar, ligue para TI no ramal 1234."
    ),
    "lento": (
        "Passos rápidos: (1) reinicie o notebook, (2) feche abas/programas extras, "
        "(3) verifique atualizações pendentes do Windows. "
        "Se o problema persistir por mais de 2 dias, agende manutenção preventiva."
    ),
    "email": (
        "Tente acessar via webmail (mail.empresa.com) para verificar se é problema "
        "local ou do servidor. Se o webmail também falhar, o servidor pode estar em "
        "manutenção — consulte status.empresa.com para informações em tempo real."
    ),
    "impressora": (
        "Passos: (1) verifique o cabo/wifi da impressora, (2) remova e reinstale o "
        "driver em Configurações → Impressoras, (3) reinicie o spooler de impressão "
        "via Services.msc. Se não resolver, abra um ticket para visita presencial."
    ),
}


# ---------------------------------------------------------------------------
# 2. FERRAMENTAS DO DOMÍNIO (SIMULADAS)
#    O agente chama essas tools automaticamente quando precisar.
# ---------------------------------------------------------------------------

@tool
def buscar_solucao_conhecida(problema: str) -> str:
    """
    Busca na base de conhecimento de TI uma solução para o problema informado.
    Use antes de abrir qualquer ticket.
    """
    for keyword, solution in _base_conhecimento.items():
        if keyword in problema.lower():
            return f"[SOLUCAO ENCONTRADA]\n{solution}"
    return "Nenhuma solução direta encontrada. Considere abrir um ticket para análise."


@tool
def abrir_ticket(titulo: str, descricao: str, prioridade: str, usuario: str) -> str:
    """
    Cria um novo ticket de suporte no sistema de TI.

    prioridade deve ser: 'baixa', 'media' ou 'alta'
      - alta:  sistema fora do ar, perda de dados, bloqueio total de trabalho
      - media: problema recorrente que impacta produtividade
      - baixa: melhoria, dúvida ou inconveniência menor
    """
    global _ticket_counter, _tickets

    ticket_id = f"TKT-{_ticket_counter:04d}"
    _tickets[ticket_id] = {
        "id": ticket_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade.lower(),
        "usuario": usuario,
        "status": "aberto",
    }
    _ticket_counter += 1

    sla = {"alta": "2h", "media": "8h", "baixa": "48h"}.get(prioridade.lower(), "48h")
    return (
        f"[TICKET CRIADO]\n"
        f"ID       : {ticket_id}\n"
        f"Titulo   : {titulo}\n"
        f"Prioridade: {prioridade.upper()} (SLA: {sla})\n"
        f"Status   : ABERTO\n"
        f"A equipe de TI entrará em contato dentro do prazo do SLA."
    )


@tool
def consultar_ticket(ticket_id: str) -> str:
    """
    Retorna o status atual de um ticket pelo seu ID (ex: TKT-0001).
    Use quando o usuário quiser saber o andamento do chamado.
    """
    ticket = _tickets.get(ticket_id.strip().upper())
    if not ticket:
        return f"[ERRO] Ticket '{ticket_id}' não encontrado. Verifique o ID e tente novamente."
    return (
        f"[STATUS DO TICKET]\n"
        f"ID         : {ticket['id']}\n"
        f"Titulo     : {ticket['titulo']}\n"
        f"Status     : {ticket['status'].upper()}\n"
        f"Prioridade : {ticket['prioridade'].upper()}\n"
        f"Usuario    : {ticket['usuario']}\n"
        f"Descricao  : {ticket['descricao']}"
    )


@tool
def listar_tickets_usuario(usuario: str) -> str:
    """
    Lista todos os tickets abertos de um determinado usuário.
    Use quando o usuário perguntar sobre seus chamados em aberto.
    """
    tickets_usuario = [t for t in _tickets.values() if t["usuario"].lower() == usuario.lower()]
    if not tickets_usuario:
        return f"Nenhum ticket encontrado para '{usuario}'."

    linhas = [
        f"  [{t['id']}] {t['prioridade'].upper():6} | {t['status'].upper():10} | {t['titulo']}"
        for t in tickets_usuario
    ]
    return f"[TICKETS DE {usuario.upper()}]\n" + "\n".join(linhas)


# ---------------------------------------------------------------------------
# 3. CRIAÇÃO DO DEEP AGENT
#
#    create_deep_agent() entrega automaticamente:
#    - MemoryCheckpointer (persistência de conversa por thread_id)
#    - StateBackend (filesystem virtual por thread — rascunhos em memória)
#    - Ferramentas embutidas: ls, read_file, write_file, edit_file, glob, grep
#    - TodoListMiddleware (planejamento de tarefas multi-step)
#
#    Você só precisa fornecer: model, suas tools e o system_prompt.
# ---------------------------------------------------------------------------

agente_helpdesk = create_deep_agent(
    model="gpt-4o-mini",    # Modelo econômico — suficiente para suporte L1
    tools=[
        buscar_solucao_conhecida,
        abrir_ticket,
        consultar_ticket,
        listar_tickets_usuario,
    ],
    system_prompt="""
    Você é o Agente de Suporte de TI da empresa. Atenda colaboradores com empatia e objetividade.

    FLUXO DE ATENDIMENTO:
    1. Entenda o problema completamente antes de agir
    2. Sempre tente buscar_solucao_conhecida primeiro
    3. Se a solução não resolver, abra um ticket com a prioridade correta
    4. Para consultas de status, use consultar_ticket ou listar_tickets_usuario
    5. Informe sempre o ID do ticket criado e o SLA esperado

    ESCALONAMENTO DE PRIORIDADE:
    - ALTA  : sistema crítico fora do ar, perda de dados, CEO/diretoria bloqueada
    - MEDIA : impacto direto na produtividade, problema recorrente
    - BAIXA : inconveniência, melhoria ou dúvida pontual

    DICA EXTRA: Você tem acesso a ferramentas de filesystem (write_file, read_file).
    Se precisar fazer anotações durante o atendimento, salve em /notas/atendimento.md.
    Isso demonstra que o Deep Agent tem contexto de "área de trabalho" embutido.

    Seja direto, profissional e resolva o problema do usuário com eficiência.
    """,
)

# ---------------------------------------------------------------------------
# 4. LOOP DE CONVERSA MULTI-TURN
#
#    O thread_id é o identificador da sessão/usuário.
#    O Deep Agent mantém todo o histórico de mensagens automaticamente.
#    Mude o thread_id para simular um usuário diferente (sem memória compartilhada).
# ---------------------------------------------------------------------------

def run_helpdesk():
    """Executa o agente em modo interativo no terminal."""

    # Cada usuário tem seu próprio thread_id — a conversa é isolada por usuário
    THREAD_ID = "colaborador-ana-lima"
    config = {"configurable": {"thread_id": THREAD_ID}}

    print("=" * 60)
    print("  HELP DESK DE TI — Powered by Deep Agents (LangChain)")
    print("=" * 60)
    print(f"  Sessao: {THREAD_ID}")
    print("  Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Voce: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nAtendimento encerrado.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("\nAtendimento encerrado. Ate logo!")
            break

        # O agente recebe a mensagem e mantém o histórico automaticamente
        # graças ao thread_id passado no config
        response = agente_helpdesk.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        # A última mensagem é sempre a resposta do agente
        reply = response["messages"][-1].content
        print(f"\nAgente: {reply}\n")

        # Exibe o plano de tarefas se o agente usou o TodoListMiddleware
        todos = response.get("todos", [])
        if todos:
            print("[Plano de tarefas do agente]")
            icons = {"completed": "[OK]", "in_progress": "[>>]", "pending": "[ ]"}
            for t in todos:
                print(f"  {icons.get(t['status'], '[ ]')} {t['content']}")
            print()


# ---------------------------------------------------------------------------
# 5. DEMONSTRAÇÃO AUTOMATIZADA (sem input manual)
#    Útil para testes e demonstrações em sala de aula.
# ---------------------------------------------------------------------------

def run_demo():
    """Executa uma conversa pré-definida para fins de demonstração."""

    config = {"configurable": {"thread_id": "demo-carlos-mendes"}}

    conversas = "Oi, minha VPN não conecta desde hoje de manhã. Preciso acessar o sistema interno urgente. Poderia abrir um ticket?"




    response = agente_helpdesk.invoke(
        {"messages": [{"role": "user", "content": conversas[0]}]},
        config=config,  # mesmo config = mesma sessao/memória
    )

    pprint.pprint(response)




# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Comente/descomente conforme o modo desejado:
    run_demo()          # Demonstração automática (sem input manual)
    # run_helpdesk()    # Modo interativo (requer input no terminal)
