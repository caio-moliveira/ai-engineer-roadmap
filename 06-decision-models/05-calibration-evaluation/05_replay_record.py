"""Módulo 05 · Script 05: grava as fixtures que fazem o bloco rodar sem chave.

Roda cada script do bloco com DECISION_PROVIDER=record. Os alvos pedidos são chamados de
verdade e cada resposta vira um arquivo em fixtures/<alvo>/<chave>.json. Os demais alvos
continuam em replay. O que já foi gravado é reaproveitado (use --forcar para regravar).

Rode (da pasta 06-decision-models):
    python 05-calibration-evaluation/05_replay_record.py                     # detecta o que está disponível
    python 05-calibration-evaluation/05_replay_record.py --alvos jev         # só o Jev (precisa de TYPESAFE_API_KEY)
    python 05-calibration-evaluation/05_replay_record.py --alvos laya --scripts 02-choice-routing/01_classify_tickets.py

Depois de gravar, faça um commit explícito: `data: regrava fixtures do <alvo>`.
Quem grava paga: confira a estimativa do harness (script 04) antes de gravar LLMs.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from common.providers import default_llm
from common.providers.jev_sdk import LAYA_BASE_URL
from common.providers.replay import FIXTURES_DIR, fixture_dir_name

BLOCK = Path(__file__).resolve().parents[1]
MODULOS = [
    "01-decision-fundamentals", "02-choice-routing", "03-noul-detection-verification",
    "04-score-ranking", "05-calibration-evaluation",
]
NAO_GRAVAM = {"05_decision_matrix.py", "01_golden_set.py", "05_replay_record.py"}
# Scripts que falam HTTP com /v1/systemone por dentro do LangChain: rodam uma vez por alvo.
POR_ALVO_HTTP = {"04_langchain_classifier.py", "05_langchain_middleware.py"}
# Scripts que recebem o alvo como argumento.
POR_ARGUMENTO = {"01_http_direct.py": ("jev", "laya"), "02_sdk_first_call.py": ("jev", "laya"), "04_laya_local.py": ("laya",)}


def alvos_disponiveis() -> list[str]:
    alvos = []
    if os.environ.get("TYPESAFE_API_KEY"):
        alvos.append("jev")
    base = os.environ.get("LAYA_BASE_URL") or LAYA_BASE_URL
    try:
        httpx.get(f"{base}/health", timeout=3).raise_for_status()
        alvos.append("laya")
    except httpx.HTTPError:
        print(f"Laya não responde em {base}: fora da gravação.")
    llm = default_llm()
    chave = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}.get(llm.split(":", 1)[0])
    if chave and os.environ.get(chave):
        alvos.append(f"llm:{llm}")
    return alvos


def scripts_padrao() -> list[Path]:
    scripts = [p for m in MODULOS for p in sorted((BLOCK / m).glob("[0-9][0-9]_*.py")) if p.name not in NAO_GRAVAM]
    final = BLOCK / "06-final-project-hybrid-agent" / "main.py"
    return [*scripts, final]


def contar() -> dict[str, int]:
    return {d.name: len(list(d.glob("*.json"))) for d in FIXTURES_DIR.iterdir() if d.is_dir()} if FIXTURES_DIR.exists() else {}


parser = argparse.ArgumentParser()
parser.add_argument("--alvos", help="ex.: jev,laya,llm:anthropic:claude-haiku-4-5-20251001 (padrão: o que estiver disponível)")
parser.add_argument("--scripts", nargs="*", help="caminhos relativos à pasta do bloco (padrão: todos)")
parser.add_argument("--forcar", action="store_true", help="regrava mesmo o que já existe")
args = parser.parse_args()

alvos = [a.strip() for a in args.alvos.split(",")] if args.alvos else alvos_disponiveis()
if not alvos:
    sys.exit("Nada para gravar: sem TYPESAFE_API_KEY, sem Laya rodando e sem chave do LLM de baseline.")
# Chamadas que não são decisões tipadas (function calling, geração) gravam junto com o LLM.
extras = [f"{kind}:{a.removeprefix('llm:')}" for a in alvos if a.startswith("llm:") for kind in ("fc", "geracao")]
scripts = [BLOCK / s for s in args.scripts] if args.scripts else scripts_padrao()

print(f"Gravando {alvos} em {len(scripts)} scripts. Fixtures em {FIXTURES_DIR}")
antes = contar()
falhas = []
for script in scripts:
    execucoes = [([], None)]
    if script.name in POR_ARGUMENTO:
        execucoes = [([a], None) for a in POR_ARGUMENTO[script.name] if a in alvos]
    elif script.name in POR_ALVO_HTTP:
        execucoes = [([], a) for a in ("jev", "laya") if a in alvos]
    elif script.name == "main.py":
        execucoes = [(["--lote", "--comparar"], None)]
    for argv, alvo_http in execucoes:
        env = {**os.environ, "DECISION_PROVIDER": "record", "DECISION_RECORD_ONLY": ",".join(alvos + extras),
               "PYTHONIOENCODING": "utf-8"}
        if args.forcar:
            env["DECISION_RECORD_FORCE"] = "1"
        if alvo_http:
            env["DECISION_TARGET"] = alvo_http
        rotulo = f"{script.relative_to(BLOCK)} {' '.join(argv)}{f' [{alvo_http}]' if alvo_http else ''}"
        start = time.perf_counter()
        proc = subprocess.run([sys.executable, str(script), *argv], cwd=script.parent, env=env, capture_output=True, text=True, encoding="utf-8")
        status = "ok" if proc.returncode == 0 else f"FALHOU ({proc.returncode})"
        print(f"  {status:<12} {time.perf_counter() - start:6.1f}s  {rotulo}")
        if proc.returncode != 0:
            falhas.append(rotulo)
            print("    " + "\n    ".join(proc.stderr.strip().splitlines()[-6:]))

depois = contar()
print("\nFixtures por alvo (antes → depois):")
for nome in sorted(set(antes) | set(depois)):
    print(f"  {nome:<45} {antes.get(nome, 0):>4} → {depois.get(nome, 0):>4}")
if "jev" not in alvos:
    print(
        f"\nO Jev não foi gravado. As fixtures em fixtures/{fixture_dir_name('jev')}/ continuam SINTÉTICAS."
        "\nCom a chave, rode: python 05-calibration-evaluation/05_replay_record.py --alvos jev --forcar"
    )
if falhas:
    sys.exit(f"\n{len(falhas)} execuções falharam: {falhas}")
