"""
04_skills.py
============
Skills e Progressive Disclosure — Capacidades Sob Demanda

Objetivo: entender como o Deep Agents carrega habilidades especializadas
progressivamente, apenas quando necessário. Isso resolve um problema real:
como dar ao agente conhecimento profundo em múltiplos domínios sem
explodir a janela de contexto com instruções que talvez nunca sejam usadas.

Conceitos demonstrados:
  1. SKILL.md: formato obrigatório com frontmatter YAML
  2. Progressive Disclosure: skill só é carregada quando o agente decide que precisa
  3. Múltiplas skills em diretórios separados (um por especialidade)
  4. FilesystemBackend: necessário para que o agente leia as skills do disco
  5. Diferença prática entre Skills e AGENTS.md (ver 05_memory.py)

ESTRUTURA DAS SKILLS (criadas em ./skills/):
  skills/
  ├── analise-financeira/
  │   └── SKILL.md    ← Diretrizes de análise financeira B2B
  └── email-executivo/
      └── SKILL.md    ← Framework de comunicação executiva

COMO FUNCIONA O CARREGAMENTO:
  1. O agente recebe uma tarefa
  2. Verifica quais skills estão disponíveis (lê a descrição do frontmatter)
  3. Decide quais skills são relevantes para a tarefa atual
  4. Carrega o SKILL.md completo apenas quando necessário
  5. Usa o conteúdo da skill para guiar a execução

Caso de uso real: Assistente Executivo de um CEO — analisa propostas financeiras
e redige respostas formais usando skills especializadas sob demanda
"""

import os
import pprint
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler()

# Diretório base deste arquivo — skills ficam em ./skills/ relativo a este arquivo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR  = os.path.join(CURRENT_DIR, "skills")

# ---------------------------------------------------------------------------
# CRIAÇÃO DO AGENTE COM SKILLS
#
#    Parâmetros essenciais para Skills funcionarem:
#
#    backend=FilesystemBackend(...)
#      → O agente precisa de acesso ao filesystem para LER os SKILL.md
#      → virtual_mode=True: sandboxing de segurança (sem path traversal)
#
#    skills=[SKILLS_DIR]
#      → Lista de diretórios onde o agente buscará SKILL.md files
#      → O agente lê o frontmatter (name + description) de todos os SKILL.md
#      → O conteúdo completo só é carregado quando a skill é ativada
#
#    checkpointer=MemorySaver()
#      → Necessário para manter o estado entre múltiplos turnos de conversa
# ---------------------------------------------------------------------------

assistente_executivo = create_deep_agent(
    name="assistente-executivo-ceo",
    model="gpt-4o",
    tools=[],   # Sem tools customizadas — toda a especialização vem das skills
    backend=FilesystemBackend(root_dir=CURRENT_DIR, virtual_mode=True),
    skills=[SKILLS_DIR],
    checkpointer=MemorySaver(),
    system_prompt="""
    Você é o Assistente Executivo de um CEO de empresa B2B de médio porte.

    Suas responsabilidades:
    - Analisar propostas financeiras e de negócios recebidas pela empresa
    - Redigir respostas e comunicações executivas em nome do CEO
    - Emitir pareceres fundamentados sobre decisões estratégicas

    SKILLS DISPONÍVEIS:
    Você tem acesso a skills especializadas carregadas sob demanda:
    - 'analise-financeira': framework completo para avaliar ROI, viabilidade e benchmarks
    - 'email-executivo': diretrizes para redigir comunicações profissionais de alto impacto

    QUANDO USAR CADA SKILL:
    - Para análise de números, ROI, custo-benefício → carregue 'analise-financeira'
    - Para redigir emails, comunicados, respostas formais → carregue 'email-executivo'
    - Para tarefas que envolvem ambos → carregue as duas skills

    Sempre que usar uma skill, diga explicitamente qual você está usando e por quê.
    Isso torna seu raciocínio transparente para o CEO.
    """,
)


# ---------------------------------------------------------------------------
# CENÁRIOS DE DEMONSTRAÇÃO
#
#    Cada cenário ativa uma skill diferente ou ambas.
#    Observe no output do agente qual skill ele decide carregar.
# ---------------------------------------------------------------------------

