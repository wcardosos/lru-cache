# tests_lru_cache.py — testes do LRUCache (T05), Python puro, só assert.
# Rodar da raiz com: python -m lru_cache.tests_lru_cache

from lru_cache.lru_cache import LRUCache


def test_put_get_basic():
    """Com capacidade folgada, `get` devolve cada valor inserido e uma chave
    ausente devolve `None`."""
    sut = LRUCache(10)
    sut.put("a", 1)
    sut.put("b", 2)
    sut.put("c", 3)
    assert sut.get("a") == 1
    assert sut.get("b") == 2
    assert sut.get("c") == 3
    assert sut.get("x") is None


def test_update_does_not_grow():
    """Reescrever uma chave existente troca o valor sem crescer a cache."""
    sut = LRUCache(10)
    sut.put("k", "a")
    assert len(sut) == 1
    sut.put("k", "b")
    assert sut.get("k") == "b"
    assert len(sut) == 1


def test_eviction_lru():
    """Critério de aceite: o `get('a')` renova a recência de `a` e empurra `b`
    para a cauda, então a inserção de `c` na cache cheia evicta `b`, não `a`."""
    sut = LRUCache(2)
    sut.put("a", 1)
    sut.put("b", 2)
    sut.get("a")  # protege 'a': 'b' passa a ser o menos recente
    sut.put("c", 3)
    assert sut.get("b") is None  # evictado
    assert sut.get("a") == 1  # sobreviveu
    assert sut.get("c") == 3  # sobreviveu
    assert len(sut) == 2


def test_hit_counter():
    """Cada `get` que acerta incrementa `hits`; um miss não conta nada.
    Caminho branco: alcança o nó pela hash interna (`sut.index`)."""
    sut = LRUCache(10)
    sut.put("a", 1)
    assert sut.index.get("a").value.hits == 0
    sut.get("a")
    sut.get("a")
    assert sut.index.get("a").value.hits == 2
    sut.get("ausente")  # miss não mexe em nada
    assert sut.index.get("a").value.hits == 2


def test_initial_state():
    """Cache recém-criada: vazia, todo `get` é miss e `str` é `(vazio)`."""
    sut = LRUCache(5)
    assert len(sut) == 0
    assert sut.get("qualquer") is None
    assert str(sut) == "(vazio)"


def test_sorted_by_hits_snapshot():
    """`sorted_by_hits` devolve as tuplas em ordem decrescente de hits sem tocar
    a recência (snapshot não-destrutivo); cache vazia devolve `[]`."""
    assert LRUCache(3).sorted_by_hits() == []  # vazia -> lista vazia

    sut = LRUCache(3)
    sut.put("a", 1)
    sut.put("b", 2)
    sut.put("c", 3)
    # Hits desiguais: b=3, c=1, a=0.
    sut.get("b")
    sut.get("b")
    sut.get("b")
    sut.get("c")

    before = str(sut)  # ordem de recência antes do relatório
    report = sut.sorted_by_hits()

    # (a) ordem decrescente de hits.
    hits = [h for (_, _, h) in report]
    assert hits == [3, 1, 0]
    assert report[0] == ("b", 2, 3)
    # (b) não-destrutivo: a recência não mudou.
    assert str(sut) == before


test_put_get_basic()
test_update_does_not_grow()
test_eviction_lru()
test_hit_counter()
test_initial_state()
test_sorted_by_hits_snapshot()
print("OK: todos os testes passaram")
