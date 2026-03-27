"""
02_pipeline_real_world.py
=========================
Pipeline de Produção de Conteúdo B2B — Deep Agents em Ação

Objetivo: demonstrar as capacidades avançadas do Deep Agents em um fluxo de trabalho
real com múltiplos agentes especializados, memória persistente entre sessões e
aprovação humana antes de publicar.

Conceitos demonstrados:
  1. Subagentes declarativos: pesquisador + redator (sem código de orquestração manual)
  2. CompositeBackend: rascunhos efêmeros (StateBackend) + biblioteca persistente (StoreBackend)
  3. TodoListMiddleware: planejamento automático de tarefas multi-step (embutido)
  4. HITL — Human-in-the-Loop: pausa a execução antes de uma ação crítica para aprovação
  5. InMemoryStore + MemorySaver: memória persistente entre threads de sessão

Caso de uso real: agência de marketing / time de conteúdo de uma empresa B2B

COMPARATIVO COM O MÓDULO ANTERIOR:
  Nos módulos 4-7, você escreveria manualmente:
    - StateGraph com nós e edges
    - Checkpointer configurado explicitamente
    - Lógica de roteamento entre subagentes
    - Gerenciamento de ToolRuntime e tool_call_id
    - Loop de HITL manual com LangGraph interrupts
  Aqui, o harness faz tudo isso. Você define O QUÊ quer, não COMO implementar.
"""

import os
import pprint
from dotenv import load_dotenv

from langchain.tools import tool
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

load_dotenv()

# ---------------------------------------------------------------------------
# 1. INFRAESTRUTURA DE PERSISTÊNCIA
#
#    InMemoryStore: banco de dados em memória compartilhado entre threads.
#    Em produção, substitua por:
#      from langgraph.store.postgres import PostgresStore
#      store = PostgresStore(connection_string="postgresql://...")
#
#    MemorySaver: checkpointer necessário para que o HITL funcione.
#    Em produção, substitua por:
#      from langgraph.checkpoint.postgres import PostgresSaver
# ---------------------------------------------------------------------------

biblioteca_store = InMemoryStore()
checkpointer = MemorySaver()


# ---------------------------------------------------------------------------
# 2. FERRAMENTAS DO DOMÍNIO
# ---------------------------------------------------------------------------

@tool
def buscar_dados_mercado(tema: str) -> str:
    """
    Pesquisa dados, estatísticas e tendências de mercado sobre um tema.
    Use para embasar o conteúdo com informações sólidas e atualizadas.
    """
    # Simulação de pesquisa. Em produção: TavilySearch, SerperAPI, etc.
    dados = {
        "inteligência artificial": """
            - 72% das empresas Fortune 500 adotaram alguma solução de IA em 2024 (McKinsey)
            - Mercado de IA generativa deve alcançar US$ 1,3 tri até 2032 (Bloomberg)
            - Prioridades de 2025: AI Agents autônomos, RAG em produção, multimodal
            - Principal barreira: falta de dados estruturados e governança clara
            - ROI médio reportado: 3.5x em processos automatizados com IA
        """,
        "cloud computing": """
            - 94% das empresas usam ao menos um serviço cloud (Flexera 2024)
            - FinOps é prioridade: 67% querem reduzir custos cloud em 2025
            - Multi-cloud é estratégia de 87% das grandes empresas
            - Edge computing cresce 37% ao ano — processamento próximo ao dado
            - Kubernetes: 96% das organizações o utilizam em produção
        """,
        "liderança": """
            - 85% dos líderes precisam de desenvolvimento contínuo (Gallup 2024)
            - Trabalho híbrido permanente exige novas habilidades de gestão assíncrona
            - Burnout de liderança afeta 42% dos gestores (Deloitte)
            - Diversidade em C-Level ainda abaixo de 30% nas 500 maiores empresas do Brasil
            - Coaching executivo cresce 28% ao ano como ferramenta de performance
        """,
    }
    tema_lower = tema.lower()
    for keyword, data in dados.items():
        if keyword in tema_lower or any(w in tema_lower for w in keyword.split()):
            return f"[PESQUISA: {tema}]\n{data.strip()}"
    return (
        f"[PESQUISA: {tema}]\n"
        f"Mercado em crescimento acelerado. Alta demanda por especialistas.\n"
        f"Foco em eficiência operacional e ROI demonstrável. "
        f"Empresas buscam cases reais e conteúdo prático."
    )


