"""Gera fixtures SINTÉTICAS do Jev para o bloco rodar em replay enquanto não há chave.

Por que existe: o Jev está em acesso antecipado e as fixtures reais exigem TYPESAFE_API_KEY.
Sem elas, nenhum script com o Jev rodaria em replay. Estas fixtures:

- partem dos RÓTULOS do golden set, com ruído determinístico (sempre o mesmo resultado);
- quando a pergunta não tem rótulo (ex.: verificação de uma resposta gerada), copiam a
  resposta gravada do LLM de baseline, ou a do Laya;
- usam a contagem de tokens do Laya como aproximação e uma latência sorteada;
- saem com "synthetic": true. O replay avisa no terminal e as tabelas marcam "(sintético)".

NÃO são medição do Jev. Os números de acurácia e calibração do Jev em replay refletem as
taxas escolhidas abaixo, não o modelo. Substitua por gravações reais:
    python 05-calibration-evaluation/05_replay_record.py --alvos jev

Uma gravação real nunca é sobrescrita por este script.

Rode (da pasta 06-decision-models): python fixtures/gerar_jev_sintetico.py
"""

import hashlib
import json
import random
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import golden
from common.decisions import DecisionResult, answers_from_systemone, canonical_json
from common.pricing import cost_usd

FIXTURES = Path(__file__).resolve().parent
MODEL = "jev-1.13.0"
ORIGEM = (
    "SINTÉTICA: gerada a partir dos rótulos do golden set com ruído determinístico "
    "(fixtures/gerar_jev_sintetico.py). Não é medição do Jev."
)
# Taxas de acerto escolhidas para o sintético. São premissas, não resultados.
ACERTO = {"choice": 0.90, "score": 0.85, "noul": 0.92}
ALIASES = {"model_route": "rota", "is_risky": "deve_bloquear"}


def rng_for(key: str, name: str) -> random.Random:
    return random.Random(int(hashlib.sha256(f"{key}:{name}".encode()).hexdigest()[:16], 16))


def label_for(state, name: str, index: dict, tickets: list, tool_calls: list):
    labels = index.get(canonical_json(state))
    name = ALIASES.get(name, name)
    if labels and name in labels:
        return labels[name]
    text = canonical_json(state)
    if name == "rota":  # o ModelRouterMiddleware manda a mensagem do usuário, não o ticket do golden set
        for t in tickets:
            if json.dumps(t.state["ticket"], ensure_ascii=False)[1:-1] in text:
                return t.labels["rota"]
    if name == "deve_bloquear" and isinstance(state, dict) and "tool_call" in state:
        call = state["tool_call"]
        for c in tool_calls:
            if c.state["tool"] == call.get("name") and c.state["args"] == call.get("args") and json.dumps(c.state["mensagem"], ensure_ascii=False)[1:-1] in text:
                return c.labels["deve_bloquear"]
    return None


def spread(rng: random.Random, chosen: str, keys: list[str], conf: float) -> dict[str, float]:
    others = [k for k in keys if k != chosen]
    weights = [rng.random() + 0.05 for _ in others]
    total = sum(weights) or 1
    probs = {k: round((1 - conf) * w / total, 4) for k, w in zip(others, weights)}
    probs[chosen] = round(conf, 4)
    return {k: probs[k] for k in keys}


