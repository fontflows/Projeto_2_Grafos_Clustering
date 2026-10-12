"""Todas as figuras do projeto. Cada função salva um PNG (slides) e um PDF (vetorial)."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgb

from dados import ATIVIDADES

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "figuras"

# Fonte única (Source Sans 3, licença OFL, arquivos em fonts/)
for arquivo in (RAIZ / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(arquivo)
plt.rcParams.update({
    "font.family": ["Source Sans 3", "DejaVu Sans"],
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "semibold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#8a8984", "axes.labelcolor": "#2b2b2b",
    "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
    "legend.frameon": False, "savefig.dpi": 300, "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})

# Mesma cor para a mesma atividade em todas as figuras:
# tons quentes = em movimento, tons frios = parado
CORES = ["#eb6834", "#e34948", "#eda100", "#2a78d6", "#1baf7a", "#4a3aa7"]
CINZA, TEXTO = "#b9b8b3", "#2b2b2b"


def salvar(fig, nome):
    PASTA.mkdir(exist_ok=True)
    fig.savefig(PASTA / f"{nome}.png")
    fig.savefig(PASTA / f"{nome}.pdf")
    plt.close(fig)


def mapa(ax, pos, cores, titulo):
    """Dispersão dos pontos no plano do t-SNE, sem eixos (as coordenadas não têm unidade)."""
    ax.scatter(pos[:, 0], pos[:, 1], c=cores, s=2, linewidths=0, rasterized=True)
    ax.set_title(titulo)
    ax.set_xticks([]), ax.set_yticks([])
    ax.grid(False)
    for lado in ax.spines.values():
        lado.set_visible(False)


def nomes_no_mapa(ax, pos, y):
    """Escreve o nome de cada atividade no centro dos seus pontos."""
    for a, nome in enumerate(ATIVIDADES):
        cx, cy = np.median(pos[y == a], axis=0)
        ax.text(cx, cy, nome, ha="center", va="center", fontsize=10, color=TEXTO, weight="semibold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.8))


def cores_grupos(grupos, y):
    """Cada grupo recebe a cor da atividade mais comum nele.
    Grupos com a mesma atividade majoritária ganham tons diferentes dessa cor."""
    maioria = pd.crosstab(grupos, y).idxmax(axis=1)
    cor = {}
    for a in range(6):
        membros = maioria.index[maioria == a]
        for i, g in enumerate(membros):
            t = i / max(len(membros) - 1, 1)      # 0 = mais escuro, 1 = mais claro
            base = np.array(to_rgb(CORES[a]))
            mistura = 0.65 + 0.7 * t              # < 1 escurece, > 1 clareia
            cor[g] = base * mistura if mistura <= 1 else base + (1 - base) * (mistura - 1)
    return np.array([cor[g] for g in grupos])


def dados_originais(pos, y):
    fig, ax = plt.subplots(figsize=(6.5, 6))
    mapa(ax, pos, np.array(CORES)[y], "10.299 janelas de sensor, coloridas pela atividade real")
    nomes_no_mapa(ax, pos, y)
    salvar(fig, "1_dados_originais")


def escolha_K(tab):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4))
    a1.plot(tab.K, tab.J / 1e6, "o-", color=CORES[3], lw=2, ms=6)
    a1.set(title="Método do cotovelo", xlabel="K", ylabel="J (milhões)")
    a2.plot(tab.K, tab.silhueta, "o-", color=CORES[3], lw=2, ms=6)
    a2.set(title="Silhueta", xlabel="K", ylabel="silhueta média")
    melhor = tab.loc[tab.silhueta.idxmax()]
    a2.annotate(f"máximo em K = {melhor.K:.0f}", (melhor.K, melhor.silhueta),
                xytext=(12, -4), textcoords="offset points", color=TEXTO, va="top")
    for ax in (a1, a2):
        ax.axvline(6, color=CINZA, ls="--", lw=1)
        ax.text(6.1, ax.get_ylim()[1], "6 atividades", va="top", color="#52514e", fontsize=10)
        ax.set_xticks(tab.K)
    fig.tight_layout()
    salvar(fig, "2_escolha_K")


def grafo(pos, y, adj, k):
    """Grafo k-NN desenhado nas posições do t-SNE, com um zoom em uma região."""
    pares = [(i, j) for i in range(len(adj)) for j in adj[i] if i < j]
    # Zoom na região de "Andando", onde aparecem várias ilhas pequenas
    centro = np.median(pos[y == 0], axis=0)
    r = 0.12 * np.ptp(pos[:, 0])
    dentro = np.all(np.abs(pos - centro) < r, axis=1)
    pares_zoom = [(i, j) for i, j in pares if dentro[i] and dentro[j]]   # só arestas internas ao quadro

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, lista, largura, alfa, tam in [(a1, pares, 0.2, 0.15, 2), (a2, pares_zoom, 0.6, 0.6, 12)]:
        segmentos = [(pos[i], pos[j]) for i, j in lista]
        ax.add_collection(LineCollection(segmentos, colors=CINZA, linewidths=largura, alpha=alfa, rasterized=True))
        ax.scatter(pos[:, 0], pos[:, 1], c=np.array(CORES)[y], s=tam, linewidths=0, zorder=2, rasterized=True)
        ax.set_xticks([]), ax.set_yticks([]), ax.grid(False)
        ax.set_aspect("equal")
    a1.set_title(f"Grafo k-NN com k = {k} ({len(pares):,} arestas)".replace(",", "."))
    a1.add_patch(plt.Rectangle(centro - r, 2 * r, 2 * r, fill=False, ec=TEXTO, lw=1))
    a2.set_xlim(centro[0] - r, centro[0] + r), a2.set_ylim(centro[1] - r, centro[1] + r)
    a2.set_title("Zoom em Andando: ilhas ligadas por dentro")
    for ax in (a1, a2):
        for lado in ax.spines.values():
            lado.set_visible(ax is a2)
    marcadores = [plt.Line2D([], [], ls="", marker="o", color=c, label=n) for c, n in zip(CORES, ATIVIDADES)]
    fig.legend(handles=marcadores, loc="lower center", ncol=6, bbox_to_anchor=(0.5, -0.02), columnspacing=1.2)
    salvar(fig, "3_grafo_knn")


def comparacao(pos, y, km, com, k):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2))
    mapa(axs[0], pos, np.array(CORES)[y], "Atividade real")
    nomes_no_mapa(axs[0], pos, y)
    mapa(axs[1], pos, cores_grupos(km, y), f"K-Means (K = {km.max() + 1})")
    mapa(axs[2], pos, cores_grupos(com, y), f"Comunidades Louvain (k = {k}, {com.max() + 1} comunidades)")
    fig.text(0.5, 0.01, "Cada grupo tem a cor da atividade mais comum nele; tons diferentes indicam grupos diferentes.",
             ha="center", color="#52514e")
    salvar(fig, "4_comparacao")


def composicao(km, com, y):
    """Tabela de contingência: quantas janelas de cada atividade há em cada grupo."""
    tabelas = [("K-Means", pd.crosstab(km, y)), ("Comunidades Louvain", pd.crosstab(com, y))]
    alturas = [len(t) for _, t in tabelas]
    fig, axs = plt.subplots(1, 2, figsize=(11, 0.32 * max(alturas) + 1.6),
                            gridspec_kw={"width_ratios": [1, 1]})
    for ax, (nome, tab) in zip(axs, tabelas):
        # Ordena os grupos pela atividade majoritária, para a "diagonal" aparecer
        tab = tab.loc[tab.idxmax(axis=1).sort_values(kind="stable").index]
        prop = tab.div(tab.sum(axis=1), axis=0)
        ax.imshow(prop, cmap="Blues", vmin=0, vmax=1, aspect="auto")
        for (i, j), v in np.ndenumerate(tab.to_numpy()):
            if v > 0:
                ax.text(j, i, v, ha="center", va="center", fontsize=8,
                        color="white" if prop.iat[i, j] > 0.6 else TEXTO)
        ax.set_xticks(range(6), ATIVIDADES, rotation=30, ha="right")
        ax.set_yticks(range(len(tab)), [f"{nome.split()[0][:3]}. {g + 1}" for g in range(len(tab))], fontsize=8)
        ax.set_title(f"{nome}: {len(tab)} grupos")
        ax.grid(False)
    fig.text(0.5, -0.02, "Número de janelas de cada atividade em cada grupo; cor = fração do grupo.",
             ha="center", color="#52514e")
    fig.tight_layout()
    salvar(fig, "5_composicao")


def experimento_k(exp, k_principal):
    """Médias e desvios-padrão (entre as sementes) das medidas em função de k."""
    g = exp.groupby("k")
    media, desvio, ks = g.mean(), g.std(), g.mean().index
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.6))
    axs = axs.ravel()
    paineis = [
        ("Grau médio (densidade)", [("grau_medio", "grau médio", CORES[3])]),
        ("Número de comunidades", [("comunidades", "comunidades", CORES[3])]),
        ("Modularidade Q", [("Q", "Q", CORES[3])]),
        ("Concordância (ARI)", [("ARI_real", "vs. atividade real", CORES[3]),
                                ("ARI_kmeans", "vs. K-Means", CORES[0])]),
    ]
    for ax, (titulo, linhas) in zip(axs, paineis):
        for col, rotulo, cor in linhas:
            ax.errorbar(ks, media[col], yerr=desvio[col], fmt="o-", color=cor, lw=2, ms=5, capsize=3, label=rotulo)
        ax.axvline(k_principal, color=CINZA, ls="--", lw=1)
        ax.set(title=titulo, xlabel="k (vizinhos, escala log)")
        ax.set_xscale("log")
        ax.set_xticks(ks, ks, fontsize=9)
        ax.minorticks_off()
    axs[3].legend(loc="lower right")
    fig.tight_layout()
    salvar(fig, "6_experimento_k")


def discordancia(pos, categoria):
    estilos = [("Os dois acertam", "#dcdbd5", 2), ("Só o K-Means erra", CORES[0], 4),
               ("Só as comunidades erram", CORES[3], 4), ("Os dois erram", TEXTO, 4)]
    fig, ax = plt.subplots(figsize=(7, 6.4))
    for nome, cor, tam in estilos:
        m = categoria == nome
        ax.scatter(pos[m, 0], pos[m, 1], c=cor, s=tam, linewidths=0, rasterized=True,
                   label=f"{nome} ({m.sum():,})".replace(",", "."))
    ax.set_title("Onde K-Means e comunidades erram")
    ax.set_xticks([]), ax.set_yticks([]), ax.grid(False)
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2, markerscale=3)
    salvar(fig, "7_discordancia")


def pessoas(tab, sujeito, y):
    """Fração dos 10 vizinhos mais próximos que vêm da mesma pessoa."""
    # Valor esperado ao acaso: chance de um vizinho sorteado da mesma atividade ser da mesma pessoa
    acaso = [np.sum((np.bincount(sujeito[y == a]) / np.sum(y == a)) ** 2) for a in range(6)]
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    barras = ax.barh(ATIVIDADES[::-1], tab.vizinhos_mesma_pessoa[::-1], color=CORES[::-1], height=0.6)
    ax.scatter(acaso[::-1], ATIVIDADES[::-1], marker="|", s=250, color=TEXTO, zorder=3)
    ax.text(acaso[0], 5.42, "ao acaso", ha="center", va="bottom", fontsize=9, color=TEXTO)
    ax.bar_label(barras, [f"{v:.0%}" for v in tab.vizinhos_mesma_pessoa[::-1]], padding=4, color=TEXTO)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(-0.5, 5.8)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.set_title("Dos 10 vizinhos mais próximos, quantos são da mesma pessoa?")
    ax.grid(axis="y", visible=False)
    salvar(fig, "8_pessoas")
