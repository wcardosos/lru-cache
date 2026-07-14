# LRU Cache

Trabalho de Estrutura de Dados: implementação **manual** de um cache LRU (*Least
Recently Used*). Todas as estruturas são feitas manualmente — **proibido usar `dict`,
`sorted()` ou `list.sort()`**. O único recurso nativo aproveitado é a função
`hash()`, e só para gerar o inteiro que vira índice de bucket (`hash(key) %
n_buckets`); a resolução de colisão, a ordem de recência e a ordenação são todas
implementadas do zero.

---

## Contexto: por que um cache LRU

Imagine uma consulta cara e repetida — um "banco lento" onde cada leitura leva
alguns segundos  para executar (é o que o `main.py` simula com `time.sleep(1.3)`).
Se as mesmas chaves são pedidas de novo e de novo, pagar o preço toda vez é
desperdício. Um **cache** guarda os resultados quentes em memória e responde na
hora nas próximas vezes.

Mas memória é finita: o cache tem uma **capacidade** máxima. Quando ele enche e
chega um item novo, é preciso **despejar** (evict) algum item antigo para abrir
espaço. A pergunta é: *qual*? A política **LRU** despeja o **menos recentemente
usado** — o item que ficou mais tempo sem ser tocado.

> **Por quê LRU:** a aposta é a **localidade temporal** — o que foi usado há
> pouco tende a ser usado de novo em breve, então o item "esfriando" há mais
> tempo é o melhor candidato a sair. É a política clássica de caches reais (p.
> ex. Redis com `maxmemory-policy allkeys-lru`) na frente de bancos e APIs.

---

## Como rodar

Não há dependências externas — basta Python 3. Rode a partir da raiz do
repositório:

```bash
python main.py            # roda a demonstração de ponta a ponta
```

A demo conta a história completa da cache: insere mais chaves do que a
capacidade (mostrando um eviction), faz acessos que renovam a recência e contam
*hits*, busca por chave via hash e, no fim, imprime um relatório ordenado pelos
mais acessados. Cada linha marca `MISS` (~1.30s, foi ao "banco lento") ou `HIT`
(~0.00s, veio do cache).

Cada estrutura mora num pacote junto com seu teste. Rode os testes da raiz com a
flag `-m` (que coloca a raiz no path e resolve os imports de pacote):

```bash
python -m linked_list.tests_linked_list
python -m hash_table.tests_hash_table
python -m lru_cache.tests_lru_cache
python -m sorting.tests_sorting
```

---

## Mapa dos arquivos

Cada estrutura é um **pacote** (uma pasta com `__init__.py`) que reúne o módulo
de código e o teste correspondente. O `main.py` é o ponto de entrada e fica na
raiz:

```
.
├── linked_list/
│   ├── __init__.py
│   ├── linked_list.py          # código
│   └── tests_linked_list.py    # teste
├── hash_table/
│   ├── __init__.py
│   ├── hash_table.py
│   └── tests_hash_table.py
├── sorting/
│   ├── __init__.py
│   ├── sorting.py
│   └── tests_sorting.py
├── lru_cache/
│   ├── __init__.py
│   ├── lru_cache.py
│   └── tests_lru_cache.py
├── main.py                     # demonstração (ponto de entrada)
└── README.md
```

| Módulo | Responsabilidade |
| --- | --- |
| `linked_list/linked_list.py` | Lista **duplamente** encadeada com sentinelas — dá a ordem de recência em O(1). |
| `hash_table/hash_table.py` | Hash table com **chaining** — dá a busca por chave em O(1) médio. |
| `lru_cache/lru_cache.py` | `LRUCache` — **compõe** hash + lista dupla; é o coração do projeto. |
| `sorting/sorting.py` | Merge sort sobre encadeamento simples de `Node` — o relatório por *hits*. |
| `main.py` | Demonstração "banco lento" de ponta a ponta. |
| `*/tests_*.py` | Teste de cada pacote (Python puro, só `assert`): lista dupla, hash (com colisão proposital), composição LRU (get/put/evict) e merge sort (N par/ímpar, estabilidade). |

> **Nota de import:** os pacotes se importam entre si por caminho completo — ex.:
> `from hash_table.hash_table import HashTable`. Isso resolve a partir da raiz do
> repositório, por isso a demo roda com `python main.py` (que coloca a raiz no
> path) e os testes com `python -m pacote.tests_pacote` (idem). Não há truque de
> `sys.path`: é o layout de pacote padrão do Python.

---

## As peças, uma a uma

O cache é feito de duas estruturas independentes. Vale entendê-las sozinhas
antes de ver como se compõem.

### 1. Lista duplamente encadeada (`linked_list/linked_list.py`)

Uma lista encadeada é uma sequência de **nós**, cada um guardando um valor e uma
referência ao próximo. Na versão **dupla**, o nó conhece os **dois** vizinhos —
`prev` e `next` — então dá para andar nos dois sentidos e, principalmente,
**remover um nó só com a referência dele**, sem varrer a lista para achar o
anterior.

