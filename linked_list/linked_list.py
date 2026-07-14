# linked_list.py — lista duplamente encadeada com sentinelas (T03)


class Node:
    """Nó de uma lista duplamente encadeada: guarda um valor e conhece os dois
    vizinhos (`prev` e `next`)."""

    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class LinkedList:
    """Lista duplamente encadeada com nós sentinela.

    Esta lista serve o cache LRU (T05): a inserção é sempre na frente (= mais
    recente) e a cauda é a ponta reservada ao *evict* (menos recente). A remoção
    tem um único primitivo por referência (`unlink`); `remove_tail` é uma
    conveniência construída sobre ele.

    Os nós `head` e `tail` são sentinelas: não guardam dados. Existem só para que
    todo nó real tenha sempre um vizinho dos dois lados, eliminando os casos
    especiais de borda (lista vazia, remover cabeça/cauda) da lista simples.
    """

    def __init__(self):
        """Cria as duas sentinelas e as liga: lista vazia = head <-> tail."""
        self.head = Node(None)
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def is_empty(self):
        """True quando não há nó real entre as sentinelas. O(1)."""
        return self.head.next is self.tail

    def add_front(self, node):
        """Insere um Node logo após `head` (frente = mais recente). O(1).

        Religa os 4 ponteiros para encaixar `node` entre `head` e o antigo
        primeiro nó.
        """
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def unlink(self, node):
        """Primitivo de remoção: desconecta `node` só pela referência, sem
        travessia. O(1).

        Ao remover um nó X (entre A e B) mudam 4 ponteiros: A.next -> B e
        B.prev -> A (os sobreviventes se ligam pulando X), e X.next / X.prev ->
        None (o nó órfão se solta). Com as sentinelas o mesmo código serve para
        frente e cauda: todo nó real sempre tem `prev` e `next` não-nulos, então
        não há mais o caso especial "é a cabeça?" da lista simples.
        """
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    def remove_tail(self):
        """Conveniência sobre `unlink`: remove e retorna o último nó real.

        Se a lista está vazia retorna None. Senão localiza a vítima na cauda
        (`tail.prev`), a desconecta e a devolve — o chamador (LRU) precisa do nó
        de volta para pegar a chave dele no evict. O(1).
        """
        if self.is_empty():
            return None
        node = self.tail.prev
        self.unlink(node)
        return node

    def __str__(self):
        """Travessia da frente para trás: '30 <-> 20 <-> 10'; vazia = '(vazia)'."""
        if self.is_empty():
            return "(vazia)"
        parts = []
        current = self.head.next
        while current is not self.tail:
            parts.append(str(current.value))
            current = current.next
        return " <-> ".join(parts)
