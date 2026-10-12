"""Implementação própria do algoritmo de Louvain (Blondel et al., 2008).

O grafo é uma lista de dicionários: adj[i] = {j: peso da aresta i-j}.
A lista é simétrica (adj[i][j] == adj[j][i]). Um laço adj[i][i] guarda o peso
interno de um nó agregado e entra uma vez no grau, como A_ii na fórmula de Q.

O algoritmo repete duas fases até a partição parar de mudar:
  1. cada nó vai para a comunidade vizinha que mais aumenta a modularidade;
  2. cada comunidade vira um único nó de um grafo menor (agregação).
"""

import numpy as np


def modularidade(adj, rotulos):
    """Q = soma sobre as comunidades c de [ dentro_c / 2m - (grau_c / 2m)^2 ]."""
    dentro, grau = {}, {}
    for i, vizinhos in enumerate(adj):
        c = rotulos[i]
        for j, w in vizinhos.items():
            grau[c] = grau.get(c, 0) + w
            if rotulos[j] == c:
                dentro[c] = dentro.get(c, 0) + w
    m2 = sum(grau.values())
    return sum(dentro.get(c, 0) / m2 - (grau[c] / m2) ** 2 for c in grau)


def mover_nos(adj, rng):
    """Fase 1: move nós entre comunidades enquanto a modularidade aumentar."""
    n = len(adj)
    grau = [sum(vizinhos.values()) for vizinhos in adj]
    m2 = sum(grau)
    com = list(range(n))   # cada nó começa sozinho
    tot = grau[:]          # tot[c] = soma dos graus dos nós da comunidade c

    mudou = True
    while mudou:
        mudou = False
        for i in rng.permutation(n).tolist():
            # Peso das arestas de i para cada comunidade vizinha
            ligacao = {}
            for j, w in adj[i].items():
                if j != i:
                    ligacao[com[j]] = ligacao.get(com[j], 0) + w

            # Tira i da sua comunidade e escolhe para onde ele vai.
            # Ganho de pôr i na comunidade c (a menos de uma constante):
            #   ligacao[c] - tot[c] * grau[i] / 2m
            atual = com[i]
            tot[atual] -= grau[i]
            melhor = atual
            melhor_ganho = ligacao.get(atual, 0) - tot[atual] * grau[i] / m2
            for c, w in ligacao.items():
                ganho = w - tot[c] * grau[i] / m2
                if ganho > melhor_ganho + 1e-12:
                    melhor, melhor_ganho = c, ganho
            tot[melhor] += grau[i]

            if melhor != atual:
                com[i] = melhor
                mudou = True

    # Renumera as comunidades como 0, 1, 2, ...
    _, com = np.unique(com, return_inverse=True)
    return com


def agregar(adj, com):
    """Fase 2: cada comunidade vira um nó; pesos entre comunidades são somados."""
    novo = [{} for _ in range(com.max() + 1)]
    for i, vizinhos in enumerate(adj):
        for j, w in vizinhos.items():
            a, b = com[i], com[j]
            novo[a][b] = novo[a].get(b, 0) + w
    return novo


def louvain(adj, semente=0):
    """Retorna um vetor com a comunidade de cada nó do grafo original."""
    rng = np.random.default_rng(semente)
    rotulos = np.arange(len(adj))
    while True:
        com = mover_nos(adj, rng)
        if com.max() + 1 == len(adj):   # nenhum nó mudou: fim
            return rotulos
        rotulos = com[rotulos]          # atualiza a comunidade dos nós originais
        adj = agregar(adj, com)
