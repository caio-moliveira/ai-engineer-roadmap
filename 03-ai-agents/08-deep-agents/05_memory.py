"""
05_memory.py
============
Memória Persistente — AGENTS.md e StoreBackend no Deep Agents

Objetivo: entender as duas camadas de "memória" do Deep Agents e quando usar cada uma.
Elas resolvem problemas diferentes — confundi-las é um erro comum de iniciantes.

CAMADA 1 — AGENTS.md (Contexto Estático, sempre presente)
  → Instruções permanentes: quem é o agente, perfil do usuário, preferências de resposta
  → Carregado automaticamente no startup quando FilesystemBackend está configurado
  → Equivalente a um "briefing fixo" — nunca muda durante a execução
  → Localização: AGENTS.md na raiz do root_dir do FilesystemBackend

CAMADA 2 — StoreBackend em /memorias/ (Memória Dinâmica, cross-thread)
  → Informações que o agente descobre durante conversas e precisa lembrar depois
  → Sobrevive a múltiplas sessões (thread_ids diferentes)
  → O agente lê e escreve dinamicamente via read_file/write_file
  → Equivalente a um "caderno de anotações" que o agente atualiza continuamente

COMPARATIVO PRÁTICO:
  AGENTS.md          → "Você trabalha em vendas B2B, prefere respostas diretas"
  /memorias/          → "Empresa Acme: CEO é João Silva, objeção: preço alto, última reunião: 10/03"

Conceitos demonstrados:
  1. FilesystemBackend + AGENTS.md: contexto estático carregado no startup
  2. CompositeBackend: /memorias/ → StoreBackend (persistente) | resto → StateBackend (efêmero)
  3. Memória cross-session: o que foi escrito em uma sessão é lido em outra
  4. Padrão de leitura-antes-de-responder: agente consulta memória antes de agir

Caso de uso real: CRM inteligente — agente de vendas que "lembra" de cada cliente
entre sessões, sem precisar que o vendedor repita o contexto toda vez.
"""

import os
import pprint
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 1. INFRAESTRUTURA DE PERSISTÊNCIA
#
#    crm_store: banco de dados compartilhado entre TODAS as sessões/threads.
#    Cada thread usa o mesmo store, então /memorias/ é verdadeiramente global.
#
#    checkpointer: necessário para manter histórico de mensagens por thread.
# ---------------------------------------------------------------------------

crm_store = InMemoryStore()
# Em produção: crm_store = PostgresStore(connection_string="postgresql://...")

checkpointer = MemorySaver()
# Em produção: checkpointer = PostgresSaver(connection_string="postgresql://...")


# ---------------------------------------------------------------------------
# 2. BACKEND HÍBRIDO PARA CRM
#
#    O CompositeBackend resolve o problema central do CRM:
#    "Como o agente trabalha com rascunhos temporários mas persiste
#     informações importantes de clientes entre sessões?"
#
#    Resposta: roteamento por prefixo de caminho.
#
#    /memorias/  → StoreBackend: tudo aqui é persistente entre sessões
#    /rascunhos/ → StateBackend: notas temporárias, descartadas ao fim da thread
#    (default)   → StateBackend: qualquer outro path é efêmero
# ---------------------------------------------------------------------------

def backend_crm(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memorias/": StoreBackend(runtime)},   # Esta pasta persiste!
    )


# ---------------------------------------------------------------------------
# 3. AGENTE DE VENDAS COM MEMÓRIA
#
#    O AGENTS.md (criado em ./AGENTS.md) é lido automaticamente pelo
#    FilesystemBackend na raiz do root_dir — fornece o contexto estático:
#    quem é o agente, perfil da empresa, preferências e glossário.
#
#    A memória dinâmica acontece em /memorias/ via StoreBackend.
# ---------------------------------------------------------------------------

agente_vendas = create_deep_agent(
    name="assistente-vendas-crm",
    model="gpt-4o",
    tools=[],
    # FilesystemBackend + CompositeBackend: lê AGENTS.md E persiste /memorias/
    backend=backend_crm,
    store=crm_store,
    checkpointer=checkpointer,
    system_prompt="""
    Você é o Assistente de Vendas B2B da TechVentures (detalhes em AGENTS.md).

    PROTOCOLO DE MEMÓRIA (siga rigorosamente):

    AO INICIAR QUALQUER CONVERSA SOBRE UM CLIENTE ESPECÍFICO:
    1. Tente ler /memorias/prospect_[nome-empresa-em-kebab-case].md
    2. Se existir: use as informações para personalizar sua resposta
    3. Se não existir: informe que é o primeiro contato e colete as informações básicas

    AO FINALIZAR UMA INTERAÇÃO RELEVANTE:
    4. Atualize /memorias/prospect_[nome-empresa].md com:
       - Data da interação
       - Novos insights sobre o prospect
       - Objeções levantadas
       - Próximos passos acordados
       - Fase atual no funil

    LEMBRE-SE: /memorias/ persiste entre sessões. /rascunhos/ é descartado ao fechar.
    Use /rascunhos/ para análises intermediárias e /memorias/ para o que importa.

    Seja consultivo: antes de vender, entenda a dor. Faça perguntas, não pitch.
    """,
)


