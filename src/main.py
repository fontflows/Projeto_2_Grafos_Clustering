"""Roda o projeto inteiro: python src/main.py

Gera as tabelas em resultados/ e as figuras em figuras/.
"""

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.metrics import normalized_mutual_info_score as nmi
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

import dados
import figuras
from grafo import grafo_knn, num_arestas
from louvain import louvain, modularidade

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "resultados"

K_KMEANS = 6                            # número de clusters do K-Means (6 atividades)
VALORES_K = [3, 5, 10, 15, 20, 30, 50, 100, 200, 400]  # vizinhos do grafo k-NN (enunciado + extras)
K_PRINCIPAL = 100                       # k usado nas comparações principais (melhor ARI/NMI)
SEMENTES = range(5)                     # repetições do Louvain para as barras de erro


def escolher_K(Z):
    """Método do cotovelo (J) e silhueta para K = 2..10."""
    linhas = []
    for K in range(2, 11):
        km = KMeans(K, n_init=10, random_state=0).fit(Z)
        linhas.append({"K": K, "J": km.inertia_, "silhueta": silhouette_score(Z, km.labels_)})
        print(f"  K={K}: J={km.inertia_:.0f}, silhueta={linhas[-1]['silhueta']:.3f}")
    return pd.DataFrame(linhas)


def experimento_k(Z, y, km):
    """Para cada k, constrói o grafo e roda o Louvain com várias sementes."""
    linhas = []
    for k in VALORES_K:
        adj, sigma = grafo_knn(Z, k)
        m, n = num_arestas(adj), len(adj)
        for s in SEMENTES:
            com = louvain(adj, semente=s)
            linhas.append({
                "k": k, "semente": s, "arestas": m, "grau_medio": 2 * m / n,
                "densidade": 2 * m / (n * (n - 1)), "sigma": sigma,
                "comunidades": com.max() + 1, "Q": modularidade(adj, com),
                "ARI_real": ari(y, com), "NMI_real": nmi(y, com),
                "ARI_kmeans": ari(km, com), "NMI_kmeans": nmi(km, com),
            })
        print(f"  k={k}: {m} arestas, {linhas[-1]['comunidades']} comunidades (semente 9)")
    return pd.DataFrame(linhas)


def validar(Z):
    """Compara nosso Louvain com o da biblioteca networkx."""
    linhas = []
    # Grafo de teste clássico (clube de karatê de Zachary), sem pesos
    G = nx.karate_club_graph()
    adj = [{j: 1.0 for j in G[i]} for i in G]
    nosso = louvain(adj)
    biblioteca = nx.community.louvain_communities(G, weight=None, seed=0)
    linhas.append({
        "grafo": "karate", "C_nosso": nosso.max() + 1, "C_networkx": len(biblioteca),
        "Q_nosso": modularidade(adj, nosso),
        "Q_nosso_pelo_networkx": nx.community.modularity(G, particao(nosso), weight=None),
        "Q_networkx": nx.community.modularity(G, biblioteca, weight=None),
        "ARI_entre_os_dois": ari(nosso, rotulos(biblioteca, len(adj))),
    })
    # Grafos k-NN do nosso dataset (valores de k da tabela do enunciado)
    for k in [3, 5, 10, 15, 20]:
        adj, _ = grafo_knn(Z, k)
        G = nx.Graph()
        G.add_weighted_edges_from((i, j, w) for i in range(len(adj)) for j, w in adj[i].items() if i < j)
        nosso = louvain(adj)
        biblioteca = nx.community.louvain_communities(G, weight="weight", seed=0)
        linhas.append({
            "grafo": f"kNN k={k}", "C_nosso": nosso.max() + 1, "C_networkx": len(biblioteca),
            "Q_nosso": modularidade(adj, nosso),
            "Q_nosso_pelo_networkx": nx.community.modularity(G, particao(nosso)),
            "Q_networkx": nx.community.modularity(G, biblioteca),
            "ARI_entre_os_dois": ari(nosso, rotulos(biblioteca, len(adj))),
        })
    return pd.DataFrame(linhas)


def particao(rot):
    """Vetor de rótulos -> lista de conjuntos (formato do networkx)."""
    return [set(np.flatnonzero(rot == c)) for c in np.unique(rot)]


def rotulos(conjuntos, n):
    """Lista de conjuntos -> vetor de rótulos."""
    rot = np.zeros(n, dtype=int)
    for c, nos in enumerate(conjuntos):
        rot[list(nos)] = c
    return rot


def acerta(grupos, y):
    """Cada grupo 'vota' na atividade mais comum entre seus membros.
    Um ponto é acerto se a atividade do seu grupo é a sua atividade real."""
    maioria = pd.crosstab(grupos, y).idxmax(axis=1)
    return maioria[grupos].to_numpy() == y


