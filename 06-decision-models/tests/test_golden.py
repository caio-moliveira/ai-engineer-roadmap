from collections import Counter

import pytest

from common import golden

TICKET_FILAS = {"financeiro", "tecnico", "comercial", "conta"}


@pytest.mark.parametrize("name", list(golden.DATASETS))
def test_datasets_carregam_com_ids_unicos(name):
    items = golden.load(name)
    assert items
    assert len({i.id for i in items}) == len(items)


def test_tickets_tem_todos_os_rotulos():
    for item in golden.load("tickets"):
        assert item.labels["fila"] in TICKET_FILAS
        assert item.labels["urgencia"] in (0, 1, 2)
        assert item.labels["rota"] in ("barato", "caro")
        assert item.labels["categoria"]


def test_categorias_pertencem_a_uma_unica_fila():
    pares = {(i.labels["fila"], i.labels["categoria"]) for i in golden.load("tickets")}
    por_categoria = Counter(c for _, c in pares)
    assert all(n == 1 for n in por_categoria.values())


def test_rerank_tem_relevantes_em_toda_pergunta():
    for q in golden.load_rerank():
        assert len(q.candidatos) == 10
        assert any(c.relevancia == 2 for c in q.candidatos)


def test_sales_adaptado_do_workshop():
    items = golden.load("sales")
    assert len(items) == 80
    assert set(items[0].labels) == {"tool", "injection", "dado_sensivel", "fora_escopo"}


def test_filtro_por_tag():
    assert all("adversarial" in i.tags for i in golden.load("sales", tag="adversarial"))
    assert len(golden.load("tickets", limit=5)) == 5
