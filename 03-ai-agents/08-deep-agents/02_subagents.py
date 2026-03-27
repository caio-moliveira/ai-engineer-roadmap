"""
02_subagents.py
===============
Subagentes com Deep Agents — Delegação Declarativa de Tarefas

Objetivo: mostrar como o Deep Agents abstrai toda a complexidade de criar
subagentes paralelos. Sem tool_call_id manual, sem ToolRuntime, sem threading
manual — apenas definições declarativas e a tool task() embutida.

Conceitos demonstrados:
  1. Subagente "general-purpose" (embutido, zero configuração)
  2. Subagentes customizados com ferramentas e modelos diferentes
  3. Modelos econômicos para tarefas analíticas vs modelos capazes para escrita
  4. Isolamento de contexto: o subagente não "polui" a memória do agente principal
  5. Passagem de resultado entre subagentes via filesystem do agente (/analises/)

Caso de uso real: pipeline de análise e resposta a propostas comerciais B2B
  Empresa recebe proposta de fornecedor → especialistas analisam → resposta redigida
"""

import os
import pprint
from dotenv import load_dotenv
from langchain.tools import tool
from deepagents import create_deep_agent

load_dotenv()


# ---------------------------------------------------------------------------
# 1. FERRAMENTAS ESPECIALIZADAS POR DOMÍNIO
#
#    Cada subagente só tem acesso às tools do seu domínio.
#    Isso evita que o agente financeiro mexa em cláusulas jurídicas e vice-versa.
# ---------------------------------------------------------------------------

@tool
def calcular_viabilidade_financeira(
    valor_proposta: float,
    economia_mensal_estimada: float,
    prazo_contrato_meses: int,
) -> str:
    """
    Calcula a viabilidade financeira de uma proposta: ROI, payback e economia total.

    valor_proposta        : custo total da proposta em R$
    economia_mensal_estimada: economia/ganho mensal esperado em R$
    prazo_contrato_meses  : duração do contrato em meses
    """
    economia_total = economia_mensal_estimada * prazo_contrato_meses
    lucro_liquido = economia_total - valor_proposta
    roi_percentual = (lucro_liquido / valor_proposta) * 100 if valor_proposta > 0 else 0
    payback_meses = valor_proposta / economia_mensal_estimada if economia_mensal_estimada > 0 else 999

    status = "VIAVEL" if roi_percentual > 20 and payback_meses <= prazo_contrato_meses else "QUESTIONAVEL"

    return (
        f"[ANALISE FINANCEIRA]\n"
        f"Investimento    : R$ {valor_proposta:,.2f}\n"
        f"Economia Total  : R$ {economia_total:,.2f}\n"
        f"Lucro Liquido   : R$ {lucro_liquido:,.2f}\n"
        f"ROI             : {roi_percentual:.1f}%\n"
        f"Payback         : {payback_meses:.1f} meses\n"
        f"Veredicto       : {status}"
    )


@tool
def buscar_cases_referencia(setor: str, tipo_solucao: str) -> str:
    """
    Busca cases de referência e benchmarks de mercado para justificar ou questionar a proposta.
    Use para embasar o parecer financeiro com dados de mercado.
    """
    cases = {
        "tecnologia": {
            "erp": "Média de mercado: R$ 80k-200k para PMEs. ROI médio 18 meses. Casos Totvs/SAP.",
            "cloud": "Migração cloud: redução média de 30% em infra. AWS/Azure médio R$ 15k/mês PMEs.",
            "segurança": "SOC/MDR: mercado R$ 8k-25k/mês. Redução de 70% em incidentes (Gartner 2024).",
        },
        "consultoria": {
            "gestao": "Projetos gestão: R$ 50k-500k. ROI típico 2-3x em 12 meses se bem executado.",
            "rh": "Consultoria RH: R$ 30k-120k. Redução de 25% em turnover como benchmark.",
        },
    }
    setor_lower = setor.lower()
    tipo_lower = tipo_solucao.lower()

    for s_key, tipos in cases.items():
        if s_key in setor_lower:
            for t_key, data in tipos.items():
                if t_key in tipo_lower:
                    return f"[BENCHMARK: {setor} / {tipo_solucao}]\n{data}"
            return f"[BENCHMARK: {setor}]\nNenhum case específico. Solicitar referências ao fornecedor."

    return "[BENCHMARK] Setor não mapeado. Recomenda-se validar com pesquisa de mercado independente."