# ---------------------------------------------------------------------------
# 4. DEMONSTRAÇÃO: MEMÓRIA CROSS-SESSION
#
#    Sessão 1 (thread A): vendedor atende Empresa Acme, registra informações
#    Sessão 2 (thread B): vendedor retoma contato — agente lembra de tudo
#
#    Este é o valor central do StoreBackend no CRM.
# ---------------------------------------------------------------------------

def sessao_primeiro_contato():
    """
    Sessão 1: Primeiro contato com a Empresa Acme.
    O agente coleta informações e registra em /memorias/.
    """
    print("=" * 65)
    print("  SESSAO 1: Primeiro Contato — Empresa Acme")
    print("=" * 65)
    print("  Thread: 'vendas-acme-sessao-1'")
    print("  O agente vai registrar o perfil em /memorias/\n")

    config = {"configurable": {"thread_id": "vendas-acme-sessao-1"}, "callbacks": [langfuse_handler]}

    # Turn 1: Apresentação do prospect
    msg1 = (
        "Acabei de ter uma call com a Empresa Acme Logística. "
        "Eles têm 200 funcionários, setor de logística, "
        "a dor principal é falta de visibilidade do estoque em tempo real. "
        "O decisor é a Dra. Beatriz Motta (COO). Budget estimado: R$ 80k/ano. "
        "Tivemos uma boa conversa — ela pediu uma demo para semana que vem. "
        "Registre isso e me diga o próximo passo recomendado."
    )

    result1 = agente_vendas.invoke(
        {"messages": [{"role": "user", "content": msg1}]},
        config=config,
    )
    print(f"[Vendedor]: {msg1[:80]}...")
    print(f"\n[Agente]:\n{result1['messages'][-1].content}\n")

    # Turn 2: Informação adicional — objeção surgiu
    msg2 = (
        "Atualização: falei com a Beatriz novamente. "
        "Ela levantou uma objeção: o time de TI deles é pequeno (2 pessoas) "
        "e está preocupado com a complexidade de implantação. "
        "Adiciona isso ao histórico."
    )

    result2 = agente_vendas.invoke(
        {"messages": [{"role": "user", "content": msg2}]},
        config=config,
    )
    print(f"[Vendedor]: {msg2[:80]}...")
    print(f"\n[Agente]:\n{result2['messages'][-1].content}\n")
    print("-" * 65)
    print("  Sessao 1 encerrada. Informacoes salvas em /memorias/prospect_acme-logistica.md")
    print("-" * 65)


def sessao_retomada_contato():
    """
    Sessão 2: Retomada de contato — thread COMPLETAMENTE diferente.
    O agente lê /memorias/ e já sabe tudo sobre a Acme.
    """
    print("\n" + "=" * 65)
    print("  SESSAO 2: Retomada de Contato — Thread Diferente!")
    print("=" * 65)
    print("  Thread: 'vendas-acme-sessao-2-nova'")
    print("  O agente nao tem historico de mensagens, mas tem /memorias/\n")

    # Thread completamente diferente — sem memória de conversa
    config = {"configurable": {"thread_id": "vendas-acme-sessao-2-nova"}, "callbacks": [langfuse_handler]}

    msg = (
        "Vou falar com a Acme Logística amanhã para a demo. "
        "Me lembra o contexto do cliente e me sugere como abordar a objeção de TI."
    )

    result = agente_vendas.invoke(
        {"messages": [{"role": "user", "content": msg}]},
        config=config,
    )
    print(f"[Vendedor]: {msg}")
    print(f"\n[Agente]:\n{result['messages'][-1].content}")
    print("\n" + "=" * 65)
    print("  OBSERVE: o agente lembrou da Beatriz Motta, da objeção de TI")
    print("  e do budget — tudo de uma thread DIFERENTE!")
    print("  Isso é o StoreBackend + /memorias/ em ação.")
    print("=" * 65)


def demo_agents_md():
    """
    Demonstra o AGENTS.md: abre uma sessão sem nenhum contexto de cliente
    e verifica se o agente já "sabe" quem é a empresa e suas preferências.
    """
    print("\n" + "=" * 65)
    print("  AGENTS.md DEMO: Contexto Estático Carregado no Startup")
    print("=" * 65)
    print("  O agente deve saber quem é a TechVentures sem que informemos.\n")

    config = {"configurable": {"thread_id": "agents-md-test-sessao"}, "callbacks": [langfuse_handler]}

    result = agente_vendas.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Qual é o ICP da nossa empresa e qual o ticket médio que trabalhamos? "
                        "Me dê também um exemplo de como você explicaria nosso produto para um CFO."
                    ),
                }
            ]
        },
        config=config,
    )
    print("[Agente]:")
    print(result["messages"][-1].content)
    print("\n  OBSERVE: o agente sabia sobre a TechVentures, ICP e ticket médio.")
    print("  Isso veio do AGENTS.md — carregado automaticamente no startup.\n")


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # DEMO 1: AGENTS.md — contexto sempre presente
    demo_agents_md()

    # DEMO 2 e 3: Memória cross-session via StoreBackend
    # Rode sessao_primeiro_contato() primeiro, depois sessao_retomada_contato()
    # para ver o agente "lembrar" entre threads diferentes.
    # sessao_primeiro_contato()
    # sessao_retomada_contato()