def demo_skill_analise_financeira():
    """
    Cenário 1: O CEO recebe uma proposta e quer análise financeira.
    O agente deve carregar a skill 'analise-financeira' automaticamente.
    """

    config = {"configurable": {"thread_id": "exec-skill-financeiro-001"}, "callbacks": [langfuse_handler]}

    proposta = """
    Proposta recebida: Sistema de BI e Analytics
    Fornecedor: DataVision Ltda

    Custos:
    - Implantação: R$ 45.000 (único)
    - Licença mensal: R$ 3.200/mês
    - Total 12 meses: R$ 83.400

    Benefícios estimados pelo fornecedor:
    - Economia de 80h/mês em geração de relatórios manuais
    - Custo médio hora analista: R$ 80/h
    - Economia mensal: R$ 6.400/mês
    """

    result = assistente_executivo.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Analise a viabilidade financeira desta proposta:\n{proposta}",
                }
            ]
        },
        config=config,
    )

    print("[ASSISTENTE]")
    print(result["messages"][-1].content)
    print()


def demo_skill_email_executivo():
    """
    Cenário 2: CEO quer recusar uma proposta com um email profissional.
    O agente deve carregar a skill 'email-executivo' automaticamente.
    """
    print("=" * 65)
    print("  SKILL DEMO 2: Email Executivo")
    print("=" * 65)
    print("  Esperado: agente carrega skill 'email-executivo'\n")

    config = {"configurable": {"thread_id": "exec-skill-email-001"}, "callbacks": [langfuse_handler]}

    result = assistente_executivo.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Preciso recusar a proposta da DataVision de forma profissional. "
                        "Os motivos são: ROI abaixo do esperado (menor que 20%) e "
                        "payback muito longo para o nosso momento financeiro. "
                        "Redija o email de resposta para o contato deles, Sr. Roberto Alves."
                    ),
                }
            ]
        },
        config=config,
    )

    print("[ASSISTENTE]")
    print(result["messages"][-1].content)
    print()


def demo_skills_combinadas():
    """
    Cenário 3: CEO quer análise + resposta em uma única solicitação.
    O agente deve carregar AMBAS as skills — Progressive Disclosure completo.
    """
    print("=" * 65)
    print("  SKILL DEMO 3: Skills Combinadas (analise + email)")
    print("=" * 65)
    print("  Esperado: agente carrega ambas as skills\n")

    config = {"configurable": {"thread_id": "exec-skill-combinado-001"}, "callbacks": [langfuse_handler]}

    proposta_completa = """
    Proposta: Plataforma de Gestão de Projetos SaaS
    Fornecedor: ProManage Solutions
    Contato: Dra. Fernanda Costa (diretora comercial)

    Custos: R$ 120.000/ano (all-inclusive)

    Benefícios estimados:
    - Redução de 30% em projetos atrasados
    - Economia de 60h/mês em reuniões de status
    - Custo médio hora gerente de projeto: R$ 120/h → economia: R$ 7.200/mês

    Prazo proposto: 24 meses com exclusividade de categoria
    """

    result = assistente_executivo.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Faça a análise financeira desta proposta e, com base nos resultados, "
                        f"redija o email de resposta para a Dra. Fernanda Costa:\n{proposta_completa}"
                    ),
                }
            ]
        },
        config=config,
    )

    print("[ASSISTENTE]")
    # print(result["messages"][-1].content)
    pprint.pprint(result)
    # Exibe o plano de tarefas (TodoListMiddleware)
    todos = result.get("todos", [])
    if todos:
        print("\n[PLANO DE TAREFAS]")
        icons = {"completed": "[OK]", "in_progress": "[>>]", "pending": "[ ]"}
        for t in todos:
            print(f"  {icons.get(t['status'], '[?]')} {t['content']}")
    print()


# ---------------------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Execute cada demo para ver o Progressive Disclosure em ação.
    # Observe no output qual skill o agente decide carregar para cada tarefa.

    #demo_skill_analise_financeira()    # Apenas skill financeira
    #demo_skill_email_executivo()     # Apenas skill de email
    demo_skills_combinadas()         # Ambas as skills combinadas
