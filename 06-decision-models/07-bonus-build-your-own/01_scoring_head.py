"""Módulo 07 (bônus) · Script 01: um modelo de decisão do zero, com cabeça de scoring.

O esquema é o do artigo de Sebastian Raschka sobre classificadores com LLM/encoder:
cada OPÇÃO é pontuada junto com o estado por um encoder + uma cabeça de UM nó de saída;
um softmax sobre as notas das opções dá a distribuição. Como as opções entram como texto,
o conjunto de opções pode mudar por requisição, sem re-treinar. É a ideia por trás do Choice.

    nota(estado, opção) = w · encoder("[estado] [SEP] [opção]: [descrição]")[CLS]
    P(opção | estado)   = softmax(notas das opções)

Encoder: jhu-clsp/mmBERT-small (140M, multilíngue, MIT). Treino em CPU com os tickets do
golden set (2/3 treino, 1/3 teste). Não precisa de chave; baixa ~550 MB do Hugging Face.

Rode: python 07-bonus-build-your-own/01_scoring_head.py [--epocas 4] [--rapido]
Saída: 07-bonus-build-your-own/saida/scoring_head/ (servido pelo script 03)
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from torch import nn
from transformers import AutoModel, AutoTokenizer

from common import golden, metrics
from common.specs import FILA

parser = argparse.ArgumentParser()
parser.add_argument("--modelo", default="jhu-clsp/mmBERT-small")
parser.add_argument("--epocas", type=int, default=8)
parser.add_argument("--acumular", type=int, default=4, help="tickets por passo do otimizador")
parser.add_argument("--rapido", action="store_true", help="2 épocas e 12 tickets de treino (smoke test)")
args = parser.parse_args()

SAIDA = Path(__file__).resolve().parent / "saida" / "scoring_head"
torch.manual_seed(0)
random.seed(0)


class ScoringHead(nn.Module):
    """Encoder + um nó de saída. Pontua um par (estado, opção)."""

    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        self.score = nn.Linear(encoder.config.hidden_size, 1)

    def forward(self, **batch) -> torch.Tensor:
        cls = self.encoder(**batch).last_hidden_state[:, 0]
        return self.score(cls).squeeze(-1)


def opcoes_texto(criteria: dict) -> list[str]:
    return [f"{label}: {desc}" for label, desc in criteria.items()]


def distribuicao(model, tokenizer, estado: str, criteria: dict) -> dict[str, float]:
    batch = tokenizer([estado] * len(criteria), opcoes_texto(criteria), padding=True, truncation=True,
                      max_length=256, return_tensors="pt")
    with torch.no_grad():
        probs = torch.softmax(model(**batch), dim=-1)
    return dict(zip(criteria, probs.tolist(), strict=True))


def avaliar(model, tokenizer, itens) -> dict:
    model.eval()
    truth, preds, confs = [], [], []
    for item in itens:
        dist = distribuicao(model, tokenizer, item.state["ticket"], FILA.criteria)
        pred = max(dist, key=dist.get)
        truth.append(item.labels["fila"])
        preds.append(pred)
        confs.append(dist[pred])
    correct = [p == t for p, t in zip(preds, truth, strict=True)]
    return {"acurácia": metrics.accuracy(truth, preds), "ece": metrics.ece(confs, correct)}


tickets = golden.load("tickets")
teste = tickets[2::3]
treino = [t for t in tickets if t not in teste]
if args.rapido:
    treino, teste, args.epocas = treino[:12], teste[:6], 2
labels = list(FILA.criteria)
print(f"{len(treino)} tickets de treino, {len(teste)} de teste, encoder {args.modelo}")

tokenizer = AutoTokenizer.from_pretrained(args.modelo)
model = ScoringHead(AutoModel.from_pretrained(args.modelo))
antes = avaliar(model, tokenizer, teste)
print(f"antes do treino (cabeça aleatória): acurácia {antes['acurácia']:.0%}, ECE {antes['ece']:.3f}")

optimizer = torch.optim.AdamW([
    {"params": model.encoder.parameters(), "lr": 2e-5},
    {"params": model.score.parameters(), "lr": 1e-3},
], weight_decay=0.01)
loss_fn = nn.CrossEntropyLoss()

for epoca in range(1, args.epocas + 1):
    model.train()
    random.shuffle(treino)
    total = 0.0
    optimizer.zero_grad()
    for passo, item in enumerate(treino, 1):
        # Uma "linha" de treino = o estado contra TODAS as opções; o alvo é o índice da certa.
        batch = tokenizer([item.state["ticket"]] * len(labels), opcoes_texto(FILA.criteria), padding=True,
                          truncation=True, max_length=256, return_tensors="pt")
        notas = model(**batch).unsqueeze(0)  # (1, n_opções)
        loss = loss_fn(notas, torch.tensor([labels.index(item.labels["fila"])]))
        (loss / args.acumular).backward()  # acumula: 40 exemplos com passo por exemplo oscilam demais
        if passo % args.acumular == 0 or passo == len(treino):
            optimizer.step()
            optimizer.zero_grad()
        total += loss.item()
    r = avaliar(model, tokenizer, teste)
    print(f"época {epoca}: loss {total / len(treino):.3f} | teste: acurácia {r['acurácia']:.0%}, ECE {r['ece']:.3f}")

SAIDA.mkdir(parents=True, exist_ok=True)
model.encoder.save_pretrained(SAIDA / "encoder")
tokenizer.save_pretrained(SAIDA / "encoder")
torch.save(model.score.state_dict(), SAIDA / "score.pt")
(SAIDA / "meta.json").write_text(json.dumps({"base": args.modelo, "treinado_em": "golden_tickets (fila)",
                                             "teste": r}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nModelo salvo em {SAIDA}. O script 03 serve este modelo em /v1/systemone.")
print("\nRepare: a cabeça nunca viu as opções como classes fixas. Troque as descrições (ou acrescente"
      "\numa opção) no script 03 e ele continua respondendo: é isso que faz um Choice ser 'zero-shot'.")