O truque de implementação são os **sentinelas**: `head` e `tail` são dois nós
falsos, que não guardam dado nenhum. Eles existem só para que **todo nó real
tenha sempre um vizinho dos dois lados**. Isso elimina os casos de borda que
atormentam a lista simples ("é o primeiro nó?", "a lista está vazia?"): o mesmo
código de religação serve para qualquer posição.

```
lista vazia:   head <-> tail
com 3 itens:   head <-> n1 <-> n2 <-> n3 <-> tail
               (frente = mais recente)      (cauda = evict)
```

As operações que o cache usa são todas **O(1)**:

- `add_front(node)` — insere logo após `head` (frente = mais recente).
- `unlink(node)` — desconecta um nó pela referência, sem travessia.
- `remove_tail()` — remove e **retorna** o último nó real (o candidato a evict);
  devolve o nó porque quem chama precisa da chave dele.

No `unlink`, ao tirar um nó X que está entre A e B, mudam **4 ponteiros**:

```
antes:   A <-> X <-> B
         A.next = X,  X.prev = A,  X.next = B,  B.prev = X

depois:  A <-> B          (X solto)
         A.next = B       (sobreviventes se ligam pulando X)
         B.prev = A
         X.next = None    (o nó órfão se desprende)
         X.prev = None
```

> **Por quê aqui:** é a lista que dá a **ordem de recência**. Cada acesso faz um
> *move-to-front* (`unlink` + `add_front`) e cada eviction tira o nó da **cauda**
> — as duas coisas em O(1). Um array daria a mesma ordem, mas mover um item para
> a frente custaria O(n) de deslocamento a cada acesso.

### 2. Hash table com chaining (`hash_table/hash_table.py`)

Uma hash table guarda pares `chave → valor` num **array de buckets** de tamanho
fixo. O bucket de uma chave é `hash(key) % n_buckets`: `hash()` gera um inteiro
qualquer e o `%` o "dobra" para dentro do array (o `%` do Python já devolve
índice não-negativo mesmo com `hash` negativo).

Como muitas chaves possíveis são dobradas em poucos buckets, duas chaves
distintas podem cair no mesmo bucket — uma **colisão**. A resolução aqui é por
**chaining**: cada bucket guarda uma **cadeia** (lista encadeada simples de
`_Entry`) com todos os pares que caíram ali. A busca vai direto ao bucket e
percorre só aquela cadeia.

```
buckets
  [0] -> None
  [1] -> ("gato": 3) -> ("rato": 9)   # duas chaves colidiram no bucket 1
  [2] -> ("pato": 7)
  [3] -> None
```

A API é `put(key, value)`, `get(key)` (miss → `None`), `remove(key)` (devolve o
valor removido) e `__len__` (número de pares, usado para o fator de carga).

> **Por quê o O(1) é "médio":** vale **enquanto as cadeias são curtas**. Dois
> degradadores: (a) **fator de carga** alto (`size / n_buckets` — mais pares que
> buckets) enche as cadeias; (b) **hash ruim**, que concentra chaves em poucos
> buckets. No pior caso (tudo no mesmo bucket) a hash degenera numa lista linear
> e a busca cai para **O(n)**. No cache isso é evitado dimensionando
> `n_buckets = capacity` (ver adiante), o que mantém o fator de carga ≤ 1.

---

## Composição: como o LRU junta as duas (`lru_cache/lru_cache.py`)

Este é o ponto central do projeto. Cada estrutura, sozinha, falha num eixo:

- a **lista** tem ordem de recência, mas achar um par por chave é **O(n)**
  (precisa varrer);
- a **hash** acha por chave em O(1), mas **não tem noção de ordem**.

Juntas se completam: a **hash mapeia `chave → Node`** e **o próprio nó vive na
lista de recência**. O mesmo nó é apontado pelos dois eixos ao mesmo tempo.

```
        índice (hash)                 recência (lista dupla)
     chave -> Node --------.
                            v
   head <-> [b] <-> [c] <-> [d] <-> tail
             ^                ^
             |                |
         frente (recente)   cauda (evict)
```

Achar `Node` pela chave é O(1) (hash); mover esse nó na lista é O(1)
(`unlink`/`add_front`). Assim **todo `get`/`put` é O(1) médio**.

### O truque do `_Item`

O `Node` da lista (T03) só sabe guardar um `value` genérico, e não queremos mexer
em `linked_list.py` nem em `hash_table.py` — eles estão fechados. A solução é
guardar um objeto `_Item` **dentro** do `Node.value`. O `_Item` carrega três
coisas que o nó cru não tem:

- `key` — o eviction pega o nó da cauda e precisa da chave para apagá-lo
  **também** na hash;
- `value` — o valor cacheado de fato;
- `hits` — quantos `get` acertaram este par (o merge sort vai ordenar por isto).

### `get(key)` passo a passo

