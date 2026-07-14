# lru_cache.py — composição LRU: hash table + lista dupla (T05)
#
# Nota de projeto: o LRU só *compõe* as duas estruturas anteriores, sem tocá-las.
# A lista dupla (T03) dá a ordem de recência — mover-pra-frente e evict-da-cauda
# em O(1); a hash (T04) dá a busca por chave em O(1) médio. Sozinhas cada uma
# falha num eixo (achar por chave na lista é O(n); a hash não tem ordem); juntas
# se completam: a hash mapeia `chave -> Node` e o nó vive na lista de recência.
#
# O payload `_Item` mora dentro do `Node.value` de propósito: assim
# `linked_list.py` e `hash_table.py` ficam intactos (o `Node` do T03 só guarda
# `value`). O contador de acessos (`hits`) já nasce pronto aqui para o merge sort
# do T06 ordenar por ele.

from linked_list.linked_list import Node, LinkedList
from hash_table.hash_table import HashTable
from sorting.sorting import merge_sort


class _Item:
    """Payload que fica no `Node.value` — detalhe interno do LRU.

    Carrega três coisas que o nó cru do T03 não tem: a `key` (o evict pega o nó
    da cauda com `remove_tail` e precisa da chave para apagá-lo também na hash),
    o `value` cacheado, e o contador `hits` (quantos `get` acertaram este par —
    o T06 vai ordenar por ele com merge sort). O underscore sinaliza uso interno.
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.hits = 0


class LRUCache:
    """Cache LRU (Least Recently Used) por composição de hash + lista dupla.

    `self.recency` é a lista de recência: a frente é o par mais recente, a cauda
    é o próximo candidato a evict. `self.index` é a hash `chave -> Node`, que dá
    o acesso O(1) médio ao nó (que a lista sozinha não daria). Todo `get`/`put`
    faz um lookup na hash e uma religação O(1) na lista.
    """

    def __init__(self, capacity):
        """Guarda a capacidade e cria as duas estruturas vazias.

        `n_buckets = capacity`: como a cache nunca passa de `capacity` pares, o
        fator de carga fica <= 1 e as cadeias dos buckets ficam curtas (mantendo
        o O(1) médio da hash).
        """
        self.capacity = capacity
        self.recency = LinkedList()
        self.index = HashTable(capacity)

    def get(self, key):
        """Retorna o valor de `key`, ou `None` no miss. O(1) médio.

        No hit: conta o acesso (`hits += 1`) e renova a recência movendo o nó
        para a frente (`unlink` + `add_front`), protegendo-o do evict.
        """
        node = self.index.get(key)
        if node is None:
            return None
        node.value.hits += 1
        self.recency.unlink(node)
        self.recency.add_front(node)
        return node.value.value

    def put(self, key, value):
        """Insere ou atualiza o par (`key`, `value`). O(1) médio.

        Chave existente: atualiza o valor e move para a frente (escrever também
        é um acesso de recência); não conta `hits` (só `get` conta hit) nem mexe
        no tamanho. Chave nova com a cache cheia: evicta a cauda (o par menos
        recente) da lista e da hash antes de inserir o novo na frente.
        """
        node = self.index.get(key)
        if node is not None:
            node.value.value = value
            self.recency.unlink(node)
            self.recency.add_front(node)
            return
        if len(self.index) == self.capacity:
            victim = self.recency.remove_tail()
            self.index.remove(victim.value.key)
        item = _Item(key, value)
        node = Node(item)
        self.recency.add_front(node)
        self.index.put(key, node)

    def sorted_by_hits(self):
        """Relatório de inspeção: itens ordenados por acessos (hits) decrescente.

        Snapshot **não-destrutivo**: a recência (`self.recency`) NÃO pode ser
        reordenada — o merge sort religa `next`, então rodá-lo nos nós reais
        destruiria a lista dupla. Por isso montamos um encadeamento simples de
        `Node`s *novos* (ligados só por `next`) espelhando os `_Item`s da recência,
        ordenamos esse snapshot com `merge_sort` e devolvemos uma lista de tuplas
        `(key, value, hits)` na ordem final. A ordem de recência do cache fica
        intacta — ordenar por frequência é uma leitura, não muda a política LRU.
        """
        # Espelha a recência (frente -> trás) num encadeamento simples de Nós
        # novos: mexer no `next` deles não toca `self.recency`; o `_Item` é
        # compartilhado por referência, mas só lido.
        head = None
        tail = None
        current = self.recency.head.next
        while current is not self.recency.tail:
            snapshot = Node(current.value)
            if head is None:
                head = snapshot
                tail = snapshot
            else:
                tail.next = snapshot
                tail = snapshot
            current = current.next
        # Ordena o snapshot por hits (decrescente) religando `next`.
        head = merge_sort(head, lambda n: n.value.hits)
        # Materializa o resultado como lista de tuplas na ordem final.
        result = []
        current = head
        while current is not None:
            item = current.value
            result.append((item.key, item.value, item.hits))
            current = current.next
        return result

    def __len__(self):
        """Número de pares vivos na cache."""
        return len(self.index)

    def __str__(self):
        """Inspeção da recência, da frente (mais recente) para trás: cada nó vira
        `chave=valor(hits=N)`; cache vazia vira `(vazio)`. Serve à demo/testes."""
        if self.recency.is_empty():
            return "(vazio)"
        parts = []
        current = self.recency.head.next
        while current is not self.recency.tail:
            item = current.value
            parts.append("{}={}(hits={})".format(item.key, item.value, item.hits))
            current = current.next
        return " ".join(parts)
