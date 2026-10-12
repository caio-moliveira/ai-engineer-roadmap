"""Módulo 07 (bônus) · Script 02: ajustar o Laya multilíngue nos seus dados.

A tese do Laya é esta: zero-shot ele fica bem abaixo do Jev, e o ganho vem de ajustar no
seu domínio. Treinamos em dois pontos onde ele foi fraco no bloco: a fila dos tickets
(módulo 02, script 01) e a escolha de tool do agente de vendas (módulo 02, script 02).

- Dados: os golden sets, divididos em treino (2/3) e teste (1/3). O teste nunca entra no treino.
- Treino: `laya.train.finetune` (o loop oficial do pacote), com `loss="soft-ce"`; o próprio
  pacote registra (#741) que o termo de RL extra não ganhou nada no split de typed decisions.
- O pacote também ajusta temperaturas de calibração ao final. Com poucos exemplos, ele avisa
  que a calibração está apoiada em pouca evidência: leia o aviso.

Roda em CPU, mas devagar (o checkpoint tem 322M). Use --rapido para um smoke test.
Pré-requisito: Bloco 5 (fine-tuning). Rode: python 07-bonus-build-your-own/02_finetune_laya.py
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import laya
from laya.train import TrainConfig, finetune, resolve_checkpoint_dir

from common import golden, metrics
from common.specs import FILA, TOOL

parser = argparse.ArgumentParser()
parser.add_argument("--epocas", type=int, default=3)
parser.add_argument("--rapido", action="store_true", help="1 época, poucos itens (smoke test)")
args = parser.parse_args()

SAIDA = Path(__file__).resolve().parent / "saida"
CHECKPOINT = SAIDA / "laya-ajustado"
SAIDA.mkdir(exist_ok=True)

TAREFAS = [("tickets", FILA), ("sales", TOOL)]


def dividir(items):
    teste = items[2::3]
    return [i for i in items if i not in teste], teste


treino_rows, teste_items = [], []
for dataset, spec in TAREFAS:
    treino, teste = dividir(golden.load(dataset))
    if args.rapido:
        treino, teste = treino[:8], teste[:4]
    treino_rows += [{"state": i.state, "questions": {spec.name: spec.to_wire()}, "expected": {spec.name: i.labels[spec.name]}}
                    for i in treino]
    teste_items += [(spec, i) for i in teste]

treino_path = SAIDA / "treino.jsonl"
treino_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in treino_rows) + "\n", encoding="utf-8")
print(f"{len(treino_rows)} linhas de treino em {treino_path.name}; {len(teste_items)} itens de teste separados")


def avaliar(agent, nome: str) -> list[dict]:
    rows = []
    for spec in {s.name: s for s, _ in teste_items}.values():
        itens = [i for s, i in teste_items if s.name == spec.name]
        truth, preds, confs = [], [], []
        for item in itens:
            answer = agent.predict(item.state, {spec.name: spec.to_wire()})["answers"][spec.name]
            truth.append(item.labels[spec.name])
            preds.append(answer["choice"])
            confs.append(answer["confidence"])
        correct = [p == t for p, t in zip(preds, truth, strict=True)]
        rows.append({"modelo": nome, "pergunta": spec.name, "n": len(itens),
                     "acurácia": metrics.accuracy(truth, preds), "ece": metrics.ece(confs, correct)})
    return rows


base_dir = resolve_checkpoint_dir("convaiinnovations/laya-multilingual")
resultado = avaliar(laya.load(base_dir), "laya-multilingual (zero-shot)")

config = TrainConfig(epochs=1 if args.rapido else args.epocas, micro_batch=8, grad_accum=1, loss="soft-ce", log_every=10)
print(f"\nTreinando a partir de {base_dir} ...")
summary = finetune(str(treino_path), base_dir, str(CHECKPOINT), config=config, device="auto")
print(f"perda por época: {summary.get('epoch_loss')}")

resultado += avaliar(laya.load(str(CHECKPOINT)), "laya ajustado")

from common.evaluation import print_table

print_table(resultado, "Laya antes e depois do ajuste (itens de teste, nunca vistos no treino)")
print(
    f"\nCheckpoint salvo em {CHECKPOINT}. Para medir no harness do módulo 05, sirva-o com o laya-serve:"
    f"\n    LAYA_PORT=8001 LAYA_EXTRA_MODELS='{{\"ajustado\": \"{CHECKPOINT.as_posix()}\"}}' uv run laya-serve"
    "\ne rode o harness com LAYA_MODEL=ajustado DECISION_PROVIDER=live."
    "\n\nCuidado com a conclusão: dezenas de exemplos de teste dão um intervalo de confiança largo."
    "\nE o golden set do bloco é pequeno de propósito; no seu domínio, use centenas por pergunta."
)
