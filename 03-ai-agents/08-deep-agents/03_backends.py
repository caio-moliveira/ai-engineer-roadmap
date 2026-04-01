"""
03_backends.py
==============
Backends de Filesystem — Controle de Armazenamento no Deep Agents

Objetivo: entender como o Deep Agents gerencia o "espaço de trabalho" do agente
através de backends plugáveis. Essa abstração resolve um problema real:
onde os arquivos que o agente cria vivem? Por quanto tempo? Quem pode acessar?

Conceitos demonstrados:
  1. StateBackend   — padrão, efêmero por thread (RAM, não persiste após o processo)
  2. FilesystemBackend — acesso real ao disco com sandboxing (dev/local)
  3. StoreBackend   — persistência cross-thread via InMemoryStore (ou PostgresStore)
  4. CompositeBackend — roteamento por prefixo: cada caminho vai para um backend diferente

QUANDO USAR CADA UM:
  StateBackend    → rascunhos temporários, trabalho de uma única sessão
  FilesystemBackend → CLI local, scripts de automação, acesso real ao projeto
  StoreBackend    → dados que precisam sobreviver a múltiplas sessões
  CompositeBackend → híbrido: working files efêmeros + outputs persistentes

Caso de uso real: Sistema de triagem e arquivamento de currículos para RH
"""

import os
import pprint
from dotenv import load_dotenv
from langchain.tools import tool
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler()

# Diretório deste arquivo — usado pelo FilesystemBackend
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


@tool
def analisar_curriculo(nome: str, experiencia_anos: int, habilidades: str, cargo_desejado: str) -> str:
    """
    Analisa um currículo e retorna uma pontuação de fit para a vaga.
    Use para avaliar candidatos recebidos.
    """
    score = 0
    feedback = []

    if experiencia_anos >= 5:
        score += 40
        feedback.append("Experiencia solida (5+ anos)")
    elif experiencia_anos >= 2:
        score += 25
        feedback.append("Experiencia adequada (2-4 anos)")
    else:
        score += 10
        feedback.append("Experiencia limitada (menos de 2 anos)")

    habilidades_lower = habilidades.lower()
    skills_desejadas = ["python", "sql", "machine learning", "cloud", "llm", "langchain"]
    matches = [s for s in skills_desejadas if s in habilidades_lower]
    score += len(matches) * 10
    if matches:
        feedback.append(f"Skills relevantes: {', '.join(matches)}")

    classificacao = "APROVADO" if score >= 50 else "RESERVA" if score >= 30 else "REPROVADO"

    return (
        f"[TRIAGEM: {nome}]\n"
        f"Cargo      : {cargo_desejado}\n"
        f"Score      : {score}/100\n"
        f"Resultado  : {classificacao}\n"
        f"Destaques  : {'; '.join(feedback)}"
    )


# ---------------------------------------------------------------------------
# 2. DEMO 1 — StateBackend (Comportamento Padrão)
#
#    O agente trabalha em memória. Arquivos existem apenas dentro da thread.
#    Se você iniciar uma nova thread (thread_id diferente), os arquivos somem.
# ---------------------------------------------------------------------------

def demo_state_backend():
    """
    StateBackend: arquivos vivem na RAM, escopados ao thread_id.
    Ideal para trabalho descartável de uma única sessão.
    """
    print("\n" + "=" * 65)
    print("  DEMO 1: StateBackend (Ephemeral)")
    print("=" * 65)
    print("  Arquivos criados pelo agente vivem APENAS nesta thread.")
    print("  Ao mudar o thread_id, o agente começa do zero.\n")

    # create_deep_agent() sem backend= usa StateBackend automaticamente
    agente = create_deep_agent(
        model="gpt-4o-mini",
        tools=[analisar_curriculo],
        system_prompt="""
            Você é um Triador de Currículos de RH.
            Para cada candidato: use analisar_curriculo, salve o resultado em
            /triagem/[nome].txt e confirme a operação.
        """,
        # Sem backend= → StateBackend é o padrão
    )

    config_thread_1 = {"configurable": {"thread_id": "triagem-sessao-manha"}, "callbacks": [langfuse_handler]}

    result = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analise este candidato e salve o resultado: "
                        "Nome: Ana Lima, 6 anos de experiência, "
                        "habilidades: Python, SQL, Machine Learning, LLM. "
                        "Vaga: Engenheiro de IA Sênior."
                    ),
                }
            ]
        },
        config=config_thread_1,
    )
    print("[Thread 'manha'] Resposta do agente:")
    print(result["messages"][-1].content)

    # Nova thread — o arquivo /triagem/Ana Lima.txt não existe aqui
    config_thread_2 = {"configurable": {"thread_id": "triagem-sessao-tarde"}, "callbacks": [langfuse_handler]}

    result2 = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Liste os arquivos em /triagem/ para ver candidatos avaliados.",
                }
            ]
        },
        config=config_thread_2,
    )
    print("\n[Thread 'tarde' — nova sessao] Resposta do agente:")
    print(result2["messages"][-1].content)
    print("\n  OBSERVE: o arquivo da sessao 'manha' NAO existe na sessao 'tarde'.")
    print("  Isso e o StateBackend: isolamento total por thread.\n")


