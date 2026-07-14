# sorting.py — merge sort na lista encadeada (T06)
#
# Por que merge sort e não quicksort numa lista encadeada:
# merge sort só exige acesso *sequencial*. Ele acha o meio com ponteiro
# lento/rápido, divide o encadeamento em duas metades e as intercala religando
# apenas `next` — O(1) de ponteiros extras e de forma estável. Quicksort, ao
# contrário, particiona em torno de um pivô e sua eficiência vem do acesso
# *aleatório*/indexação de arrays; numa lista sem índice cada acesso por posição
# é O(n), então o particionamento fica caro. Logo, a lista encadeada é o terreno
# natural do merge sort.
#
# Este sort religa `next` in-place: **não** materializa array durante a
# ordenação. Opera sobre um encadeamento simples de `Node` (ligados por `next`,
# terminado em `None`), não sobre a `LinkedList` com sentinelas.
#
# Ordena **decrescente** de propósito (relatório "mais acessados primeiro").
# Empates preservam a ordem de entrada — estável, graças ao `>=` no merge.

from linked_list.linked_list import Node


def merge_sort(head, key):
    """Ordena o encadeamento a partir de `head` em ordem decrescente por
    `key(node)`, religando `next`. Retorna a nova cabeça. O(n log n).

    Divide-e-conquista: parte a cadeia ao meio (`_split`), ordena cada metade
    recursivamente e intercala as duas metades ordenadas (`_merge`). O caso base
    é uma cadeia de 0 ou 1 nó, que já está ordenada.
    """
    # Caso base: 0 ou 1 nó já está ordenado.
    if head is None or head.next is None:
        return head

    left, right = _split(head)
    left = merge_sort(left, key)
    right = merge_sort(right, key)
    return _merge(left, right, key)


def _split(head):
    """Parte o encadeamento em duas metades e retorna `(left, right)`.

    Usa ponteiros lento/rápido: o rápido anda de dois em dois, o lento de um em
    um; quando o rápido chega ao fim, o lento está no meio. Corta o encadeamento
    ali (`slow.next = None`), separando as duas metades. Com N par as metades
    ficam n/2 + n/2; com N ímpar o nó extra fica na esquerda.
    """
    slow = head
    fast = head.next
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    right = slow.next
    slow.next = None
    return head, right


def _merge(left, right, key):
    """Intercala dois encadeamentos já ordenados (decrescente) em um só,
    religando `next`. Retorna a cabeça do resultado.

    A cada passo anexa o nó de **maior** `key` (ordem decrescente). Um nó
    sentinela `dummy` elimina o caso de borda da primeira ligação; `tail`
    acompanha o fim da cadeia sendo montada. O `>=` garante estabilidade: em
    empate o nó da esquerda (que entrou antes) vem primeiro.
    """
    dummy = Node(None)
    tail = dummy
    while left is not None and right is not None:
        if key(left) >= key(right):
            tail.next = left
            left = left.next
        else:
            tail.next = right
            right = right.next
        tail = tail.next
    # Anexa o resto (uma das cadeias ainda tem nós, já ordenados).
    tail.next = left if left is not None else right
    return dummy.next
