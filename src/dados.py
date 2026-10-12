"""Download e leitura do dataset Human Activity Recognition Using Smartphones (UCI)."""

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

URL = "https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip"
ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "har.zip"

# Nomes das 6 atividades em português, na ordem dos rótulos 1..6 do dataset
ATIVIDADES = ["Andando", "Subindo escada", "Descendo escada", "Sentado", "Em pé", "Deitado"]


def baixar():
    """Baixa o zip do UCI se ele ainda não estiver na pasta dados/."""
    if not ARQUIVO.exists():
        ARQUIVO.parent.mkdir(exist_ok=True)
        print("Baixando o dataset do UCI (cerca de 60 MB)...")
        urllib.request.urlretrieve(URL, ARQUIVO)


def carregar():
    """Retorna X (n x 561), y (atividade 0..5) e sujeito (voluntário 1..30).

    O dataset vem dividido em treino e teste. Como aqui não treinamos nenhum
    classificador, juntamos as duas partes em um único conjunto.
    """
    baixar()
    # O zip do UCI tem outro zip dentro, com os arquivos de texto
    with zipfile.ZipFile(ARQUIVO) as externo:
        interno = zipfile.ZipFile(io.BytesIO(externo.read("UCI HAR Dataset.zip")))

    def ler(nome):
        return np.loadtxt(io.StringIO(interno.read(f"UCI HAR Dataset/{nome}").decode()))

    X = np.vstack([ler("train/X_train.txt"), ler("test/X_test.txt")])
    y = np.concatenate([ler("train/y_train.txt"), ler("test/y_test.txt")]).astype(int) - 1
    sujeito = np.concatenate([ler("train/subject_train.txt"), ler("test/subject_test.txt")]).astype(int)
    return X, y, sujeito


def padronizar(X):
    """Padronização z = (x - média) / desvio, coluna por coluna."""
    return (X - X.mean(axis=0)) / X.std(axis=0)