def main():
    PASTA.mkdir(exist_ok=True)
    X, y, sujeito = dados.carregar()
    Z = dados.padronizar(X)
    print(f"Dados: {Z.shape[0]} janelas, {Z.shape[1]} atributos, {len(set(sujeito))} voluntários")

    print("Projeção 2D com t-SNE (só para visualização)...")
    pos = TSNE(random_state=0).fit_transform(PCA(50, random_state=0).fit_transform(Z))

    print("Escolha de K para o K-Means...")
    tab_K = escolher_K(Z)
    tab_K.to_csv(PASTA / "escolha_K.csv", index=False)
    km = KMeans(K_KMEANS, n_init=10, random_state=0).fit_predict(Z)
    km2 = KMeans(2, n_init=10, random_state=0).fit_predict(Z)
    movimento = (y <= 2).astype(int)   # 1 = andando ou escada, 0 = parado
    print(f"  K=2 contra 'em movimento x parado': ARI = {ari(movimento, km2):.3f}")

    print("Experimento com k (grafo k-NN + Louvain)...")
    exp = experimento_k(Z, y, km)
    exp.to_csv(PASTA / "experimento_k_todas_sementes.csv", index=False)
    resumo = exp.drop(columns="semente").groupby("k").agg(["mean", "std"])
    resumo.columns = [f"{a}_{b}" for a, b in resumo.columns]
    resumo.round(4).to_csv(PASTA / "experimento_k.csv")
    print(resumo[["comunidades_mean", "Q_mean", "ARI_real_mean", "NMI_real_mean"]].round(3))

    print("Validação contra o networkx...")
    val = validar(Z)
    val.round(4).to_csv(PASTA / "validacao_louvain.csv", index=False)
    print(val.round(3).to_string(index=False))

    # Partição principal de comunidades (k = K_PRINCIPAL, semente 0)
    adj, _ = grafo_knn(Z, K_PRINCIPAL)
    com = louvain(adj, semente=0)

    # Comparações da seção 11 do enunciado
    comp = pd.DataFrame([
        {"comparacao": "K-Means x Atividade real", "ARI": ari(y, km), "NMI": nmi(y, km)},
        {"comparacao": "Comunidades x Atividade real", "ARI": ari(y, com), "NMI": nmi(y, com)},
        {"comparacao": "K-Means x Comunidades", "ARI": ari(km, com), "NMI": nmi(km, com)},
    ])
    comp.round(4).to_csv(PASTA / "comparacoes.csv", index=False)
    silh = pd.DataFrame([
        {"particao": nome, "grupos": len(np.unique(r)), "silhueta": silhouette_score(Z, r)}
        for nome, r in [("Atividade real", y), ("K-Means", km), ("Comunidades", com)]
    ])
    silh.round(4).to_csv(PASTA / "silhuetas.csv", index=False)
    print(comp.round(3).to_string(index=False))
    print(silh.round(3).to_string(index=False))

    # Composição: quantas janelas de cada atividade há em cada grupo
    pd.crosstab(km, y).set_axis(dados.ATIVIDADES, axis=1).to_csv(PASTA / "composicao_kmeans.csv")
    pd.crosstab(com, y).set_axis(dados.ATIVIDADES, axis=1).to_csv(PASTA / "composicao_comunidades.csv")

    # Onde os métodos erram: proporção dos 10 vizinhos com atividade diferente
    _, viz = NearestNeighbors(n_neighbors=11).fit(Z).kneighbors(Z)
    viz = viz[:, 1:]
    mistura = (y[viz] != y[:, None]).mean(axis=1)
    ok_km, ok_com = acerta(km, y), acerta(com, y)
    categoria = np.select(
        [ok_km & ok_com, ~ok_km & ok_com, ok_km & ~ok_com],
        ["Os dois acertam", "Só o K-Means erra", "Só as comunidades erram"],
        default="Os dois erram")
    disc = pd.DataFrame({"categoria": categoria, "mistura": mistura, "atividade": np.array(dados.ATIVIDADES)[y]})
    resumo_disc = disc.groupby("categoria").agg(janelas=("mistura", "size"), mistura_media=("mistura", "mean"))
    resumo_disc.round(4).to_csv(PASTA / "discordancia.csv")
    pd.crosstab(disc.categoria, disc.atividade).to_csv(PASTA / "discordancia_por_atividade.csv")
    print(resumo_disc.round(3))

    # Achado extra: os vizinhos de uma janela são da mesma pessoa?
    mesma_pessoa = sujeito[viz] == sujeito[:, None]
    # As janelas se sobrepõem 50% no tempo. Para conferir que o efeito não vem só disso,
    # repetimos a conta ignorando vizinhos a até 5 linhas de distância no arquivo (janelas vizinhas no tempo)
    longe = np.abs(viz - np.arange(len(viz))[:, None]) > 5
    # Com k pequeno o Louvain separa pessoas: comparamos comunidades (k = 10) com voluntários
    adj10, _ = grafo_knn(Z, 10)
    com10 = louvain(adj10, semente=0)
    pessoas = pd.DataFrame({
        "atividade": dados.ATIVIDADES,
        "vizinhos_mesma_pessoa": [mesma_pessoa[y == a].mean() for a in range(6)],
        "vizinhos_mesma_pessoa_longe_no_tempo": [mesma_pessoa[y == a][longe[y == a]].mean() for a in range(6)],
        "vizinhos_mesma_atividade": [1 - mistura[y == a].mean() for a in range(6)],
        "NMI_comunidade_k10_pessoa": [nmi(sujeito[y == a], com10[y == a]) for a in range(6)],
    })
    pessoas.round(4).to_csv(PASTA / "pessoas.csv", index=False)
    print(pessoas.round(3).to_string(index=False))

    print("Gerando figuras...")
    figuras.dados_originais(pos, y)
    figuras.escolha_K(tab_K)
    figuras.grafo(pos, y, adj10, k=10)
    figuras.comparacao(pos, y, km, com, K_PRINCIPAL)
    figuras.composicao(km, com, y)
    figuras.experimento_k(exp, K_PRINCIPAL)
    figuras.discordancia(pos, categoria)
    figuras.pessoas(pessoas, sujeito, y)
    print("Pronto.")


if __name__ == "__main__":
    main()
