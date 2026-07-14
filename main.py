# main.py — demonstração do LRU Cache (T07)
#
# Roteiro que conta a história completa da cache: inserção além da capacidade
# (com eviction do menos recente), acessos que renovam a recência e contam hits,
# busca por chave via hash (requisito de busca) e relatório final ordenado por
# acessos via merge sort (requisito de ordenação). Cada bloco imprime o estado
# da recência para a saída "contar a história" de forma legível.

import time
from lru_cache.lru_cache import LRUCache


def slow_source(key):
    """Simula uma consulta cara a um 'banco lento': dorme e devolve um valor
    derivado da chave. É o que o cache existe para evitar repetir."""
    time.sleep(1.3)
    return key.upper()


def load(cache, key):
    """Busca no cache; no miss consulta o banco lento e popula o cache. Imprime
    HIT/MISS e o tempo gasto — o hit deve ser ~instantâneo, o miss ~1.3s."""
    start = time.time()
    value = cache.get(key)
    if value is None:                      # miss: paga o banco lento
        value = slow_source(key)
        cache.put(key, value)
        tag = "MISS"
    else:
        tag = "HIT "
    elapsed = time.time() - start
    print(f"  {tag} {key!r} -> {value!r} ({elapsed:.2f}s)")
    return value


def main():
    """Executa o roteiro da demonstração, bloco a bloco."""
    cache = LRUCache(3)  # capacidade pequena para o eviction aparecer

    print("=== 1) Inserções além da capacidade ===")
    # 4 chaves numa cache de 3: todas MISS; ao inserir 'd' a cauda ('a') é evictada.
    for key in ("a", "b", "c", "d"):
        load(cache, key)
    print(f"  estado: {cache}")

    print("=== 2) Acessos variados (HIT rápido, hits sobem, recência reordena) ===")
    # 'b','b','c','d' ainda estão no cache -> HIT; 'a' foi evictado -> MISS e re-evicta.
    for key in ("b", "b", "c", "d", "a"):
        load(cache, key)
    print(f"  estado: {cache}")

    print("=== 3) Busca por chave via hash (requisito de busca) ===")
    # Lookup O(1) da hash servindo direto do cache: chave presente vira HIT.
    load(cache, "d")
    print(f"  estado: {cache}")

    print("=== 4) Relatório final por acessos (requisito de ordenação) ===")
    before = str(cache)  # ordem de recência antes do relatório
    print("Relatório — mais acessados primeiro (merge sort por hits):")
    for key, value, hits in cache.sorted_by_hits():
        print(f"  {key}={value} ({hits} acessos)")
    # O relatório é inspeção: não reordena o cache. A recência continua igual.
    print(f"  recência antes:  {before}")
    print(f"  recência depois: {cache}")


main()
