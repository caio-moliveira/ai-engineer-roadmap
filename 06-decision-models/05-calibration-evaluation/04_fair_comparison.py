"""Módulo 05 · Script 04: o harness de comparação justa.

Mesma spec, mesmos dados, todos os providers. Tokens da resposta, latência do relógio,
preço de common/pricing.yaml. Exporta um CSV com uma linha por (tarefa, item, provider) para
você abrir no Excel/pandas e cortar por tag, dificuldade ou o que quiser.

Rode:
    python 05-calibration-evaluation/04_fair_comparison.py
    python 05-calibration-evaluation/04_fair_comparison.py --tarefas fila,spam --alvos laya,jev --limite 20
Em modo live, o harness estima o custo antes e pede --confirmar acima de US$ 1.

Este é o harness que todo módulo usa para medir. Para comparar um provider novo (outro LLM,
um Laya ajustado, qualquer servidor /v1/systemone), aponte DECISION_TARGETS para ele.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden
from common.decisions import DecisionSpec
from common.evaluation import confidence, prediction, print_table, run_targets, summarize
from common.pricing import PricingMissingError, cost_usd
from common.providers import compare_targets
from common.providers.replay import is_live, mode
from common.specs import FILA, GUARDRAIL, QUALIDADE, RELEVANCIA, ROTA, SPAM_DIRETO, TOOL, URGENCIA, VERIFICACAO

# tarefa -> (golden set, perguntas feitas JUNTAS numa chamada)
TAREFAS: dict[str, tuple[str, list[DecisionSpec]]] = {
    "fila": ("tickets", [FILA]),
    "urgencia": ("tickets", [URGENCIA]),
    "rota": ("tickets", [ROTA]),
    "spam": ("spam", [SPAM_DIRETO]),
    "tool": ("sales", [TOOL]),
    "guardrail": ("sales", GUARDRAIL),
    "verificacao": ("verify", VERIFICACAO),
    "qualidade": ("verify", [QUALIDADE]),
    "relevancia": ("rerank", [RELEVANCIA]),
}

parser = argparse.ArgumentParser(description="Harness de comparação justa entre providers de decisão")
parser.add_argument("--tarefas", default=",".join(TAREFAS), help=f"subconjunto de: {', '.join(TAREFAS)}")
parser.add_argument("--alvos", default=",".join(compare_targets()), help="ex.: jev,laya,llm:openai:gpt-5.6-luna")
parser.add_argument("--limite", type=int, default=None, help="no máximo N itens por tarefa (controle de custo)")
parser.add_argument("--csv", default=str(Path(__file__).resolve().parent / "saida" / "comparacao.csv"))
parser.add_argument("--confirmar", action="store_true", help="roda em live mesmo com estimativa acima de US$ 1")
args = parser.parse_args()

tarefas = [t.strip() for t in args.tarefas.split(",") if t.strip()]
alvos = [a.strip() for a in args.alvos.split(",") if a.strip()]
desconhecidas = set(tarefas) - set(TAREFAS)
if desconhecidas:
    sys.exit(f"tarefas desconhecidas: {sorted(desconhecidas)}")

# --- Estimativa de custo antes de gastar (só em live) ---------------------------------------
# Estimativa grosseira (4 caracteres por token, saída de LLM ~40 tokens por pergunta) só para
# o portão de orçamento. Os números do relatório vêm dos tokens reais da resposta.
estimativa = 0.0
for alvo in alvos:
    if not is_live(alvo):
        continue
    modelo = alvo.removeprefix("llm:").split(":", 1)[-1] if alvo.startswith("llm:") else ("jev-1.13.0" if alvo.startswith("jev") else "laya-rl-agent")
    for tarefa in tarefas:
        dataset, specs = TAREFAS[tarefa]
        for item in golden.load(dataset, limit=args.limite):
            chars = len(json.dumps(item.state, ensure_ascii=False)) + len(json.dumps([s.to_wire() for s in specs], ensure_ascii=False))
            try:
                estimativa += cost_usd(modelo, chars // 4, 40 * len(specs) if alvo.startswith("llm:") else 0)
            except PricingMissingError:
                pass
if estimativa:
    print(f"Estimativa de custo das chamadas live: ~US$ {estimativa:.2f}")
    if estimativa > 1 and not args.confirmar:
        sys.exit("Acima de US$ 1. Rode de novo com --confirmar, ou reduza com --limite.")

print(f"modo: {mode()} | alvos: {alvos} | tarefas: {tarefas} | limite: {args.limite or 'todos'}")

resumo, linhas = [], []
for tarefa in tarefas:
    dataset, specs = TAREFAS[tarefa]
    items = golden.load(dataset, limit=args.limite)
    print(f"\n▶ {tarefa}: {len(items)} itens de {dataset}, {len(specs)} pergunta(s) por chamada")
    for alvo, runs in run_targets(alvos, items, specs).items():
        for spec in specs:
            row = summarize(spec, runs)
            resumo.append({"tarefa": tarefa, "pergunta": spec.name, **row})
            for r in runs:
                a = r.result.answers.get(spec.name)
                linhas.append({
                    "tarefa": tarefa, "pergunta": spec.name, "item": r.item.id, "tags": "|".join(r.item.tags),
                    "provider": alvo, "sintetico": r.result.synthetic, "rotulo": r.item.labels[spec.name],
                    "previsao": prediction(spec, r), "valor": a.value if a else None, "confianca": confidence(spec, r),
                    "acerto": prediction(spec, r) == r.item.labels[spec.name],
                    "latency_ms": round(r.result.latency_ms, 1), "tokens_in": r.result.tokens_in,
                    "tokens_out": r.result.tokens_out, "cost_usd": r.result.cost_usd,
                    "parse_ok": r.result.parse_ok, "values_in_schema": r.result.values_in_schema,
                })

colunas = ["tarefa", "pergunta", "provider", "n", "acurácia", "f1_macro", "brier", "ece", "p95_ms", "custo_1k_usd", "falha_formato"]
print_table([{k: row[k] for k in colunas} for row in resumo], "Resumo do harness")

if linhas:
    destino = Path(args.csv)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas[0]))
        writer.writeheader()
        writer.writerows(linhas)
    print(f"\n{len(linhas)} linhas exportadas para {destino}")

if any(r["provider"].endswith("(sintético)") for r in resumo):
    print("\n⚠️  Linhas '(sintético)' vêm de fixtures sintéticas: ilustram o formato, não medem o modelo.")
print(
    "\nO bloco não conclui qual provider é melhor. O harness mede; a conclusão é sua, no seu caso:"
    "\nqual acurácia o negócio exige, quanto custa cada erro, qual latência cabe no fluxo."
)
