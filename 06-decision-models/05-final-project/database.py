"""Banco SQLite da operação de vendas: schema e conexão.

O arquivo `vendas.db` fica nesta pasta. Quem cria e popula é o `ingest.py`; a API roda a ingestão
sozinha no início se o banco ainda não existir.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vendas.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS vendedores (
    id      INTEGER PRIMARY KEY,
    nome    TEXT NOT NULL,
    regiao  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL,
    segmento  TEXT NOT NULL,
    cidade    TEXT NOT NULL,
    uf        TEXT NOT NULL,
    regiao    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS produtos (
    id         INTEGER PRIMARY KEY,
    nome       TEXT NOT NULL,
    categoria  TEXT NOT NULL,
    preco      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS pedidos (
    id             INTEGER PRIMARY KEY,
    cliente_id     INTEGER NOT NULL REFERENCES clientes(id),
    vendedor_id    INTEGER NOT NULL REFERENCES vendedores(id),
    data_pedido    TEXT NOT NULL,              -- AAAA-MM-DD
    prazo_entrega  TEXT NOT NULL,
    data_entrega   TEXT,                       -- vazio enquanto não entregue
    status         TEXT NOT NULL CHECK (status IN ('em_transito', 'entregue', 'cancelado')),
    valor_total    REAL NOT NULL,
    observacao     TEXT
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    pedido_id       INTEGER NOT NULL REFERENCES pedidos(id),
    produto_id      INTEGER NOT NULL REFERENCES produtos(id),
    quantidade      INTEGER NOT NULL,
    preco_unitario  REAL NOT NULL,
    PRIMARY KEY (pedido_id, produto_id)
);

-- As ações de risco gravam aqui. Nada sai do banco: é uma simulação.
CREATE TABLE IF NOT EXISTS reembolsos (
    protocolo  TEXT PRIMARY KEY,
    pedido_id  INTEGER NOT NULL REFERENCES pedidos(id),
    valor      REAL NOT NULL,
    motivo     TEXT NOT NULL,
    criado_em  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cancelamentos (
    protocolo  TEXT PRIMARY KEY,
    pedido_id  INTEGER NOT NULL REFERENCES pedidos(id),
    motivo     TEXT NOT NULL,
    criado_em  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pedidos_data ON pedidos(data_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos(status);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def banco_existe() -> bool:
    if not DB_PATH.exists():
        return False
    with connect() as conn:
        tabela = conn.execute("SELECT name FROM sqlite_master WHERE name = 'pedidos'").fetchone()
        return tabela is not None and conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] > 0