# ---------------------------------------------------------------------------
# 3. DEMO 2 — FilesystemBackend (Acesso Real ao Disco)
#
#    O agente lê e escreve arquivos REAIS no seu sistema de arquivos.
#    virtual_mode=True: sandbox de segurança — bloqueia path traversal (../../etc/passwd)
#    Ideal para scripts locais, CLIs e automações no seu projeto.
# ---------------------------------------------------------------------------

def demo_filesystem_backend():
    """
    FilesystemBackend: acesso real ao disco, com sandbox de segurança.
    Arquivos gerados ficam em CURRENT_DIR/output_rh/
    """
    print("\n" + "=" * 65)
    print("  DEMO 2: FilesystemBackend (Real Disk Access)")
    print("=" * 65)
    print(f"  Root dir : {CURRENT_DIR}")
    print("  Arquivos criados em disco ficam em: ./output_rh/")
    print("  virtual_mode=True bloqueia acesso fora do root_dir.\n")

    agente = create_deep_agent(
        model="gpt-4o-mini",
        tools=[analisar_curriculo],
        system_prompt="""
            Você é um Triador de Currículos de RH com acesso ao disco.
            Para cada candidato: use analisar_curriculo e salve em /output_rh/[nome].txt.
            Use ls para confirmar que o arquivo foi criado.
        """,
        # FilesystemBackend: lê/escreve arquivos reais no root_dir
        backend=FilesystemBackend(root_dir=CURRENT_DIR, virtual_mode=True),
    )

    config = {"configurable": {"thread_id": "rh-disk-session-001"}, "callbacks": [langfuse_handler]}

    result = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analise e salve em disco: "
                        "Nome: Carlos Mendes, 3 anos de experiência, "
                        "habilidades: Python, SQL, Cloud, LangChain. "
                        "Vaga: Engenheiro de IA Pleno."
                    ),
                }
            ]
        },
        config=config,
    )
    print("[FilesystemBackend] Resposta do agente:")
    # print(result["messages"][-1].content)
    pprint.pprint(result)
    # Verifica se o arquivo foi criado no disco
    output_path = os.path.join(CURRENT_DIR, "output_rh")
    if os.path.exists(output_path):
        arquivos = os.listdir(output_path)
        print(f"\n  Arquivos criados em disco ({output_path}):")
        for f in arquivos:
            print(f"    - {f}")
    print()


# ---------------------------------------------------------------------------
# 4. DEMO 3 — StoreBackend (Persistência Cross-Thread)
#
#    Arquivos são armazenados no InMemoryStore (ou PostgresStore em produção).
#    Sobrevivem a troca de thread_id — qualquer sessão pode ler.
#    Ideal para dados que precisam ser acessados em sessões futuras.
# ---------------------------------------------------------------------------

def demo_store_backend():
    """
    StoreBackend: arquivos persistem entre threads diferentes.
    Qualquer sessão com acesso ao mesmo Store pode ler os arquivos.
    """
    print("\n" + "=" * 65)
    print("  DEMO 3: StoreBackend (Cross-Thread Persistence)")
    print("=" * 65)
    print("  Arquivos sobrevivem a troca de thread_id.")
    print("  Thread 'manha' escreve → thread 'tarde' le.\n")

    store_rh = InMemoryStore()
    # Em produção: store_rh = PostgresStore(connection_string="postgresql://...")

    agente = create_deep_agent(
        model="gpt-4o-mini",
        tools=[analisar_curriculo],
        system_prompt="""
            Você é um Triador de Currículos com memória persistente.
            Salve todos os candidatos aprovados em /banco_candidatos/[nome].txt.
            Ao listar, use ls /banco_candidatos/ para ver todos os salvos.
        """,
        # StoreBackend: arquivos vão para o InMemoryStore, não para a RAM da thread
        backend=lambda rt: StoreBackend(rt),
        store=store_rh,
    )

    # SESSÃO 1 (manhã): Triagem inicial
    config_manha = {"configurable": {"thread_id": "rh-store-manha"}, "callbacks": [langfuse_handler]}
    result_manha = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analise e salve no banco: "
                        "Nome: Julia Santos, 7 anos de experiência, "
                        "habilidades: Python, LLM, LangChain, ML, Cloud. "
                        "Vaga: Tech Lead de IA."
                    ),
                }
            ]
        },
        config=config_manha,
    )
    print("[Sessao 'manha'] Candidato avaliado e salvo.")
    pprint.pprint(result_manha)

    # SESSÃO 2 (tarde): Thread completamente diferente — mas acessa o mesmo Store
    config_tarde = {"configurable": {"thread_id": "rh-store-tarde-nova-sessao"}, "callbacks": [langfuse_handler]}
    result_tarde = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Liste todos os candidatos salvos no banco /banco_candidatos/.",
                }
            ]
        },
        config=config_tarde,
    )
    print("[Sessao 'tarde' — thread diferente] Lendo banco de candidatos:")
    # print(result_tarde["messages"][-1].content)
    pprint.pprint(result_tarde)
    print("\n  OBSERVE: a sessao 'tarde' leu dados gravados pela sessao 'manha'.")
    print("  Isso e o StoreBackend: persistencia alem do thread_id.\n")


