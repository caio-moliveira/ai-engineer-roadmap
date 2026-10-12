"""As tools do agente de vendas: cada uma devolve uma tabela pronta.

No workshop-jev, cada tool lê uma view do Postgres. Aqui, para o projeto rodar sem banco,
os resultados estão gravados em ../data/tool_results/. Troque `run_tool` por uma consulta
real quando plugar o seu domínio.
"""

import json
from pathlib import Path

TOOL_RESULTS = Path(__file__).resolve().parents[1] / "data" / "tool_results"


def run_tool(name: str) -> list[dict]:
    path = TOOL_RESULTS / f"{name}.json"
    if not path.exists():
        raise ValueError(f"tool desconhecida: {name!r}")  # o nome vem do Choice, nunca de texto livre
    return json.loads(path.read_text(encoding="utf-8"))["rows"]
