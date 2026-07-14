# tests_linked_list.py — testes da lista duplamente encadeada (T03)
# Python puro, sem lib de teste. Rodar da raiz com:
#   python -m linked_list.tests_linked_list

from linked_list.linked_list import Node, LinkedList


def test_add_front_traversal():
    """add_front + travessia: o último inserido fica na frente."""
    sut = LinkedList()
    sut.add_front(Node(10))
    sut.add_front(Node(20))
    sut.add_front(Node(30))
    assert str(sut) == "30 <-> 20 <-> 10", str(sut)


def test_unlink_by_reference():
    """Critério de aceite: guardar a referência de um nó do meio, desconectá-la só
    pela referência e conferir integridade na frente."""
    sut = LinkedList()
    sut.add_front(Node(10))
    sut.add_front(Node(20))
    sut.add_front(Node(30))
    middle = sut.head.next.next  # o nó do meio (20)
    assert middle.value == 20
    sut.unlink(middle)
    assert str(sut) == "30 <-> 10", str(sut)
    assert middle.prev is None and middle.next is None


def test_prev_integrity():
    """Percorrer de tail.prev para trás deve dar o inverso da travessia para frente
    (prova que os `prev` foram religados)."""
    sut = LinkedList()
    sut.add_front(Node(10))
    sut.add_front(Node(30))

    forward = []
    current = sut.head.next
    while current is not sut.tail:
        forward.append(current.value)
        current = current.next

    backward = []
    current = sut.tail.prev
    while current is not sut.head:
        backward.append(current.value)
        current = current.prev

    assert forward == [30, 10], forward
    assert backward == list(reversed(forward)), backward


def test_remove_tail():
    """remove_tail: remove e retorna o último nó real; chamadas repetidas esvaziam."""
    sut = LinkedList()
    sut.add_front(Node(10))
    sut.add_front(Node(30))  # ordem: 30 <-> 10
    tail_node = sut.remove_tail()
    assert tail_node.value == 10 and isinstance(tail_node, Node)
    assert str(sut) == "30", str(sut)
    tail_node = sut.remove_tail()
    assert tail_node.value == 30
    assert sut.is_empty()
    assert sut.remove_tail() is None


def test_initial_state():
    """Lista vazia / sentinelas."""
    fresh = LinkedList()
    assert fresh.is_empty() is True
    assert str(fresh) == "(vazia)"
    assert fresh.head.next is fresh.tail
    assert fresh.tail.prev is fresh.head
    assert fresh.remove_tail() is None


test_add_front_traversal()
test_unlink_by_reference()
test_prev_integrity()
test_remove_tail()
test_initial_state()
print("OK: todos os testes passaram")
