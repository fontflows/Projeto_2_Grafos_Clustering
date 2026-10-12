"""Construção do grafo k-NN com pesos gaussianos."""

import numpy as np
from sklearn.neighbors import NearestNeighbors


def grafo_knn(X, k):
    """Liga cada ponto aos seus k vizinhos mais próximos (distância euclidiana).

    O grafo é simétrico: i e j ficam ligados se j está entre os k vizinhos de i
    OU i está entre os k vizinhos de j. Peso gaussiano:
        w_ij = exp(-d_ij^2 / (2 sigma^2)),
    com sigma = mediana das distâncias de todos os pares de vizinhos.

    Retorna adj (lista de dicionários, o formato usado em louvain.py) e sigma.
    """
    # k + 1 porque o vizinho mais próximo de cada ponto é ele mesmo
    dist, idx = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X)
    dist, idx = dist[:, 1:], idx[:, 1:]
    sigma = np.median(dist)
    peso = np.exp(-dist**2 / (2 * sigma**2))

    adj = [{} for _ in range(len(X))]
    for i in range(len(X)):
        for j, w in zip(idx[i].tolist(), peso[i].tolist()):
            adj[i][j] = w
            adj[j][i] = w
    return adj, sigma


def num_arestas(adj):
    return sum(len(v) for v in adj) // 2