# ---------------------------------------------------------------------------
# 5. DEMO 4 — CompositeBackend (Roteamento Híbrido)
#
#    Combina backends diferentes para caminhos diferentes.
#    Roteamento por prefixo mais longo (longest prefix match).
#
#    /rascunhos/*       → StateBackend  (trabalho temporário, descartável)
#    /banco_aprovados/* → StoreBackend  (candidatos aprovados, permanente)
#    /resto/*           → StateBackend  (default)
# ---------------------------------------------------------------------------

def demo_composite_backend():
    """
    CompositeBackend: cada caminho roteia para um backend diferente.
    O agente usa o sistema de arquivos naturalmente — o harness decide onde armazenar.
    """
    print("\n" + "=" * 65)
    print("  DEMO 4: CompositeBackend (Hybrid Routing)")
    print("=" * 65)
    print("  /rascunhos/       → StateBackend  (efemero)")
    print("  /banco_aprovados/ → StoreBackend  (persistente)")
    print("  Mesmo agente, comportamento diferente por caminho.\n")

    store_aprovados = InMemoryStore()

    def backend_hibrido(runtime):
        return CompositeBackend(
            default=StateBackend(runtime),                            # tudo é efêmero por padrão
            routes={"/banco_aprovados/": StoreBackend(runtime)},      # exceto esta pasta
        )

    agente = create_deep_agent(
        model="gpt-4o-mini",
        tools=[analisar_curriculo],
        system_prompt="""
            Você é um Triador de Currículos com sistema híbrido de armazenamento.

            REGRAS DE ARMAZENAMENTO:
            - Rascunhos e notas temporárias: salve em /rascunhos/ (não persistem)
            - Candidatos APROVADOS (score >= 50): salve em /banco_aprovados/[nome].txt
            - Candidatos reprovados: salve apenas em /rascunhos/ (descartável)

            Após avaliar, confirme em qual pasta cada candidato foi salvo.
        """,
        backend=backend_hibrido,
        store=store_aprovados,
    )

    config_1 = {"configurable": {"thread_id": "rh-composite-sessao-1"}, "callbacks": [langfuse_handler]}

    result = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Avalie os dois candidatos:\n"
                        "1) Pedro Alves: 1 ano de experiência, habilidades: Excel, Word. Vaga: Eng. IA Sênior.\n"
                        "2) Maria Oliveira: 8 anos de experiência, habilidades: Python, LLM, LangChain, SQL, Cloud. Vaga: Eng. IA Sênior."
                    ),
                }
            ]
        },
        config=config_1,
    )
    print("[Sessao 1] Avaliacao e armazenamento:")
    print(result["messages"][-1].content)

    # Sessão 2: Apenas aprovados são visíveis (StoreBackend)
    config_2 = {"configurable": {"thread_id": "rh-composite-sessao-2-nova"}, "callbacks": [langfuse_handler]}
    result2 = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Liste /banco_aprovados/ e /rascunhos/ para ver o que persiste.",
                }
            ]
        },
        config=config_2,
    )
    print("\n[Sessao 2 — nova thread] Verificando o que persiste:")
    print(result2["messages"][-1].content)
    print("\n  OBSERVE: /banco_aprovados/ tem dados, /rascunhos/ esta vazia.")
    print("  CompositeBackend roteou corretamente cada arquivo.\n")


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Execute cada demo individualmente para ver o comportamento de cada backend.
    # Comente/descomente conforme necessário.

    #demo_state_backend()       # Demo 1: StateBackend (padrão)
    #demo_filesystem_backend()  # Demo 2: FilesystemBackend (cria arquivos reais em disco)
    demo_store_backend()       # Demo 3: StoreBackend (cross-thread)
    #demo_composite_backend()   # Demo 4: CompositeBackend (híbrido)
