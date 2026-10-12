"""Infraestrutura compartilhada do Bloco 6 (Modelos de Decisão).

Exceção consciente à regra da trilha de "nada compartilhado entre módulos": dentro deste
bloco, todo módulo mede com as mesmas métricas, os mesmos golden sets e o mesmo
`DecisionClient`. Sem isso, a comparação entre providers deixaria de ser justa.
"""

from pathlib import Path

from dotenv import load_dotenv

BLOCK_DIR = Path(__file__).resolve().parents[1]

# .env da pasta do bloco tem prioridade; depois o da raiz do repositório.
load_dotenv(BLOCK_DIR / ".env")
load_dotenv(BLOCK_DIR.parent / ".env")