```
node = index.get(key)          # lookup O(1) na hash
if node is None: return None    # miss
node.value.hits += 1            # conta o acesso
recency.unlink(node)            # tira da posição atual  ]
recency.add_front(node)         # e joga para a frente    ] move-to-front, O(1)
return node.value.value         # valor cacheado
```

### `put(key, value)` passo a passo

- **Chave já existe:** atualiza o `value` e move o nó para a frente (escrever
  também conta como acesso de recência). **Não** incrementa `hits` — só `get`
  conta hit — nem muda o tamanho.
- **Chave nova com a cache cheia:** antes de inserir, **evicta a cauda**
  (`remove_tail`) e remove essa mesma chave da hash; só então cria o `_Item`,
  embrulha num `Node` e insere na frente, registrando na hash.

### Complexidade

| Operação | Custo | Por quê |
| --- | --- | --- |
| `get` | O(1) médio | lookup na hash + religação O(1) na lista |
| `put` | O(1) médio | idem; eviction também é O(1) |
| evict | O(1) | `remove_tail` na lista + `remove` na hash |

---

## Ordenação: merge sort na lista encadeada (`sorting/sorting.py`)

O trabalho exige uma ordenação implementada à mão. Ela produz o **relatório por
acessos** (`sorted_by_hits`): os itens do mais para o menos acessado.

O algoritmo escolhido é o **merge sort**, e a escolha não é acidental:

> **Por quê merge sort e não quicksort numa lista encadeada:** o merge sort só
> exige acesso **sequencial**. Ele acha o meio com um ponteiro **lento/rápido**
> (o rápido anda de dois em dois; quando chega ao fim, o lento está no meio),
> divide o encadeamento em duas metades e as **intercala religando só `next`** —
> de forma estável e com O(1) de ponteiros extras. O quicksort, ao contrário,
> tira sua eficiência do acesso **aleatório**/indexação de arrays; numa lista
> sem índice, cada acesso por posição é O(n) e o particionamento fica caro. A
> lista encadeada é o terreno natural do merge sort.

Características desta implementação:

- opera sobre um **encadeamento simples de `Node`** (ligados só por `next`,
  terminado em `None`) — **não** sobre a `LinkedList` com sentinelas;
- **religa `next` in-place**, sem materializar um array durante a ordenação;
- ordena **decrescente** por `hits` ("mais acessados primeiro");
- é **estável** — empates preservam a ordem de entrada (graças ao `>=` no
  merge). Complexidade **O(n log n)**.

---

## Ordenação × ordem de recência (a sutileza)

Há uma armadilha aqui, e `sorted_by_hits()` a resolve sendo **não-destrutivo**.

O merge sort **religa `next`** dos nós que recebe. Se ele rodasse nos nós
**reais** da lista de recência, embaralharia os ponteiros e **destruiria** a
lista dupla — a política LRU pararia de funcionar.

Por isso `sorted_by_hits()` monta um **snapshot**: um encadeamento simples de
`Node`s **novos**, espelhando a recência atual, cada um apontando (por
referência, só para leitura) o mesmo `_Item`. O merge sort ordena **esse
snapshot** e a função devolve uma lista de tuplas `(key, value, hits)` na ordem
final.

> **Por quê não-destrutivo:** ordenar por frequência é **inspeção / leitura**,
> não é uma operação da política do cache. A ordem de **recência** fica
> intacta; a demo prova isso imprimindo a recência **antes e depois** do
> relatório — são idênticas.

---

## A demo passo a passo (`main.py`)

A cache é criada com `capacity = 3` (pequena de propósito, para o eviction
aparecer). A saída de `python main.py` tem quatro blocos:

1. **Inserções além da capacidade** — 4 chaves (`a b c d`) numa cache de 3:
   todas `MISS` (foram ao banco lento, ~1.30s). Ao inserir `d`, a cauda (`a`,
   o menos recente) é evictada.
2. **Acessos variados** — `b b c d` estão no cache → `HIT` (~0.00s) e sobem seus
   `hits`; `a` foi evictado → `MISS` de novo. Cada hit reordena a recência.
3. **Busca por chave via hash** — um `load` de `d` mostra o lookup O(1) servindo
   direto do cache.
4. **Relatório final por acessos** — imprime os itens do mais acessado ao menos
   (`chave=valor (N acessos)`), via merge sort, e mostra que a recência **antes
   e depois** do relatório é a mesma.

No `__str__` da cache, o estado é impresso da **frente** (mais recente) para a
**cauda**, cada nó como `chave=valor(hits=N)`. Para ver de verdade, rode e leia
a saída.

---

## Decisões e limites de escopo

- **Capacidade fixa:** a hash é dimensionada uma vez, sem `resize`/`rehash`.
- **`n_buckets = capacity`:** como a cache nunca passa de `capacity` pares, o
  fator de carga fica **≤ 1** e as cadeias dos buckets ficam curtas — é o que
  sustenta o O(1) médio da hash.
- **Fora de escopo:** resize/rehash, TTL
  (expiração por tempo), *thread-safety* e uma API HTTP na frente do cache.