@tool
def publicar_conteudo(slug: str, conteudo: str, tema: str, formato: str) -> str:
    """
    Publica o conteúdo aprovado na biblioteca persistente da empresa.

    ATENÇÃO: Esta ferramenta requer aprovação humana antes de ser executada (HITL).
    O editor responsável irá revisar o conteúdo antes da publicação.

    slug   : identificador único sem espaços (ex: 'ia-para-pmes-linkedin-2025')
    conteudo: texto completo do conteúdo a ser publicado
    tema   : assunto abordado
    formato: tipo de conteúdo (ex: 'Post LinkedIn', 'Artigo Blog')
    """
    biblioteca_store.put(
        namespace=("biblioteca_conteudo",),
        key=slug,
        value={"conteudo": conteudo, "tema": tema, "formato": formato},
    )
    return (
        f"[PUBLICADO COM SUCESSO]\n"
        f"Slug   : {slug}\n"
        f"Tema   : {tema}\n"
        f"Formato: {formato}\n"
        f"O conteudo esta disponivel na biblioteca e pronto para distribuicao."
    )


@tool
def listar_conteudo_publicado() -> str:
    """
    Lista todo o conteúdo já publicado na biblioteca da empresa.
    Use para verificar se um tema já foi coberto antes de produzir novo conteúdo.
    """
    items = list(biblioteca_store.search(("biblioteca_conteudo",)))
    if not items:
        return "[BIBLIOTECA VAZIA] Nenhum conteudo publicado ainda."

    linhas = [
        f"  [{item.key}] {item.value.get('tema', 'N/A')} ({item.value.get('formato', 'N/A')})"
        for item in items
    ]
    return "[BIBLIOTECA DE CONTEUDO]\n" + "\n".join(linhas)


# ---------------------------------------------------------------------------
# 3. BACKEND HÍBRIDO (CompositeBackend)
#
#    Roteamento de filesystem por prefixo de caminho:
#      - /rascunhos/* → StateBackend  (efêmero, vive apenas na thread atual)
#      - /biblioteca/* → StoreBackend (persistente via InMemoryStore)
#
#    O agente não precisa saber qual backend está usando.
#    Ele simplesmente escreve em /rascunhos/ ou /biblioteca/ e o harness roteias.
# ---------------------------------------------------------------------------

def criar_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/biblioteca/": StoreBackend(runtime)},
    )


# ---------------------------------------------------------------------------
# 4. SUBAGENTES ESPECIALIZADOS
#
#    Definidos de forma declarativa — sem código de orquestração.
#    O harness cria a thread secundária, gerencia o ToolRuntime e
#    garante que o contexto do agente principal não seja "poluído".
# ---------------------------------------------------------------------------

subagentes = [
    {
        "name": "pesquisador",
        "description": (
            "Pesquisa dados, estatísticas e tendências de mercado sobre um tema. "
            "Retorna um relatório estruturado com os principais pontos para embasar conteúdo B2B."
        ),
        "model": "gpt-4o-mini",   # Modelo econômico — pesquisa não exige criatividade
        "system_prompt": """
            Você é um Pesquisador de Conteúdo B2B especializado.

            Quando receber um tema:
            1. Use buscar_dados_mercado para coletar estatísticas e tendências
            2. Salve os achados organizados em /rascunhos/pesquisa.md
            3. Retorne um resumo com: contexto do mercado, 3-5 dados concretos, dores do público-alvo

            Seja preciso. Dados sem fonte são inventados — evite.
        """,
        "tools": [buscar_dados_mercado],
    },
    {
        "name": "redator",
        "description": (
            "Escreve posts LinkedIn e artigos de blog B2B com base em pesquisa fornecida. "
            "Especialista em copy que converte, com tom profissional e linguagem acessível."
        ),
        "model": "gpt-4o",        # Modelo mais capaz — escrita criativa exige qualidade
        "system_prompt": """
            Você é um Redator Expert em Conteúdo B2B para LinkedIn e blogs corporativos.

            Diretrizes de escrita:
            - Tom: profissional mas humano, sem jargão excessivo
            - Estrutura: Hook impactante → Problema → 3 insights com dados → CTA claro
            - Post LinkedIn: 200-280 palavras, parágrafos curtos, use dados da pesquisa
            - Artigo Blog: 600-800 palavras, subtítulos, listas quando pertinente

            Processo:
            1. Leia os dados em /rascunhos/pesquisa.md
            2. Escreva o conteúdo seguindo as diretrizes acima
            3. Salve o rascunho em /rascunhos/draft_final.md
            4. Retorne o texto completo

            Nunca invente estatísticas. Use apenas dados que estão na pesquisa.
        """,
        "tools": [],   # O redator usa apenas as ferramentas de filesystem embutidas
    },
]


