"""Módulo 01 · Script 03: a mesma pergunta, decidida por um LLM com structured output.

Pergunta-chave do módulo: por que gerar texto para responder uma pergunta de múltipla escolha?

O LLM recebe a MESMA `DecisionSpec` (regra de ouro do bloco: não existe prompt por modelo),
devolve JSON via `with_structured_output` e uma confiança autorrelatada. Medimos tempo,
tokens, custo e se o JSON veio válido, lado a lado com o modelo de decisão.

Rode: python 01-decision-fundamentals/03_llm_same_question.py
Troque o LLM com DECISION_LLM=openai:gpt-5.6-luna (precisa de gravação ou modo live).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.evaluation import print_table
from common.providers import default_llm, get_client
from common.providers.llm import build_messages
from common.providers.replay import ReplayMissError
from common.specs import FILA

state = {"ticket": "Fui cobrado duas vezes na fatura de setembro. Preciso que estornem o valor duplicado ainda hoje."}

print("O que o LLM recebe, montado a partir da mesma spec:\n")
for message in build_messages(state, [FILA]):
    print(f"[{message.type}]\n{message.content}\n")

rows = []
for target in ["jev", "laya", f"llm:{default_llm()}"]:
    try:
        result = get_client(target).decide(state, [FILA])
    except ReplayMissError:
        print(f"⚠️  sem gravação de '{target}' para esta pergunta; pulando.")
        continue
    answer = result.answers.get("fila")
    rows.append(
        {
            "provider": result.provider + (" (sintético)" if result.synthetic else ""),
            "resposta": answer.value if answer else "—",
            "confiança": answer.confidence if answer else None,
            "tem distribuição?": "sim" if answer and answer.probabilities else "não",
            "latência_ms": result.latency_ms,
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
            "custo_usd": result.cost_usd,
            "JSON válido": result.parse_ok,
        }
    )

print_table(rows, "A mesma decisão por três caminhos")
print(
    "\nLeitura:"
    "\n- O LLM gera dezenas de tokens de saída para dizer uma palavra; o modelo de decisão, quase nenhum."
    "\n- A confiança do LLM é um número que ele escreveu, não uma probabilidade medida."
    "\n  O módulo 05 mede a diferença com ECE e diagrama de confiabilidade."
    "\n- O JSON do LLM pode vir quebrado ou com uma opção que não existe; o modelo de decisão"
    "\n  só consegue responder dentro das opções, por construção."
)