def synth_answer(key: str, name: str, q: dict, label, fallback: dict | None) -> dict:
    rng = rng_for(key, name)
    kind = q["type"]
    if kind == "noul":
        if label is None:
            p = float(fallback["noul"]) if fallback else 0.5
        else:
            certo = rng.random() < ACERTO["noul"]
            alto = rng.uniform(0.85, 0.99) if certo else rng.uniform(0.55, 0.80)
            p = alto if bool(label) == certo else 1 - alto
        return {"type": "noul", "noul": round(p, 4)}

    if kind == "choice":
        keys = list(q["criteria"])
        if label is None or label not in keys:
            chosen = fallback.get("choice") if fallback and fallback.get("choice") in keys else keys[0]
            conf = rng.uniform(0.70, 0.95)
        elif rng.random() < ACERTO["choice"]:
            chosen, conf = label, rng.uniform(0.80, 0.99)
        else:
            chosen, conf = rng.choice([k for k in keys if k != label] or keys), rng.uniform(0.45, 0.80)
        probs = spread(rng, chosen, keys, conf)
        return {"type": "choice", "choice": chosen, "confidence": round(conf, 4), "probabilities": probs}

    levels = [str(i) for i in range(len(q["criteria"]))]
    if label is None:
        chosen = str(round(float(fallback["score"]))) if fallback and "score" in fallback else levels[len(levels) // 2]
        conf = rng.uniform(0.6, 0.9)
    elif rng.random() < ACERTO["score"]:
        chosen, conf = str(label), rng.uniform(0.75, 0.97)
    else:
        vizinhos = [lv for lv in levels if abs(int(lv) - int(label)) == 1]
        chosen, conf = rng.choice(vizinhos or levels), rng.uniform(0.45, 0.75)
    probs = spread(rng, chosen, levels, conf)
    return {"type": "score", "score": round(sum(int(k) * p for k, p in probs.items()), 4), "confidence": round(conf, 4),
            "legend": {lv: q["criteria"][int(lv)] for lv in levels}, "probabilities": probs}


def main() -> None:
    index = golden.label_index()
    tickets, tool_calls = golden.load("tickets"), golden.load("tool_calls")
    fontes = [d for d in FIXTURES.iterdir() if d.is_dir() and (d.name == "laya" or d.name.startswith("llm-"))]
    pedidos: dict[str, dict] = {}
    for fonte in fontes:
        for path in fonte.glob("*.json"):
            fx = json.loads(path.read_text(encoding="utf-8"))
            entry = pedidos.setdefault(fx["key"], {"request": fx["request"], "answers": {}, "tokens": None})
            raw_answers = fx["result"].get("raw", {}).get("answers")
            for name, a in (raw_answers or {}).items():
                entry["answers"].setdefault(name, a)
            if not raw_answers:  # LLM: monta no formato de fio a partir do valor normalizado
                for name, a in fx["result"]["answers"].items():
                    q = fx["request"]["questions"].get(name, {})
                    wire = {"noul": {"noul": a["value"]}, "choice": {"choice": a["value"]}, "score": {"score": a["value"]}}.get(q.get("type"))
                    if wire:
                        entry["answers"].setdefault(name, wire)
            if fonte.name == "laya":
                entry["tokens"] = fx["result"].get("tokens_in")

    # Pedidos que dependem da decisão do PRÓPRIO Jev (ex.: o 2º nível da classificação hierárquica
    # usa a fila que ele escolheu) não foram gravados por ninguém quando ele erra: geramos todos.
    from common.decisions import request_key, to_wire_questions
    from common.specs import CATEGORIAS, categoria_da_fila

    for t in tickets:
        for fila in CATEGORIAS:
            wire = to_wire_questions([categoria_da_fila(fila)])
            pedidos.setdefault(request_key(t.state, wire), {"request": {"state": t.state, "questions": wire},
                                                            "answers": {}, "tokens": None})

    destino = FIXTURES / "jev"
    destino.mkdir(exist_ok=True)
    criadas = puladas = sem_rotulo = 0
    for key, entry in sorted(pedidos.items()):
        path = destino / f"{key}.json"
        if path.exists() and not json.loads(path.read_text(encoding="utf-8")).get("synthetic"):
            puladas += 1
            continue
        state, questions = entry["request"]["state"], entry["request"]["questions"]
        answers = {}
        for name, q in questions.items():
            label = label_for(state, name, index, tickets, tool_calls)
            sem_rotulo += label is None
            answers[name] = synth_answer(key, name, q, label, entry["answers"].get(name))
        rng = rng_for(key, "_meta")
        tokens_in = entry["tokens"] or len(canonical_json(entry["request"])) // 4
        raw = {"model": MODEL, "answers": answers, "usage": {"input_tokens": tokens_in, "output_tokens": 0}}
        result = DecisionResult(
            provider="jev", model=MODEL, answers=answers_from_systemone(answers),
            latency_ms=round(rng.uniform(35, 60) + 6 * len(questions), 1),
            tokens_in=tokens_in, tokens_out=0, cost_usd=cost_usd(MODEL, tokens_in, 0), synthetic=True, raw=raw,
        )
        fixture = {"key": key, "target": "jev", "recorded_at": date.today().isoformat(), "synthetic": True,
                   "origin": ORIGEM, "request": entry["request"], "result": result.model_dump(mode="json")}
        path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        criadas += 1
    print(f"{criadas} fixtures sintéticas do Jev escritas; {puladas} gravações reais preservadas; "
          f"{sem_rotulo} perguntas sem rótulo (copiadas do LLM ou do Laya).")


if __name__ == "__main__":
    main()
