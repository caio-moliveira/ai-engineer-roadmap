"""Módulo 02 · Script 03: um Choice "barato / caro" antes do LLM.

A decisão de roteamento custa uma fração de centavo. Ela decide quanto da conta de geração
migra para o modelo barato e quanto risco você aceita mandando um caso difícil para ele.

Rode: python 02-choice-routing/03_model_routing.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden
from common.evaluation import prediction, print_table, run_targets, summarize
from common.pricing import cost_usd
from common.providers import compare_targets
from common.specs import ROTA

MODELO_BARATO = "claude-haiku-4-5-20251001"
MODELO_CARO = "claude-opus-5-5"

# PREMISSA explícita, não medição: tamanho médio de uma resposta de suporte gerada.
# Troque pelos números do seu tráfego (os tokens reais estão nos traces de produção).
PREMISSA_TOKENS_IN = 1_200
PREMISSA_TOKENS_OUT = 350

custo_barato = cost_usd(MODELO_BARATO, PREMISSA_TOKENS_IN, PREMISSA_TOKENS_OUT)
custo_caro = cost_usd(MODELO_CARO, PREMISSA_TOKENS_IN, PREMISSA_TOKENS_OUT)
print(f"Premissa por resposta: {PREMISSA_TOKENS_IN} tokens in, {PREMISSA_TOKENS_OUT} out")
print(f"  {MODELO_BARATO}: US$ {custo_barato:.5f}  |  {MODELO_CARO}: US$ {custo_caro:.5f}\n")

tickets = golden.load("tickets")
runs_by_target = run_targets(compare_targets(), tickets, [ROTA])
print_table([summarize(ROTA, runs) for runs in runs_by_target.values()], "Choice 'rota': acerto do roteador")

rows = []
n = len(tickets)
sempre_caro = n * custo_caro
for target, runs in runs_by_target.items():
    preds = [prediction(ROTA, r) for r in runs]
    barato = sum(p == "barato" for p in preds)
    geracao = sum(custo_barato if p == "barato" else custo_caro for p in preds)
    roteamento = sum(r.result.cost_usd or 0 for r in runs)
    rows.append(
        {
            "roteador": target,
            "% para o barato": f"{barato / n:.0%}",
            "custo_total_usd": geracao + roteamento,
            "economia vs sempre caro": f"{1 - (geracao + roteamento) / sempre_caro:.0%}",
            "difícil→barato (risco)": sum(p == "barato" and r.item.labels["rota"] == "caro" for p, r in zip(preds, runs)),
            "fácil→caro (desperdício)": sum(p == "caro" and r.item.labels["rota"] == "barato" for p, r in zip(preds, runs)),
        }
    )
rows.append({"roteador": "sempre caro (sem roteador)", "% para o barato": "0%", "custo_total_usd": sempre_caro,
             "economia vs sempre caro": "0%", "difícil→barato (risco)": 0, "fácil→caro (desperdício)": sum(t.labels["rota"] == "barato" for t in tickets)})
print_table(rows, f"Conta de geração para {n} tickets")

print(
    "\nO número que importa não é só a economia: é 'difícil→barato'. Cada um é um cliente"
    "\nprestes a sair recebendo resposta de modelo pequeno. Use a confiança do Choice:"
    "\nse P(barato) < limiar, mande para o caro. O módulo 05 escolhe esse limiar."
    "\n\nNo LangChain, o middleware experimental ModelRouterMiddleware faz exatamente isto dentro"
    "\nde um create_agent: veja 04_langchain_classifier.py."
)
