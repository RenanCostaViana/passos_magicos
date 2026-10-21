"""Leitura e padronização da base PEDE (2022 a 2024) da Passos Mágicos.

Usado pelo notebook e pelo app, para que os dois tratem os dados da mesma forma.
"""
import re

import numpy as np
import pandas as pd

INDICADORES = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']
ORDEM_PEDRAS = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']

# Nomes das colunas que mudam de um ano para outro
COLUNAS_POR_ANO = {
    2022: {'inde': 'INDE 22', 'pedra': 'Pedra 22', 'defasagem': 'Defas'},
    2023: {'inde': 'INDE 2023', 'pedra': 'Pedra 2023', 'defasagem': 'Defasagem'},
    2024: {'inde': 'INDE 2024', 'pedra': 'Pedra 2024', 'defasagem': 'Defasagem'},
}


def fase_numerica(valor):
    """'ALFA' -> 0; 'FASE 3', '3' ou '3B' (turma) -> 3."""
    texto = str(valor).upper().strip()
    if texto.startswith('ALFA'):
        return 0
    numero = re.search(r'\d+', texto)
    return int(numero.group()) if numero else np.nan


def ano_nascimento(aba, ano):
    """2022 traz o ano de nascimento; 2023 e 2024 trazem a data completa, em formatos mistos."""
    if ano == 2022:
        return pd.to_numeric(aba['Ano nasc'], errors='coerce')
    datas = pd.to_datetime(aba['Data de Nasc'].astype(str), errors='coerce', format='mixed')
    return datas.dt.year


def classifica_defasagem(defasagem):
    """Defasagem negativa = aluno atrás da fase ideal; zero ou positiva = adequado."""
    if pd.isna(defasagem):
        return np.nan
    if defasagem <= -3:
        return 'Severa'
    if defasagem < 0:
        return 'Moderada'
    return 'Sem defasagem'


def carrega_base(caminho):
    """Lê as três abas, padroniza nomes e tipos e devolve uma linha por aluno e ano."""
    partes = []
    for ano, nomes in COLUNAS_POR_ANO.items():
        aba = pd.read_excel(caminho, sheet_name=f'PEDE{ano}')
        df = pd.DataFrame({
            'RA': aba['RA'],
            'ANO': ano,
            'FASE': aba['Fase'].map(fase_numerica),
            'IDADE': ano - ano_nascimento(aba, ano),
            'GENERO': aba['Gênero'].replace({'Menina': 'Feminino', 'Menino': 'Masculino'}),
            'PEDRA': aba[nomes['pedra']].replace({'Agata': 'Ágata', 'INCLUIR': np.nan}),
            'INDE': pd.to_numeric(aba[nomes['inde']], errors='coerce'),
            'DEFASAGEM': pd.to_numeric(aba[nomes['defasagem']], errors='coerce'),
        })
        for indicador in INDICADORES:
            # IPP não existe em 2022; textos como 'INCLUIR' viram nulo
            df[indicador] = pd.to_numeric(aba[indicador], errors='coerce') if indicador in aba else np.nan
        partes.append(df)

    base = pd.concat(partes, ignore_index=True)
    base['NIVEL_DEFASAGEM'] = base['DEFASAGEM'].map(classifica_defasagem)
    base['DEFASADO'] = (base['DEFASAGEM'] < 0).astype('Int64').where(base['DEFASAGEM'].notna())
    return base


def pares_ano_seguinte(base):
    """Junta cada aluno com a situação dele no ano seguinte (2022->2023 e 2023->2024)."""
    seguinte = (base[['RA', 'ANO', 'DEFASAGEM']]
                .assign(ANO=lambda d: d['ANO'] - 1)
                .rename(columns={'DEFASAGEM': 'DEFASAGEM_PROX'}))
    pares = base.merge(seguinte, on=['RA', 'ANO']).dropna(subset=['DEFASAGEM', 'DEFASAGEM_PROX'])
    pares['DEFASADO_PROX'] = (pares['DEFASAGEM_PROX'] < 0).astype(int)
    return pares
