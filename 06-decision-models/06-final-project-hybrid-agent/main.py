"""Projeto final: agente híbrido medido ponta a ponta.

Rode de dentro da pasta do projeto (imports flat, como o projeto final do Bloco 4):
    cd 06-decision-models/06-final-project-hybrid-agent
    python main.py "Qual região vendeu mais em 2026?"     # uma pergunta (precisa de gravação ou live)
    python main.py --lote                                 # golden set de vendas, providers do config.yaml
    python main.py --comparar                             # o agente inteiro com cada provider, lado a lado
    python main.py --lote --limite 20

O relatório vai para saida/relatorio.md: custo, latência p95, acurácia e concordância.
"""

import argparse
import copy
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from graph import build_graph, load_config

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden, metrics
from common.evaluation import print_table
from common.providers import compare_targets, mode
from common.providers.replay import ReplayMissError
from common.specs import GUARDRAIL

SAIDA = Path(__file__).resolve().parent / "saida"
AUTOMATIZADOS = {"bloqueada", "sem_dado", "aprovada"}


def rodar(config: dict, perguntas) -> list[tuple]:
    graph = build_graph(config)
    saidas = []
    for i, p in enumerate(perguntas, 1):
        saidas.append((p, graph.invoke({"pergunta": p.state["pergunta"]})))
        if i % 20 == 0:
            print(f"  {i}/{len(perguntas)}")
    return saidas


def relatorio(nome: str, saidas: list[tuple]) -> dict:
    n = len(saidas)
    ataque = [any(p.labels[s.name] for s in GUARDRAIL) for p, _ in saidas]
    bloqueou = [o.get("desfecho") == "bloqueada" for _, o in saidas]
    passaram = [(p, o) for p, o in saidas if o.get("desfecho") != "bloqueada" and o.get("tool") is not None]
    chamadas = [c for _, o in saidas for c in o.get("chamadas", [])]
    decisoes = [c for c in chamadas if c["tipo"] == "decisão"]
    geracoes = [c for c in chamadas if c["tipo"] == "geração"]
    lat_decisoes = [sum(c["latency_ms"] for c in o.get("chamadas", []) if c["tipo"] == "decisão") for _, o in saidas]
    desfechos = Counter(o.get("desfecho") for _, o in saidas)
    precision, recall = metrics.precision_recall(ataque, bloqueou)
    return {
        "configuração": nome + (" (sintético)" if any(c["synthetic"] for c in decisoes) else ""),
        "n": n,
        "guardrail recall": recall,
        "guardrail FPR": metrics.false_positive_rate(ataque, bloqueou),
        "triagem acurácia": metrics.accuracy([p.labels["tool"] for p, _ in passaram], [o["tool"] for _, o in passaram]) if passaram else None,
        "automatizado": sum(desfechos[d] for d in AUTOMATIZADOS) / n,
        "decisões p95_ms": metrics.p95(lat_decisoes),
        "geração p95_ms": metrics.p95([c["latency_ms"] for c in geracoes]) if geracoes else None,
        "decisões US$/1k": sum(c["cost_usd"] for c in decisoes) / n * 1000,
        "geração US$/1k": sum(c["cost_usd"] for c in geracoes) / n * 1000,
        "desfechos": dict(desfechos),
    }


def uma_pergunta(pergunta: str) -> None:
    try:
        out = build_graph().invoke({"pergunta": pergunta})
    except ReplayMissError:
        sys.exit("Essa pergunta não tem gravação. Rode com DECISION_PROVIDER=live (precisa das chaves e do Laya).")
    for c in out.get("chamadas", []):
        extra = c.get("respostas", "")
        print(f"[{c['node']:<11}] {c['provider']:<45} {c['latency_ms']:7.0f} ms  US$ {c['cost_usd']:.6f}  {extra}")
    print(f"\ndesfecho: {out.get('desfecho')}\n\n{out.get('resposta')}")


parser = argparse.ArgumentParser()
parser.add_argument("pergunta", nargs="?")
parser.add_argument("--lote", action="store_true")
parser.add_argument("--comparar", action="store_true")
parser.add_argument("--limite", type=int)
args = parser.parse_args()

if args.pergunta:
    uma_pergunta(args.pergunta)
    sys.exit()

config = load_config()
perguntas = golden.load("sales", limit=args.limite)
print(f"modo {mode()} | {len(perguntas)} perguntas | geração: {config['geracao']}")
linhas, por_alvo = [], {}

if args.lote or not args.comparar:
    print(f"\n▶ config.yaml: {config['providers']}")
    try:
        saidas = rodar(config, perguntas)
        linhas.append(relatorio("config.yaml", saidas))
    except ReplayMissError as error:
        print(f"⚠️  sem gravação para a configuração atual: {str(error).splitlines()[0]}")

if args.comparar:
    for alvo in compare_targets():
        cfg = copy.deepcopy(config)
        cfg["providers"] = {node: alvo for node in cfg["providers"]}
        print(f"\n▶ todas as decisões em {alvo}")
        try:
            por_alvo[alvo] = rodar(cfg, perguntas)
        except ReplayMissError as error:
            print(f"⚠️  pulando {alvo}: {str(error).splitlines()[0]}")
            continue
        linhas.append(relatorio(alvo, por_alvo[alvo]))

tabela = [{k: v for k, v in linha.items() if k != "desfechos"} for linha in linhas]
print_table(tabela, "Agente híbrido: guardrail, triagem, geração e verificação")
for linha in linhas:
    print(f"  {linha['configuração']}: {linha['desfechos']}")

concordancia = []
for a, b in combinations(por_alvo, 2):
    tools_a = [o.get("tool") for _, o in por_alvo[a]]
    tools_b = [o.get("tool") for _, o in por_alvo[b]]
    block_a = [o.get("desfecho") == "bloqueada" for _, o in por_alvo[a]]
    block_b = [o.get("desfecho") == "bloqueada" for _, o in por_alvo[b]]
    concordancia.append({"A": a, "B": b, "concordância bloqueio": metrics.agreement(block_a, block_b),
                         "concordância tool": metrics.agreement(tools_a, tools_b),
                         "kappa tool": metrics.cohen_kappa(tools_a, tools_b)})
if concordancia:
    print_table(concordancia, "Concordância entre providers")

if linhas:
    SAIDA.mkdir(exist_ok=True)
    from tabulate import tabulate

    texto = ["# Relatório do agente híbrido", "", f"Modo: {mode()}. Perguntas: {len(perguntas)}. Geração: {config['geracao']}.", "",
             tabulate(tabela, headers="keys", tablefmt="github", floatfmt=".3f"), ""]
    if concordancia:
        texto += ["## Concordância", "", tabulate(concordancia, headers="keys", tablefmt="github", floatfmt=".3f"), ""]
    texto += ["## Limiares usados", "", *[f"- {k}: {v}" for k, v in config["limiares"].items()], "",
              "Justifique cada limiar com a curva do módulo 05 antes de entregar."]
    (SAIDA / "relatorio.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(f"\nRelatório salvo em {SAIDA / 'relatorio.md'}")
