# tests_hash_table.py — testes da hash table com chaining (T04)
# Python puro, sem lib de teste. Rodar da raiz com:
#   python -m hash_table.tests_hash_table
#
# Nota de determinismo: `hash()` de strings é randomizado por processo
# (PYTHONHASHSEED), então o teste de colisão usa chaves inteiras — em CPython
# `hash(int) == int` para inteiros não-negativos, deixando o bucket previsível.

from hash_table.hash_table import HashTable


def test_put_get_basic():
    """put de alguns pares; get devolve cada valor; chave ausente → None."""
    sut = HashTable(8)
    sut.put("a", 1)
    sut.put("b", 2)
    sut.put("c", 3)
    assert sut.get("a") == 1
    assert sut.get("b") == 2
    assert sut.get("c") == 3
    assert sut.get("ausente") is None


def test_update_does_not_duplicate():
    """put(k, "a") e depois put(k, "b"): o valor troca e len não cresce na 2ª escrita."""
    sut = HashTable(8)
    sut.put("k", "a")
    assert len(sut) == 1
    sut.put("k", "b")
    assert sut.get("k") == "b"
    assert len(sut) == 1


def test_collision_same_bucket():
    """Critério de aceite: 1 e 5 caem no mesmo bucket (ambos % 4 == 1). As duas
    coexistem na cadeia, cada uma recuperável com seu próprio valor."""
    sut = HashTable(4)
    assert sut._index(1) == sut._index(5)  # prova que colidem
    sut.put(1, "um")
    sut.put(5, "cinco")
    assert sut.get(1) == "um"
    assert sut.get(5) == "cinco"
    assert len(sut) == 2


def test_remove_both_branches():
    """No bucket colidido a ordem (insere-na-frente) é 5 → 1. Remover 5 exercita o
    ramo cabeça; remover 1 exercita o ramo com anterior. A cada remoção a outra
    do mesmo bucket continua recuperável (prova a religação)."""
    sut = HashTable(4)
    sut.put(1, "um")
    sut.put(5, "cinco")

    # ramo cabeça: buckets[idx] = atual.next
    assert sut.remove(5) == "cinco"
    assert sut.get(5) is None
    assert sut.get(1) == "um"  # a que ficou continua acessível
    assert len(sut) == 1

    # reconstroi para exercitar o ramo com anterior (remover o não-cabeça)
    sut.put(5, "cinco")  # cadeia volta a 5 → 1
    assert sut.remove(1) == "um"  # ramo com anterior: anterior.next = atual.next
    assert sut.get(1) is None
    assert sut.get(5) == "cinco"
    assert len(sut) == 1

    # remove de chave ausente → None e sem erro
    assert sut.remove(999) is None


def test_initial_state():
    """Tabela nova: sem pares, todo get e todo remove devolvem None."""
    sut = HashTable(8)
    assert len(sut) == 0
    assert sut.get("qualquer") is None
    assert sut.remove("qualquer") is None


test_put_get_basic()
test_update_does_not_duplicate()
test_collision_same_bucket()
test_remove_both_branches()
test_initial_state()
print("OK: todos os testes passaram")
