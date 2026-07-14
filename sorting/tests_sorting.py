# tests_sorting.py — testes do merge sort na lista encadeada (T06)
# Python puro, sem lib de teste. Rodar da raiz com:
#   python -m sorting.tests_sorting

from linked_list.linked_list import Node
from sorting.sorting import merge_sort


def build_chain(values):
    """Monta um encadeamento simples de `Node` ligados por `next` (terminado em
    None) a partir de `values`, preservando a ordem. Retorna a cabeça (ou None)."""
    head = None
    tail = None
    for value in values:
        node = Node(value)
        if head is None:
            head = node
            tail = node
        else:
            tail.next = node
            tail = node
    return head


def to_values(head):
    """Percorre o encadeamento por `next` coletando `node.value` numa lista."""
    values = []
    current = head
    while current is not None:
        values.append(current.value)
        current = current.next
    return values


def test_empty():
    """Cadeia vazia: merge_sort(None) devolve None."""
    assert merge_sort(None, lambda n: n.value) is None


def test_single():
    """Um único nó volta ele mesmo, com next None."""
    node = Node(42)
    result = merge_sort(node, lambda n: n.value)
    assert result is node
    assert result.next is None


def test_even_n():
    """Critério de aceite (N par): [3,1,4,2] -> [4,3,2,1]."""
    head = build_chain([3, 1, 4, 2])
    result = merge_sort(head, lambda n: n.value)
    assert to_values(result) == [4, 3, 2, 1], to_values(result)


def test_odd_n():
    """Critério de aceite (N ímpar): [3,1,2,5,4] -> [5,4,3,2,1]."""
    head = build_chain([3, 1, 2, 5, 4])
    result = merge_sort(head, lambda n: n.value)
    assert to_values(result) == [5, 4, 3, 2, 1], to_values(result)


def test_already_sorted():
    """Já decrescente permanece igual."""
    head = build_chain([5, 4, 3, 2, 1])
    result = merge_sort(head, lambda n: n.value)
    assert to_values(result) == [5, 4, 3, 2, 1], to_values(result)


def test_reversed():
    """Crescente vira decrescente."""
    head = build_chain([1, 2, 3, 4, 5])
    result = merge_sort(head, lambda n: n.value)
    assert to_values(result) == [5, 4, 3, 2, 1], to_values(result)


def test_stable_ties():
    """Estabilidade: com chave repetida, a ordem de entrada entre empates é
    preservada. Usa tuplas (hits, tag) e ordena só por hits."""
    entrada = [(2, "a"), (1, "b"), (2, "c"), (1, "d"), (2, "e")]
    head = build_chain(entrada)
    result = merge_sort(head, lambda n: n.value[0])
    saida = to_values(result)
    # hits em ordem decrescente
    assert [hits for hits, _ in saida] == [2, 2, 2, 1, 1], saida
    # tags dos hits==2 na ordem original (a, c, e); dos hits==1 (b, d)
    assert [tag for hits, tag in saida if hits == 2] == ["a", "c", "e"], saida
    assert [tag for hits, tag in saida if hits == 1] == ["b", "d"], saida


class _Counter:
    """Objeto de teste que espelha o uso real: carrega um contador `hits`
    (sem depender do `_Item` privado do cache)."""

    def __init__(self, hits):
        self.hits = hits


def test_by_hits():
    """Uso real: nós cujo value tem atributo .hits, ordenados decrescente."""
    head = build_chain([_Counter(1), _Counter(7), _Counter(3), _Counter(7)])
    result = merge_sort(head, lambda n: n.value.hits)
    assert [c.hits for c in to_values(result)] == [7, 7, 3, 1]


test_empty()
test_single()
test_even_n()
test_odd_n()
test_already_sorted()
test_reversed()
test_stable_ties()
test_by_hits()
print("OK: todos os testes passaram")