# ---------------------------------------------------------------------------
# 5. AGENTE ORQUESTRADOR (Deep Agent Principal)
#
#    Este agente coordena todo o pipeline:
#      - Usa write_todos para planejar as etapas (TodoListMiddleware embutido)
#      - Delega pesquisa e redação via task() (SubAgentMiddleware embutido)
#      - Chama publicar_conteudo, que dispara o HITL antes de executar
#
#    interrupt_on: define quais tools precisam de aprovação humana ANTES de rodar.
#    checkpointer: necessário para pausar/retomar a execução no HITL.
# ---------------------------------------------------------------------------

orquestrador = create_deep_agent(
    name="orquestrador-conteudo-b2b",
    model="gpt-4o",
    tools=[publicar_conteudo, listar_conteudo_publicado],
    subagents=subagentes,
    backend=criar_backend,
    system_prompt="""
    Você é o Orquestrador de um Pipeline de Produção de Conteúdo B2B de uma agência de marketing.

    Para CADA solicitação de criação de conteúdo, siga este fluxo:

    ETAPA 1 — PLANEJAMENTO: Use write_todos para criar o plano com as etapas:
      ["Verificar biblioteca", "Pesquisa de mercado", "Redação do conteúdo", "Revisão", "Publicação"]

    ETAPA 2 — VERIFICAÇÃO: Use listar_conteudo_publicado para checar se o tema já existe.

    ETAPA 3 — PESQUISA: Delegue ao subagente 'pesquisador' com instrução completa sobre o tema.
      Instrução completa inclui: tema exato + formato desejado + público-alvo.

    ETAPA 4 — REDAÇÃO: Delegue ao subagente 'redator' com:
      - O tema e formato
      - O resultado resumido da pesquisa
      - Instrução para salvar em /rascunhos/draft_final.md e retornar o texto completo

    ETAPA 5 — REVISÃO: Leia /rascunhos/draft_final.md e avalie se está dentro das diretrizes.
      Se houver problemas graves, delegue novamente ao redator com feedback específico.

    ETAPA 6 — PUBLICAÇÃO: Chame publicar_conteudo com:
      - slug: identificador único kebab-case (ex: 'ia-automacao-pmes-linkedin')
      - conteudo: o texto completo do rascunho final
      - tema: o tema original
      - formato: o formato do conteúdo

    IMPORTANTE: A publicação requer aprovação humana. Após chamar publicar_conteudo,
    o editor da empresa irá revisar antes de confirmar. Aguarde a decisão.

    Seja metódico e transparente. Informe o usuário sobre cada etapa concluída.
    """,
    # HITL: publicar_conteudo requer aprovação do editor antes de executar
    interrupt_on={"publicar_conteudo": True},
    checkpointer=checkpointer,
    store=biblioteca_store,
)


# ---------------------------------------------------------------------------
# 6. PIPELINE COM HITL INTERATIVO
#
#    O fluxo tem 2 fases:
#      Fase 1 — Produção: o agente pesquisa, redige e propõe a publicação
#      Fase 2 — Aprovação: o humano vê o conteúdo e decide aprovar ou rejeitar
#
#    A "magia" do Deep Agents:
#      Quando o agente chama publicar_conteudo(), o HITL pausa a execução.
#      O estado completo é preservado no checkpointer.
#      Ao aprovar, a execução retoma de onde parou — sem repetir etapas.
# ---------------------------------------------------------------------------

