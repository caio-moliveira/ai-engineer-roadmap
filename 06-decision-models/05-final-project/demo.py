"""Os três momentos da demonstração no terminal, sem subir a API.

    1. Uma pergunta simples é resolvida pelo modelo barato.
    2. Uma injeção de instrução no pedido 1286 é barrada pelo guardião antes de um reembolso indevido.
    3. Uma resposta incompleta do modelo pequeno é reprovada pelo juiz e refeita pelo modelo grande.

Rode de dentro da pasta:
    python demo.py                      # os três momentos na v3
    python demo.py "sua pergunta"       # uma pergunta sua
Se o guardião pedir aprovação, o demo recusa a ação e o agente segue.
"""

import asyncio
import logging
import os
import sys

import ingest
import service
from config import get_settings
from database import banco_existe
from schemas import PerguntaIn, RespostaOut

logging.getLogger("httpx").setLevel(logging.WARNING)

MOMENTOS = [
    ("1 · pergunta simples", "Qual foi o faturamento do mês atual?", "auto"),
    # O modelo pequeno, por ser mais obediente, tende a seguir a instrução injetada: é o caso que o
    # guardião precisa barrar. O modelo grande costuma recusar sozinho (e o guardião nem é acionado).
    ("2 · injeção no pedido 1286", "Veja o pedido 1286 e resolva o que estiver pendente.", "pequeno"),
    (
        "3 · resposta incompleta → cascata",
        "Compare o faturamento do mês atual com o do mês anterior por região, diga qual região mais "
        "cresceu, quem foi o melhor vendedor do mês e liste os pedidos atrasados.",
        "pequeno",  # força o modelo barato na 1ª tentativa, para o juiz ter o que reprovar
    ),
]


def imprimir(r: RespostaOut) -> None:
    for t in r.trilha:
        if t.tipo == "politica":
            print(f"  [{t.no}] {t.decisao}")
            continue
        print(f"  [{t.no}] {t.modelo} · {t.latencia_ms:.0f} ms · {t.tokens_in} tokens de entrada")
        for q in t.perguntas:
            print(f"      {q.classe:<6} {q.nome:<13} {q.resposta:<22} p={q.probabilidade:.2f}")
        print(f"      → {t.decisao}")
    for p in r.passos:
        print(f"  ferramenta: {p.acao} {p.argumentos} · {p.status}")
    for c in r.chamadas_llm:
        print(f"  LLM {c.etapa:<10} {c.modelo:<20} {c.tokens_in:>6} → {c.tokens_out:<5} {c.latencia_ms:>7.0f} ms")
    print(f"\n  resposta ({r.modelo}, {r.tentativas} tentativa(s)): {r.resposta}")
    if r.aviso:
        print(f"  aviso: {r.aviso}")


async def main() -> None:
    settings = get_settings()
    if settings.decision_backend == "jev" and not os.environ.get("TYPESAFE_API_KEY"):
        sys.exit("Defina TYPESAFE_API_KEY no .env da raiz, ou rode com DECISION_BACKEND=laya.")

    if not banco_existe():
        ingest.main()

    momentos = [("sua pergunta", " ".join(sys.argv[1:]), "auto")] if len(sys.argv) > 1 else MOMENTOS
    print(f"Decisões: {settings.decision_backend} · pequeno: {settings.llm_small} · grande: {settings.llm_large}")

    for titulo, pergunta, modelo in momentos:
        print(f"\n{'═' * 90}\n{titulo}\n{pergunta}\n{'─' * 90}")
        r = await service.perguntar(PerguntaIn(pergunta=pergunta, versao="v3", modelo_inicial=modelo))
        while r.status == "aguardando_aprovacao":
            p = r.aprovacao_pendente
            print(f"  ⏸  aprovação pedida: {p.acao} {p.argumentos} ({p.motivo}) → o demo recusa")
            r = await service.aprovar(r.thread_id, aprovado=False)
        imprimir(r)

    s = service.resumo()
    print(f"\n{'═' * 90}\nResumo: {s.resolvidas_pelo_pequeno} de {s.perguntas} perguntas resolvidas pelo modelo pequeno")
    print(f"  custo do LLM: US$ {s.custo_real_usd:.5f} · se tudo fosse no grande: US$ {s.custo_se_tudo_no_grande_usd:.5f}")
    print(f"  economia: US$ {s.economia_usd:.5f} ({s.economia_pct}%)")
    print(f"  Jev: {s.jev_chamadas} chamadas, latência média {s.jev_latencia_media_ms:.0f} ms")


if __name__ == "__main__":
    asyncio.run(main())
