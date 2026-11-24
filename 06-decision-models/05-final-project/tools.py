"""As ferramentas do agente, como tools comuns do LangChain, sobre o banco SQLite `vendas.db`.

Leitura: indicadores, pedidos atrasados, um pedido pelo número e ranking de vendedores.
Ações de risco: reembolso e cancelamento gravam no banco (tabelas `reembolsos` e `cancelamentos`).
É uma simulação: nenhum dinheiro sai, mas o efeito aparece nas consultas seguintes.

As tools são síncronas: o `ainvoke` do LangChain as roda num executor, sem travar o event loop.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from langchain_core.tools import BaseTool, tool

from database import connect
from ingest import HOJE

PERIODOS = {"mes_atual": "2026-11", "mes_anterior": "2026-10"}
Periodo = Literal["mes_atual", "mes_anterior"]

_ATRASADO = f"p.status = 'em_transito' AND p.prazo_entrega < '{HOJE.isoformat()}'"


def _filtro_regiao(regiao: str | None) -> tuple[str, list]:
    return ("AND lower(c.regiao) = lower(?)", [regiao]) if regiao else ("", [])


# --- Leitura -------------------------------------------------------------------------------------
@tool
def consultar_indicadores(periodo: Periodo = "mes_atual", regiao: str | None = None) -> dict:
    """Indicadores de vendas de um mês (atual ou anterior), no total ou de uma região: faturamento,
    número de pedidos, ticket médio, quantos pedidos feitos no mês estão atrasados, cancelamentos,
    reembolsos e faturamento por região.
    O mês atual vai até a data de referência (é parcial)."""
    filtro, params = _filtro_regiao(regiao)
    mes = PERIODOS[periodo]
    with connect() as conn:
        r = conn.execute(
            f"""
            SELECT
                COALESCE(SUM(CASE WHEN p.status != 'cancelado' THEN p.valor_total END), 0) AS faturamento,
                SUM(p.status != 'cancelado') AS pedidos,
                SUM(p.status = 'cancelado') AS cancelamentos,
                SUM({_ATRASADO}) AS atrasados_do_mes,
                COUNT(DISTINCT p.data_pedido) AS dias_com_venda
            FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
            WHERE substr(p.data_pedido, 1, 7) = ? {filtro}
            """,
            [mes, *params],
        ).fetchone()
        por_regiao = conn.execute(
            f"""
            SELECT c.regiao, ROUND(SUM(p.valor_total), 2) AS faturamento, COUNT(*) AS pedidos
            FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
            WHERE substr(p.data_pedido, 1, 7) = ? AND p.status != 'cancelado' {filtro}
            GROUP BY c.regiao ORDER BY faturamento DESC
            """,
            [mes, *params],
        ).fetchall()
        reembolsado = conn.execute(
            f"""
            SELECT COALESCE(SUM(r.valor), 0) FROM reembolsos r
            JOIN pedidos p ON p.id = r.pedido_id JOIN clientes c ON c.id = p.cliente_id
            WHERE substr(p.data_pedido, 1, 7) = ? {filtro}
            """,
            [mes, *params],
        ).fetchone()[0]

    pedidos = r["pedidos"] or 0
    return {
        "periodo": periodo,
        "mes": mes,
        "parcial_ate": HOJE.isoformat() if periodo == "mes_atual" else None,
        "regiao": regiao or "todas",
        "faturamento": round(r["faturamento"], 2),
        "pedidos": pedidos,
        "ticket_medio": round(r["faturamento"] / pedidos, 2) if pedidos else 0,
        "pedidos_do_mes_atrasados": r["atrasados_do_mes"] or 0,  # a lista completa: listar_pedidos_atrasados
        "cancelamentos": r["cancelamentos"] or 0,
        "reembolsado": round(reembolsado, 2),
        "dias_com_venda": r["dias_com_venda"],
        "faturamento_por_regiao": [dict(x) for x in por_regiao],
    }


@tool
def listar_pedidos_atrasados(regiao: str | None = None) -> dict:
    """Pedidos em trânsito com o prazo de entrega vencido, do mais atrasado para o menos,
    opcionalmente filtrados por região."""
    filtro, params = _filtro_regiao(regiao)
    with connect() as conn:
        linhas = conn.execute(
            f"""
            SELECT p.id, c.nome AS cliente, c.regiao, v.nome AS vendedor, p.valor_total AS valor,
                   p.prazo_entrega, CAST(julianday(?) - julianday(p.prazo_entrega) AS INTEGER) AS dias_de_atraso
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id JOIN vendedores v ON v.id = p.vendedor_id
            WHERE {_ATRASADO} {filtro}
            ORDER BY dias_de_atraso DESC, p.id
            """,
            [HOJE.isoformat(), *params],
        ).fetchall()
    pedidos = [dict(x) for x in linhas]
    return {
        "data_de_referencia": HOJE.isoformat(),
        "total": len(pedidos),
        "valor_total": round(sum(p["valor"] for p in pedidos), 2),
        "pedidos": pedidos,
    }


@tool
def buscar_pedido(pedido_id: int) -> dict:
    """Todos os dados de um pedido pelo número: cliente, vendedor, status, prazo, itens,
    observações do atendimento e reembolsos ou cancelamentos já registrados."""
    with connect() as conn:
        p = conn.execute(
            f"""
            SELECT p.*, c.nome AS cliente, c.segmento, c.cidade, c.uf, c.regiao, v.nome AS vendedor,
                   ({_ATRASADO}) AS atrasado
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id JOIN vendedores v ON v.id = p.vendedor_id
            WHERE p.id = ?
            """,
            [pedido_id],
        ).fetchone()
        if p is None:
            return {"erro": f"pedido {pedido_id} não encontrado"}
        itens = conn.execute(
            """
            SELECT pr.nome AS produto, i.quantidade, i.preco_unitario,
                   ROUND(i.quantidade * i.preco_unitario, 2) AS subtotal
            FROM itens_pedido i JOIN produtos pr ON pr.id = i.produto_id
            WHERE i.pedido_id = ?
            """,
            [pedido_id],
        ).fetchall()
        reembolsos = conn.execute(
            "SELECT protocolo, valor, motivo, criado_em FROM reembolsos WHERE pedido_id = ?", [pedido_id]
        ).fetchall()
    pedido = {k: p[k] for k in p.keys() if k not in ("cliente_id", "vendedor_id")}
    pedido["atrasado"] = bool(pedido["atrasado"])
    return {**pedido, "itens": [dict(i) for i in itens], "reembolsos": [dict(r) for r in reembolsos]}


@tool
def ranking_vendedores(periodo: Periodo = "mes_atual") -> dict:
    """Faturamento, número de pedidos e ticket médio de cada vendedor no mês, do maior para o menor."""
    with connect() as conn:
        linhas = conn.execute(
            """
            SELECT v.nome AS vendedor, v.regiao, ROUND(SUM(p.valor_total), 2) AS faturamento,
                   COUNT(*) AS pedidos, ROUND(AVG(p.valor_total), 2) AS ticket_medio
            FROM pedidos p JOIN vendedores v ON v.id = p.vendedor_id
            WHERE substr(p.data_pedido, 1, 7) = ? AND p.status != 'cancelado'
            GROUP BY v.id ORDER BY faturamento DESC
            """,
            [PERIODOS[periodo]],
        ).fetchall()
    return {"periodo": periodo, "ranking": [dict(x) for x in linhas]}


# --- Ações de risco (gravam no banco; nada sai de verdade) ---------------------------------------
@tool
def reembolsar_cliente(pedido_id: int, valor: float, motivo: str) -> str:
    """Devolve dinheiro ao cliente de um pedido. Irreversível."""
    with connect() as conn:
        p = conn.execute("SELECT valor_total FROM pedidos WHERE id = ?", [pedido_id]).fetchone()
        if p is None:
            return f"Erro: pedido {pedido_id} não encontrado."
        ja = conn.execute("SELECT COALESCE(SUM(valor), 0) FROM reembolsos WHERE pedido_id = ?", [pedido_id]).fetchone()[0]
        if valor <= 0 or ja + valor > p["valor_total"]:
            return f"Erro: reembolso de R$ {valor:.2f} excede o saldo do pedido (R$ {p['valor_total'] - ja:.2f})."
        protocolo = _protocolo()
        conn.execute(
            "INSERT INTO reembolsos VALUES (?, ?, ?, ?, ?)",
            [protocolo, pedido_id, valor, motivo, datetime.now().isoformat(timespec="seconds")],
        )
    return f"Reembolso de R$ {valor:.2f} no pedido {pedido_id} registrado. Protocolo {protocolo}."


@tool
def cancelar_pedido(pedido_id: int, motivo: str) -> str:
    """Cancela um pedido que ainda não foi entregue. Irreversível."""
    with connect() as conn:
        p = conn.execute("SELECT status FROM pedidos WHERE id = ?", [pedido_id]).fetchone()
        if p is None:
            return f"Erro: pedido {pedido_id} não encontrado."
        if p["status"] != "em_transito":
            return f"Erro: o pedido {pedido_id} está '{p['status']}' e não pode ser cancelado."
        protocolo = _protocolo()
        conn.execute("UPDATE pedidos SET status = 'cancelado' WHERE id = ?", [pedido_id])
        conn.execute(
            "INSERT INTO cancelamentos VALUES (?, ?, ?, ?)",
            [protocolo, pedido_id, motivo, datetime.now().isoformat(timespec="seconds")],
        )
    return f"Pedido {pedido_id} cancelado. Protocolo {protocolo}."


def _protocolo() -> str:
    return f"SIM-{uuid.uuid4().hex[:6].upper()}"


def acoes_executadas() -> list[dict]:
    """Reembolsos e cancelamentos gravados, do mais recente ao mais antigo."""
    with connect() as conn:
        linhas = conn.execute(
            """
            SELECT 'reembolso' AS acao, protocolo, pedido_id, valor, motivo, criado_em FROM reembolsos
            UNION ALL
            SELECT 'cancelamento', protocolo, pedido_id, NULL, motivo, criado_em FROM cancelamentos
            ORDER BY criado_em DESC
            """
        ).fetchall()
    return [dict(x) for x in linhas]


# --- Catálogo ------------------------------------------------------------------------------------
LEITURA: list[BaseTool] = [consultar_indicadores, listar_pedidos_atrasados, buscar_pedido, ranking_vendedores]
RISCO: list[BaseTool] = [reembolsar_cliente, cancelar_pedido]
POR_NOME: dict[str, BaseTool] = {t.name: t for t in LEITURA + RISCO}


def ferramentas(incluir_acoes_de_risco: bool) -> list[BaseTool]:
    """As tools que o agente recebe neste passo."""
    return LEITURA + RISCO if incluir_acoes_de_risco else list(LEITURA)


def descrever(nome: str) -> str:
    t = POR_NOME.get(nome)
    return t.description if t else ""


def e_acao_de_risco(nome: str) -> bool:
    return any(t.name == nome for t in RISCO)


async def executar(nome: str, argumentos: dict) -> str:
    """Executa a tool e devolve o resultado como texto para o agente ler."""
    t = POR_NOME.get(nome)
    if t is None:
        return f"Erro: a ferramenta '{nome}' não existe."
    try:
        resultado = await t.ainvoke(argumentos)
    except Exception as exc:  # argumento inválido: o agente lê o erro e pode tentar de outro jeito
        return f"Erro ao chamar {nome}: {exc}"
    return resultado if isinstance(resultado, str) else json.dumps(resultado, ensure_ascii=False, default=str)

