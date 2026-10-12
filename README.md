# Projeto 2: Clustering de Dados e Detecção de Comunidades em Grafos

Francisco Eduardo Fontenele (15452569) e Vinicius Botte (15522900)

Comparamos duas formas de agrupar os mesmos dados de sensores de celular
(dataset *Human Activity Recognition Using Smartphones*, UCI):

1. **K-Means** sobre os 561 atributos padronizados;
2. **grafo k-NN** com pesos gaussianos + **Louvain implementado por nós** (`src/louvain.py`).

As partições são comparadas entre si e com as atividades reais (ARI, NMI, silhueta),
e o efeito do número de vizinhos k é medido com 10 sementes.

## Como rodar

Requer Python 3.10 ou mais novo.

```
python -m venv .venv
.venv\Scripts\activate          (no Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python src/main.py
```

O script baixa o dataset (cerca de 60 MB) na primeira execução e leva uns 6 minutos.
Tudo usa sementes fixas, então os resultados são sempre os mesmos.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `src/dados.py` | baixa e lê o dataset, padroniza os atributos |
| `src/grafo.py` | monta o grafo k-NN com pesos gaussianos |
| `src/louvain.py` | **nossa implementação do Louvain** e o cálculo da modularidade |
| `src/main.py` | roda todos os experimentos e salva tabelas e figuras |
| `src/figuras.py` | desenha as figuras |
| `resultados/` | tabelas em CSV |
| `figuras/` | figuras em PNG e PDF |
| `apresentacao/` | slides em PowerPoint (com notas) e PDF, e `roteiro.md` com a fala de cada slide |
| `fonts/` | fonte Source Sans 3 (licença SIL OFL), usada nas figuras |

## Dados

Reyes-Ortiz, J., Anguita, D., Ghio, A., Oneto, L. e Parra, X. (2013).
*Human Activity Recognition Using Smartphones*. UCI Machine Learning Repository.
https://doi.org/10.24432/C54S4K. Licença CC BY 4.0.
