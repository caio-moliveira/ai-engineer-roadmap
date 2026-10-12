"""Módulo 07 (bônus) · Script 03: o seu próprio servidor `/v1/systemone`.

Qualquer servidor que fale este esquema vira um provider do bloco sem mudar uma linha do
código cliente: o SDK do Jev, o `DecisionClient`, o harness do módulo 05.

Backend do servidor:
- `head` (padrão, se existir): a cabeça de scoring treinada no script 01. Noul vira um Choice
  verdadeiro/falso; Score vira um Choice sobre os níveis, com o valor esperado como `score`.
- `cliente`: delega para um `DecisionClient` do bloco (replay, Jev ou Laya). Útil como gateway.

Rode:
    python 07-bonus-build-your-own/03_serve_systemone.py              # sobe, chama pelo SDK e desliga
    python 07-bonus-build-your-own/03_serve_systemone.py --servir     # fica de pé em 127.0.0.1:8002
Endpoints são FastAPI: a inferência é síncrona e roda em `asyncio.to_thread`, o padrão da trilha
(04-ocr/06-final-project/router.py) para não travar o event loop.
"""

import argparse
import asyncio
import sys
import threading
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from common import golden
from common.decisions import DecisionSpec
from common.specs import FILA

HEAD_DIR = Path(__file__).resolve().parent / "saida" / "scoring_head"
MODEL_NAME = "meu-systemone"  # preço 0 em common/pricing.yaml: roda na sua máquina

parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=["head", "cliente"], default="head" if HEAD_DIR.exists() else "cliente")
parser.add_argument("--porta", type=int, default=8002)
parser.add_argument("--servir", action="store_true", help="fica de pé até Ctrl+C")
args = parser.parse_args()


class SystemOneRequest(BaseModel):
    state: Any
    model: str | None = None
    questions: dict[str, dict[str, Any]]


# --- Backends ------------------------------------------------------------------------------


def head_backend():
    import torch
    from torch import nn
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(HEAD_DIR / "encoder")
    encoder = AutoModel.from_pretrained(HEAD_DIR / "encoder").eval()
    score = nn.Linear(encoder.config.hidden_size, 1)
    score.load_state_dict(torch.load(HEAD_DIR / "score.pt"))

    def distribution(state_text: str, options: dict[str, str]) -> dict[str, float]:
        batch = tokenizer([state_text] * len(options), [f"{k}: {v}" for k, v in options.items()],
                          padding=True, truncation=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            notas = score(encoder(**batch).last_hidden_state[:, 0]).squeeze(-1)
        return dict(zip(options, torch.softmax(notas, -1).tolist(), strict=True)), int(batch["attention_mask"].sum())

    def answer(state: Any, questions: dict) -> tuple[dict, int]:
        state_text = state if isinstance(state, str) else " ".join(str(v) for v in state.values()) if isinstance(state, dict) else str(state)
        answers, tokens = {}, 0
        for name, q in questions.items():
            instr = q.get("instructions") or ""
            if q["type"] == "choice":
                opts = {k: f"{instr} {v or ''}".strip() for k, v in q["criteria"].items()}
                dist, n = distribution(state_text, opts)
                best = max(dist, key=dist.get)
                answers[name] = {"type": "choice", "choice": best, "confidence": dist[best], "probabilities": dist}
            elif q["type"] == "noul":
                crit = q.get("criteria") or {}
                dist, n = distribution(state_text, {"true": f"{instr} Sim. {crit.get('true') or ''}",
                                                    "false": f"{instr} Não. {crit.get('false') or ''}"})
                answers[name] = {"type": "noul", "noul": dist["true"]}
            else:
                levels = {str(i): f"{instr} {c}" for i, c in enumerate(q["criteria"])}
                dist, n = distribution(state_text, levels)
                best = max(dist, key=dist.get)
                answers[name] = {"type": "score", "score": sum(int(k) * p for k, p in dist.items()), "confidence": dist[best],
                                 "legend": {str(i): c for i, c in enumerate(q["criteria"])}, "probabilities": dist}
            tokens += n
        return answers, tokens

    return answer


def client_backend():
    from common.providers import get_client

    client = get_client()

    def answer(state: Any, questions: dict) -> tuple[dict, int]:
        specs = [DecisionSpec(name=name, **q) for name, q in questions.items()]
        result = client.decide(state, specs)
        return result.raw.get("answers") or {}, result.tokens_in or 0

    return answer


backend = head_backend() if args.backend == "head" else client_backend()

app = FastAPI(title="Meu System One")


@app.get("/health")
def health():
    return {"status": "ok", "backend": args.backend}


@app.post("/v1/systemone")
async def system_one(request: SystemOneRequest):
    answers, tokens = await asyncio.to_thread(backend, request.state, request.questions)
    return {"model": MODEL_NAME, "answers": answers, "usage": {"input_tokens": tokens, "output_tokens": 0}}


base_url = f"http://127.0.0.1:{args.porta}"
if args.servir:
    print(f"Servindo /v1/systemone em {base_url} (backend: {args.backend}). Ctrl+C para sair.")
    uvicorn.run(app, host="127.0.0.1", port=args.porta, log_level="warning")
    sys.exit()

server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=args.porta, log_level="warning"))
threading.Thread(target=server.run, daemon=True).start()
for _ in range(50):
    try:
        httpx.get(f"{base_url}/health", timeout=1)
        break
    except httpx.HTTPError:
        time.sleep(0.1)

# O cliente do bloco, sem mudança nenhuma: só a base_url é outra.
from common.providers.jev_sdk import JevSDKClient

client = JevSDKClient(provider="meu-systemone", base_url=base_url, api_key="local", model=MODEL_NAME)
print(f"Servidor de pé em {base_url} (backend: {args.backend}). Chamando pelo SDK do Jev:\n")
for item in golden.load("tickets")[:6]:
    result = client.decide(item.state, [FILA])
    a = result.answers["fila"]
    print(f"  [{item.id}] {a.value:<11} ({a.confidence:.2f}) esperado {item.labels['fila']:<11} {result.latency_ms:5.0f} ms")
server.should_exit = True
print(
    "\nPara usar no harness: suba com --servir e aponte um alvo para ele. O jeito mais curto é"
    f"\nLAYA_BASE_URL={base_url} LAYA_MODEL={MODEL_NAME} DECISION_PROVIDER=live, rodando o harness com --alvos laya."
)