@tool
def verificar_riscos_contratuais(clausulas_texto: str) -> str:
    """
    Analisa texto de cláusulas contratuais e identifica riscos jurídicos e operacionais.
    Retorna lista de pontos de atenção e recomendações.
    """
    # Simulação de análise jurídica. Em produção: RAG em base de contratos ou LLM especializado.
    riscos_identificados = []
    alertas_alto = []

    texto_lower = clausulas_texto.lower()

    if "exclusividade" in texto_lower:
        alertas_alto.append("EXCLUSIVIDADE: Avaliar impacto competitivo antes de assinar.")
    if "reajuste" in texto_lower and "anual" not in texto_lower:
        riscos_identificados.append("REAJUSTE: Cláusula de reajuste sem periodicidade definida — risco de aumento arbitrário.")
    if "multa rescisória" in texto_lower or "multa rescisoria" in texto_lower:
        riscos_identificados.append("MULTA RESCISÓRIA: Verificar percentual — padrão de mercado é 20-30% do valor restante.")
    if "dados" in texto_lower and "lgpd" not in texto_lower:
        alertas_alto.append("LGPD: Contrato menciona dados mas sem referência à LGPD — risco de compliance.")
    if "sla" not in texto_lower and "nível de serviço" not in texto_lower:
        riscos_identificados.append("SLA: Nenhum acordo de nível de serviço identificado — incluir antes de assinar.")

    if not riscos_identificados and not alertas_alto:
        return "[ANALISE JURIDICA]\nNenhum risco crítico identificado. Revisão formal por advogado recomendada antes da assinatura."

    resultado = "[ANALISE JURIDICA]\n"
    if alertas_alto:
        resultado += "ALERTAS CRITICOS:\n" + "\n".join(f"  !! {a}" for a in alertas_alto) + "\n"
    if riscos_identificados:
        resultado += "PONTOS DE ATENCAO:\n" + "\n".join(f"  -> {r}" for r in riscos_identificados)
    return resultado


# ---------------------------------------------------------------------------
# 2. DEFINIÇÃO DOS SUBAGENTES
#
#    A "mágica" acontece aqui: ao invés de criar StateGraph + nodes + edges
#    manualmente (como nos módulos 4-6), declaramos os subagentes como dicts.
#    O Deep Agents cria as threads secundárias automaticamente.
#
#    REGRA DE OURO: Subagentes são STATELESS — cada chamada via task() é
#    uma nova conversa. Passe TODAS as informações necessárias na instrução.
# ---------------------------------------------------------------------------

subagentes_proposta = [
    {
        # Analista financeiro: modelo econômico, trabalho analítico/calculístico
        "name": "analista_financeiro",
        "description": (
            "Especialista em análise financeira de propostas comerciais. "
            "Calcula ROI, payback, viabilidade e busca benchmarks de mercado. "
            "Salva o parecer financeiro em /analises/financeiro.md"
        ),
        "model": "gpt-4o-mini",   # Análise numérica não exige o modelo mais caro
        "system_prompt": """
            Você é um Analista Financeiro Sênior especializado em avaliação de propostas B2B.

            Para cada proposta recebida:
            1. Extraia os valores numéricos da proposta
            2. Use calcular_viabilidade_financeira com os dados encontrados
            3. Use buscar_cases_referencia para contextualizar com o mercado
            4. Salve o parecer completo em /analises/financeiro.md
            5. Retorne um resumo executivo do veredicto financeiro

            Seja objetivo. ROI abaixo de 15% ou payback acima de 24 meses são sinais de alerta.
        """,
        "tools": [calcular_viabilidade_financeira, buscar_cases_referencia],
    },
    {
        # Analista jurídico: modelo econômico, análise de riscos
        "name": "analista_juridico",
        "description": (
            "Especialista em análise de riscos contratuais e compliance. "
            "Identifica cláusulas problemáticas, riscos de LGPD e SLA. "
            "Salva o parecer jurídico em /analises/juridico.md"
        ),
        "model": "gpt-4o-mini",
        "system_prompt": """
            Você é um Analista Jurídico especializado em contratos B2B e compliance.

            Para cada proposta recebida:
            1. Extraia as cláusulas e condições contratuais relevantes
            2. Use verificar_riscos_contratuais com o texto das cláusulas
            3. Adicione sua análise qualitativa sobre os riscos
            4. Salve o parecer em /analises/juridico.md
            5. Retorne um resumo dos principais pontos de atenção

            Seja criterioso. É melhor sinalizar um falso positivo do que deixar passar um risco real.
        """,
        "tools": [verificar_riscos_contratuais],
    },
    {
        # Redator de resposta: modelo mais capaz, escrita executiva
        "name": "redator_resposta",
        "description": (
            "Redige a resposta formal da empresa ao fornecedor com base nos pareceres "
            "financeiro e jurídico. Tom executivo, direto e profissional."
        ),
        "model": "gpt-4o",        # Escrita executiva exige qualidade — vale o custo
        "system_prompt": """
            Você é o Redator de Comunicações Executivas da empresa.

            Para redigir a resposta à proposta:
            1. Leia os pareceres em /analises/financeiro.md e /analises/juridico.md
            2. Redija um email executivo formal com:
               - Agradecimento pela proposta
               - Posicionamento claro (aceitar / rejeitar / negociar)
               - Justificativa baseada nos pareceres (sem expor todos os detalhes internos)
               - Próximos passos concretos
            3. Tom: profissional, respeitoso e direto. Máximo 3 parágrafos.
            4. Salve a resposta em /analises/resposta_email.md e retorne o texto completo.
        """,
        "tools": [],   # Usa apenas ferramentas de filesystem embutidas (read_file, write_file)
    },
]


