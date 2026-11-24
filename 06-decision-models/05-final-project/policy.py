"""A política do agente: limiares e regras de negócio, escritos e versionados pela equipe.

O Jev devolve valores e probabilidades; quem decide o que fazer com eles é este arquivo. Cada
função recebe a resposta de um nó e devolve uma decisão com o motivo em texto, que aparece na
trilha de decisões do frontend.

Ao mudar um limiar, pense nos dois erros: o que acontece quando ele erra para cima e para baixo.
"""

from dataclasses import dataclass

from typesafe_sdk import SystemOneResponse

# --- Roteador ------------------------------------------------------------------------------------
LIMIAR_AMBIGUA = 0.6  # P(ambígua) acima disso: pede esclarecimento em vez de chutar
LIMIAR_COMPLEXIDADE = 0.9  # complexidade esperada (0 a 2) acima disso: modelo grande

# --- Guardião ------------------------------------------------------------------------------------
LIMIAR_INJECAO = 0.5  # P(injeção) acima disso: bloqueia, sem discussão
LIMIAR_CONFIANCA = 0.7  # P do veredito abaixo disso, numa ação de risco: pausa para um humano decidir
LIMIAR_RISCO = 1.4  # risco esperado (0 a 2) acima disso, numa ação irreversível: pede aprovação
LIMIAR_IRREVERSIVEL = 0.5
LIMITE_REEMBOLSO_AUTOMATICO = 200.0  # regra de negócio: reembolso acima disso sempre pede aprovação

# --- Juiz ----------------------------------------------------------------------------------------
LIMIAR_SUSTENTADA = 0.6  # P(sustentada) mínima para entregar
LIMIAR_COMPLETUDE = 1.4  # completude esperada (0 a 2) mínima para entregar
MAX_TENTATIVAS = 2  # depois disso, a resposta sai com aviso de baixa confiança

# --- Agente --------------------------------------------------------------------------------------
MAX_PASSOS = 8  # ações propostas por pergunta; ao chegar aqui, o agente é obrigado a responder


@dataclass
class Decisao:
    rota: str
    motivo: str


def politica_roteador(r: SystemOneResponse, modelo_inicial: str) -> tuple[Decisao, str]:
    """Devolve a rota (esclarecer ou agente) e o tamanho do modelo (pequeno ou grande)."""
    p_ambigua = r.nouls["ambigua"].noul
    complexidade = r.scores["complexidade"].score
    intencao = r.choices["intencao"].choice

    # Conversa vai direto ao agente (que responde sem ferramentas): "oi, tudo bem?" não precisa
    # de esclarecimento. A ambiguidade só pesa quando há dado a buscar ou ação a executar.
    if intencao != "conversa" and p_ambigua >= LIMIAR_AMBIGUA:
        return Decisao("esclarecer", f"ambígua (P={p_ambigua:.2f})"), "pequeno"

    if modelo_inicial in ("pequeno", "grande"):
        return Decisao("agente", f"{intencao}; modelo {modelo_inicial} forçado na requisição"), modelo_inicial

    tamanho = "grande" if complexidade > LIMIAR_COMPLEXIDADE else "pequeno"
    return Decisao("agente", f"{intencao}, complexidade {complexidade:.2f} → modelo {tamanho}"), tamanho


def politica_guardiao(r: SystemOneResponse, acao: str, argumentos: dict, acao_de_risco: bool) -> Decisao:
    """Devolve permitir, aprovacao (pausa para um humano) ou bloquear."""
    p_injecao = r.nouls["injecao"].noul
    p_irreversivel = r.nouls["irreversivel"].noul
    risco = r.scores["risco"].score
    veredito = r.choices["veredito"]
    p_veredito = _prob(veredito)

    if p_injecao >= LIMIAR_INJECAO:
        return Decisao("bloquear", f"instrução injetada (P={p_injecao:.2f})")
    # Leitura não muda nada: só a injeção bloqueia. Pedir aprovação para ler dados só atrapalha.
    if not acao_de_risco:
        return Decisao("permitir", f"leitura, risco {risco:.2f}")
    if p_veredito < LIMIAR_CONFIANCA:
        return Decisao("aprovacao", f"veredito incerto ({veredito.choice}, P={p_veredito:.2f})")
    if veredito.choice == "bloquear":
        return Decisao("bloquear", f"guardião bloqueou (P={p_veredito:.2f})")

    valor = _como_numero(argumentos.get("valor"))
    if acao == "reembolsar_cliente" and valor is not None and valor > LIMITE_REEMBOLSO_AUTOMATICO:
        return Decisao("aprovacao", f"reembolso de R$ {valor:.2f} acima do limite automático")
    if veredito.choice == "pedir_aprovacao":
        return Decisao("aprovacao", f"guardião pediu aprovação (P={p_veredito:.2f})")
    if p_irreversivel >= LIMIAR_IRREVERSIVEL and risco > LIMIAR_RISCO:
        return Decisao("aprovacao", f"irreversível (P={p_irreversivel:.2f}) e risco {risco:.2f}")
    return Decisao("permitir", f"risco {risco:.2f}")


def politica_juiz(r: SystemOneResponse, tentativa: int) -> Decisao:
    """Devolve entregar, refazer (volta ao roteador com o modelo grande) ou aviso."""
    p_sustentada = r.nouls["sustentada"].noul
    completude = r.scores["completude"].score
    veredito = r.choices["veredito"]

    if p_sustentada >= LIMIAR_SUSTENTADA and completude >= LIMIAR_COMPLETUDE:
        return Decisao("entregar", f"sustentada {p_sustentada:.2f}, completude {completude:.2f}")

    falha = f"sustentada {p_sustentada:.2f}, completude {completude:.2f}"
    if veredito.choice == "escalar" and _prob(veredito) >= LIMIAR_CONFIANCA:
        return Decisao("aviso", f"{falha}; juiz escalou (P={_prob(veredito):.2f})")
    if tentativa < MAX_TENTATIVAS:
        return Decisao("refazer", f"{falha}; tentativa {tentativa} de {MAX_TENTATIVAS}")
    return Decisao("aviso", f"{falha}; acabaram as tentativas")


def _prob(answer) -> float:
    """Probabilidade da opção escolhida num Choice: a mesma que aparece na trilha."""
    return answer.probabilities.get(answer.choice, answer.confidence)


def _como_numero(valor) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None
