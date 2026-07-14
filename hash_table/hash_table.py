# hash_table.py — hash table com chaining (T04)
#
# Nota do critério de aceite — o O(1) desta hash é MÉDIO, não garantido: vale
# enquanto as cadeias dos buckets são curtas. Dois degradadores: (a) fator de
# carga alto (`size / n_buckets` — mais pares que buckets) enche as cadeias; e
# (b) hash ruim — se `hash(key) % n_buckets` concentra chaves em poucos buckets,
# a cadeia vira uma lista linear e a busca cai para O(n). No pior caso (tudo no
# mesmo bucket) a hash degenera numa simples lista encadeada.


class _Entry:
    """Elo da cadeia de um bucket — detalhe interno da hash table.

    Singly-linked: guarda o par (`key`, `value`) e aponta para o próximo elo do
    mesmo bucket (`next`). Um bucket é a *cabeça* de uma cadeia desses elos, ou
    `None` quando vazio. O underscore no nome sinaliza uso interno do módulo.
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    """Tabela hash com resolução de colisão por chaining (cadeia por bucket).

    A tabela é um array de tamanho fixo (`n_buckets`); o bucket de uma chave é
    `hash(key) % n_buckets`. Como muitas chaves possíveis são dobradas em poucos
    buckets, duas chaves distintas podem cair no mesmo bucket (colisão). O
    chaining resolve guardando, em cada bucket, uma cadeia de todos os pares que
    caíram ali; a busca vai direto ao bucket e percorre só aquela cadeia curta.

    Capacidade fixa: a tabela é dimensionada uma vez na criação. Resize/rehash
    está fora de escopo do projeto.
    """

    def __init__(self, n_buckets):
        """Cria a tabela com `n_buckets` buckets vazios.

        `self.buckets` é o array: cada posição é a cabeça de uma cadeia de
        `_Entry` (`None` = bucket vazio). `self.size` conta os pares — serve a
        `__len__` e ao fator de carga (`size / n_buckets`).
        """
        self.n_buckets = n_buckets
        self.buckets = [None] * n_buckets
        self.size = 0

    def _index(self, key):
        """Índice do bucket de `key`: `hash(key) % n_buckets`.

        `hash()` só gera o inteiro; o `%` o dobra dentro do array. O `%` do
        Python já devolve índice não-negativo mesmo quando `hash(key)` é
        negativo, então o resultado é sempre um índice válido de `buckets`.
        """
        return hash(key) % self.n_buckets

    def put(self, key, value):
        """Insere o par (`key`, `value`) ou atualiza o valor se a chave já existe.

        Percorre a cadeia do bucket comparando `key`: se achar, atualiza o
        `value` no lugar (não duplica, `size` não muda); se não achar, cria um
        `_Entry` e o insere na *frente* do bucket (novo vira a nova cabeça) e
        incrementa `size`. Médio O(1).
        """
        idx = self._index(key)
        current = self.buckets[idx]
        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next
        entry = _Entry(key, value)
        entry.next = self.buckets[idx]
        self.buckets[idx] = entry
        self.size += 1

    def get(self, key):
        """Retorna o valor de `key`, ou `None` se ausente (miss → `None`).

        Percorre a cadeia do bucket comparando `key`. O miss devolvendo `None`
        se alinha ao `get` do LRU no T05. Médio O(1).
        """
        current = self.buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def remove(self, key):
        """Remove `key` e retorna o valor removido, ou `None` se ausente.

        Percorre a cadeia guardando o elo *anterior* (é singly-linked: sem
        `prev`, para religar a cadeia é preciso do anterior). Ao achar, religa
        `anterior.next = atual.next`, ou `buckets[idx] = atual.next` quando o
        alvo é a cabeça do bucket; decrementa `size`. Chave ausente devolve
        `None`, sem erro. Médio O(1).
        """
        idx = self._index(key)
        previous = None
        current = self.buckets[idx]
        while current is not None:
            if current.key == key:
                if previous is None:
                    self.buckets[idx] = current.next
                else:
                    previous.next = current.next
                self.size -= 1
                return current.value
            previous = current
            current = current.next
        return None

    def __len__(self):
        """Número de pares guardados. Conveniência para testes e para
        materializar o fator de carga (`len / n_buckets`)."""
        return self.size

    def __str__(self):
        """Inspeção visual: uma linha por bucket ocupado, mostrando os pares da
        cadeia. Serve às provas visuais nos testes e à demo."""
        lines = []
        for idx in range(self.n_buckets):
            current = self.buckets[idx]
            if current is None:
                continue
            pairs = []
            while current is not None:
                pairs.append("{}: {}".format(current.key, current.value))
                current = current.next
            lines.append("[{}] {}".format(idx, " -> ".join(pairs)))
        return "\n".join(lines)