def executar_pipeline(tema: str, formato: str = "Post LinkedIn"):
    """
    Executa o pipeline completo de produção com HITL.

    Args:
        tema   : assunto do conteúdo (ex: "Inteligência Artificial para PMEs")
        formato: tipo de conteúdo (ex: "Post LinkedIn", "Artigo Blog")
    """
    # thread_id único por produção — mantém o estado de toda a execução
    thread_id = f"producao-{tema[:25].lower().replace(' ', '-').replace('/', '')}"
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 65)
    print("  PIPELINE DE CONTEUDO B2B — Deep Agents")
    print("=" * 65)
    print(f"  Tema   : {tema}")
    print(f"  Formato: {formato}")
    print(f"  Thread : {thread_id}")
    print("-" * 65)
    print("\n[1/2] Iniciando producao...\n")

    # --- FASE 1: PRODUCAO ---
    # O agente irá: planejar → pesquisar → redigir → tentar publicar
    # Na tentativa de publicar, o HITL pausará a execução automaticamente
    result = orquestrador.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Preciso de um {formato} sobre '{tema}'. "
                        f"Siga seu fluxo de trabalho completo e apresente o conteúdo final antes de publicar."
                    ),
                }
            ]
        },
        config=config,
    )

    # --- FASE 2: APROVACAO HUMANA ---
    # state.next indica que a execução está pausada aguardando input
    state = orquestrador.get_state(config)

    while state.next:
        print("\n" + "=" * 65)
        print("[2/2] APROVACAO NECESSARIA — Execucao pausada para revisao humana")
        print("=" * 65)

        # Extrai o conteúdo pendente de publicação do estado atual
        mensagens = state.values.get("messages", [])
        conteudo_para_revisar = _extrair_conteudo_para_revisao(mensagens)

        if conteudo_para_revisar:
            print(f"\n[CONTEUDO AGUARDANDO APROVACAO]\n")
            print(conteudo_para_revisar[:800])
            if len(conteudo_para_revisar) > 800:
                print(f"\n... (e mais {len(conteudo_para_revisar) - 800} caracteres)")

        print("\nOpcoes:")
        print("  [a] Aprovar — publicar na biblioteca")
        print("  [r] Rejeitar — enviar para revisao com feedback")
        print("  [s] Sair sem publicar")

        decisao = input("\nSua decisao: ").strip().lower()

        if decisao == "a":
            print("\n[APROVADO] Publicando na biblioteca de conteudo...")
            result = orquestrador.invoke(
                Command(resume={"decisions": [{"type": "approve"}]}),
                config=config,
            )
        elif decisao == "r":
            feedback = input("Feedback para o redator (ex: 'Faltou mencionar o ROI'): ").strip()
            if not feedback:
                feedback = "Revisar e melhorar o conteudo."
            print(f"\n[REJEITADO] Enviando para revisao: '{feedback}'")
            result = orquestrador.invoke(
                Command(resume={"decisions": [{"type": "reject", "message": feedback}]}),
                config=config,
            )
        else:
            print("\n[ENCERRADO] Pipeline finalizado sem publicacao.")
            break

        # Verifica se houve novas interrupções (ex: o agente tentou publicar novamente)
        state = orquestrador.get_state(config)

    # --- RESULTADO FINAL ---
    print("\n" + "=" * 65)
    print("  PIPELINE CONCLUIDO")
    print("=" * 65)

    ultima_mensagem = result.get("messages", [])
    if ultima_mensagem:
        print(f"\n[AGENTE]\n{ultima_mensagem[-1].content}")

    # Exibe o plano de tarefas executado pelo TodoListMiddleware
    todos = result.get("todos", [])
    if todos:
        print("\n[PLANO DE TAREFAS EXECUTADO]")
        icons = {"completed": "[FEITO]", "in_progress": "[EXEC ]", "pending": "[     ]"}
        for t in todos:
            print(f"  {icons.get(t['status'], '[?]')} {t['content']}")

    print()


def _extrair_conteudo_para_revisao(mensagens: list) -> str:
    """
    Tenta extrair o rascunho do conteúdo das últimas mensagens para exibição ao revisor.
    Procura na última mensagem do assistente por blocos de conteúdo.
    """
    for msg in reversed(mensagens):
        content = getattr(msg, "content", "")
        if isinstance(content, str) and len(content) > 100:
            # Retorna a última mensagem substancial do agente como preview
            tipo = getattr(msg, "type", "")
            if tipo == "ai":
                return content
    return ""


# ---------------------------------------------------------------------------
# 7. DEMONSTRAÇÃO DE MEMÓRIA PERSISTENTE ENTRE SESSÕES
#
#    Isso demonstra o StoreBackend em ação:
#    Conteúdo publicado em uma sessão é visível em outra sessão completamente diferente.
# ---------------------------------------------------------------------------

def verificar_biblioteca():
    """
    Abre uma sessão NOVA e lista o conteúdo publicado em sessões anteriores.
    Demonstra que o StoreBackend persiste além do thread_id.
    """
    # Thread completamente diferente — sem memória de conversa anterior
    config = {"configurable": {"thread_id": "verificacao-biblioteca-session"}}

    print("=" * 65)
    print("  VERIFICACAO DA BIBLIOTECA (nova sessao)")
    print("=" * 65)
    print("  Demonstracao: conteudo de sessoes anteriores permanece disponivel.\n")

    result = orquestrador.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Liste todo o conteúdo publicado na nossa biblioteca de conteúdo.",
                }
            ]
        },
        config=config,
    )

    print("[AGENTE]")
    print(result["messages"][-1].content)
    print()


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # --- PIPELINE PRINCIPAL ---
    # O agente vai pesquisar, redigir e pedir aprovação antes de publicar.
    executar_pipeline(
        tema="Inteligência Artificial para Pequenas Empresas",
        formato="Post LinkedIn",
    )

    # --- VERIFICAÇÃO DE MEMÓRIA PERSISTENTE ---
    # Rode esta linha DEPOIS do pipeline acima para ver o conteúdo publicado
    # em uma nova sessão (thread_id diferente).
    # Descomente para testar:
    # verificar_biblioteca()