# ---------------------------------------------------------------------------
# 3. AGENTE ORQUESTRADOR
#
#    O agente principal conhece todos os subagentes e delega via task().
#    Ele não executa as análises — coordena quem executa.
# ---------------------------------------------------------------------------

agente_propostas = create_deep_agent(
    name="gestor-propostas-comerciais",
    model="gpt-4o",
    tools=[],   # Sem tools próprias — delega tudo aos subagentes
    subagents=subagentes_proposta,
    system_prompt="""
    Você é o Gestor de Propostas Comerciais da empresa. Sua função é COORDENAR, não executar.

    Para cada proposta recebida:

    PASSO 1 — ANÁLISE PARALELA (delegue AMBOS simultaneamente se possível):
      - task(agent="analista_financeiro", instruction="[instrução completa com os dados da proposta]")
      - task(agent="analista_juridico",   instruction="[instrução completa com as cláusulas da proposta]")

    PASSO 2 — RESPOSTA:
      - task(agent="redator_resposta", instruction="Redija a resposta baseada nos pareceres salvos em /analises/")

    PASSO 3 — SÍNTESE:
      - Leia /analises/resposta_email.md
      - Apresente ao usuário: veredicto final (aprovar/rejeitar/negociar) + email redigido

    LEMBRETE CRÍTICO SOBRE SUBAGENTES:
      Os subagentes são STATELESS. Cada chamada task() começa do zero.
      Inclua TODAS as informações relevantes na instrução — eles não têm memória de chamadas anteriores.
    """,
)


# ---------------------------------------------------------------------------
# 4. EXECUÇÃO E DEMONSTRAÇÃO
# ---------------------------------------------------------------------------

PROPOSTA_EXEMPLO = """
PROPOSTA COMERCIAL — Sistema de Gestão ERP Cloud

Fornecedor: TechSoft Soluções Ltda
Data: Março 2025

ESCOPO:
Implementação de ERP cloud completo para gestão financeira, RH e operações.
Inclui migração de dados, treinamento e suporte 24h por 12 meses.

VALORES:
- Implantação: R$ 85.000 (pagamento único)
- Licença mensal: R$ 4.500/mês
- Suporte adicional: R$ 1.200/mês
- Total 12 meses: R$ 151.400

BENEFÍCIOS ESTIMADOS PELO FORNECEDOR:
- Redução de 40% no tempo de fechamento contábil
- Economia estimada: R$ 18.000/mês em horas de trabalho manual

CLÁUSULAS RELEVANTES:
- Contrato de exclusividade tecnológica por 24 meses
- Multa rescisória de 50% do valor restante
- Reajuste pelo IGPM sem periodicidade definida
- Dados dos colaboradores armazenados em servidor do fornecedor (sem menção à LGPD)
- Nenhum SLA formal de disponibilidade do sistema
"""


def analisar_proposta():
    config = {"configurable": {"thread_id": "proposta-techsoft-marco-2025"}}

    print("=" * 65)
    print("  GESTOR DE PROPOSTAS COMERCIAIS — Deep Agents")
    print("=" * 65)
    print("\n[INPUT] Proposta recebida. Iniciando análise multidisciplinar...\n")

    response = agente_propostas.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Analise a proposta abaixo e me diga se devemos aceitar, "
                        f"rejeitar ou negociar. Prepare também o email de resposta.\n\n"
                        f"{PROPOSTA_EXEMPLO}"
                    ),
                }
            ]
        },
        config=config,
    )

    print("\n[RESULTADO FINAL DO GESTOR]")
    print("-" * 65)

    pprint.pprint(response)
    # print(response["messages"][-1].content)

    # # Mostra o plano de tarefas se o agente usou o TodoListMiddleware
    # todos = response.get("todos", [])
    # if todos:
    #     print("\n[PLANO DE EXECUCAO]")
    #     icons = {"completed": "[OK]", "in_progress": "[>>]", "pending": "[ ]"}
    #     for t in todos:
    #         print(f"  {icons.get(t['status'], '[?]')} {t['content']}")


if __name__ == "__main__":
    analisar_proposta()
