"""Carregamento de dados e modelo, previsão e gráficos usados pelo app."""
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression

from utils.preparacao import INDICADORES, ORDEM_PEDRAS

sns.set_theme(style='whitegrid')
CORES_DEFASAGEM = ['#4C9F70', '#F2B134', '#D1495B']
AZUL = '#2E86AB'


# ============================================================
# 1. DADOS E MODELO
# ============================================================

def carregar_dados(caminho='dados_limpos.csv'):
    return pd.read_csv(caminho)


def carregar_ranking(caminho='ranking_risco_2025.csv'):
    return pd.read_csv(caminho)


def carregar_modelo(caminho='modelo_risco.joblib'):
    """Devolve um dicionário com o modelo treinado e a lista de variáveis, na ordem do treino."""
    return joblib.load(caminho)


def faixa_risco(probabilidade):
    if probabilidade >= 0.6:
        return 'Alto'
    if probabilidade >= 0.35:
        return 'Médio'
    return 'Baixo'


def prever_risco(artefato, valores):
    """Recebe um dicionário {variável: valor} e devolve a probabilidade de defasagem no ano seguinte."""
    entrada = pd.DataFrame([valores])[artefato['variaveis']]
    return float(artefato['modelo'].predict_proba(entrada)[0, 1])


# ============================================================
# 2. GRÁFICOS
# ============================================================

def grafico_perfil_defasagem(df):
    perfil = (pd.crosstab(df['ANO'], df['NIVEL_DEFASAGEM'], normalize='index')
              [['Sem defasagem', 'Moderada', 'Severa']] * 100)
    fig, ax = plt.subplots(figsize=(7, 4))
    perfil.plot(kind='bar', stacked=True, color=CORES_DEFASAGEM, ax=ax)
    ax.set_title('Perfil de defasagem por ano (% dos alunos)')
    ax.set_xlabel('')
    ax.set_ylabel('%')
    ax.tick_params(axis='x', rotation=0)
    ax.legend(title='', bbox_to_anchor=(1, 1))
    fig.tight_layout()
    return fig


def grafico_ida_fase(df):
    tabela = df.pivot_table(values='IDA', index='FASE', columns='ANO', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(tabela, annot=True, fmt='.1f', cmap='Blues', ax=ax)
    ax.set_title('IDA médio por fase e ano')
    fig.tight_layout()
    return fig


def grafico_dispersao(df, x, y, titulo, diagonal=False):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.regplot(data=df, x=x, y=y, ax=ax, scatter_kws={'alpha': 0.2, 's': 10}, line_kws={'color': '#D1495B'})
    if diagonal:
        ax.plot([0, 10], [0, 10], '--', color='gray')
    correlacao = df[[x, y]].corr().iloc[0, 1]
    ax.set_title(f'{titulo} (correlação = {correlacao:.2f})')
    fig.tight_layout()
    return fig


def grafico_ips_queda(df):
    """% de alunos com queda de mais de 1 ponto no ano seguinte, por quartil de IPS."""
    linhas = []
    for indicador in ['IDA', 'IEG']:
        seguinte = (df[['RA', 'ANO', indicador]].assign(ANO=lambda d: d['ANO'] - 1)
                    .rename(columns={indicador: 'PROX'}))
        pares = df.merge(seguinte, on=['RA', 'ANO']).dropna(subset=['IPS', indicador, 'PROX'])
        pares['QUARTIL_IPS'] = pd.qcut(pares['IPS'], 4, labels=['1º (menor)', '2º', '3º', '4º (maior)'])
        queda = pares.groupby('QUARTIL_IPS', observed=True).apply(
            lambda g: ((g['PROX'] - g[indicador]) < -1).mean() * 100)
        linhas.append(queda.rename(indicador))
    tabela = pd.concat(linhas, axis=1)
    fig, ax = plt.subplots(figsize=(7, 4))
    tabela.plot(kind='bar', ax=ax, color=[AZUL, '#F2B134'])
    ax.set_title('% com queda de mais de 1 ponto no ano seguinte, por quartil de IPS')
    ax.set_xlabel('Quartil de IPS no ano atual')
    ax.set_ylabel('%')
    ax.tick_params(axis='x', rotation=0)
    fig.tight_layout()
    return fig


def grafico_ipp_defasagem(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df.dropna(subset=['IPP']), x='NIVEL_DEFASAGEM', y='IPP',
                order=['Sem defasagem', 'Moderada', 'Severa'], hue='NIVEL_DEFASAGEM',
                hue_order=['Sem defasagem', 'Moderada', 'Severa'], palette=CORES_DEFASAGEM, legend=False, ax=ax)
    ax.set_title('IPP por nível de defasagem')
    ax.set_xlabel('')
    fig.tight_layout()
    return fig


def grafico_corr_ipv(df):
    correlacao = df[INDICADORES].corr()['IPV'].drop('IPV').sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    correlacao.plot(kind='barh', color=AZUL, ax=ax)
    ax.set_title('Correlação de cada indicador com o IPV')
    fig.tight_layout()
    return fig


def pesos_inde(df):
    """Pesos de cada indicador no INDE, estimados por regressão (o INDE é uma média ponderada fixa)."""
    dados = df.dropna(subset=['INDE'] + INDICADORES)
    regressao = LinearRegression().fit(dados[INDICADORES], dados['INDE'])
    return pd.Series(regressao.coef_, index=INDICADORES).round(2).sort_values(ascending=False)


def grafico_pesos_inde(df):
    pesos = pesos_inde(df).sort_values() * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    pesos.plot(kind='barh', color=AZUL, ax=ax)
    ax.set_title('Peso de cada indicador no INDE (%)')
    fig.tight_layout()
    return fig


def grafico_pedras(df):
    pedras = pd.crosstab(df['ANO'], df['PEDRA'], normalize='index')[ORDEM_PEDRAS] * 100
    fig, ax = plt.subplots(figsize=(7, 4))
    pedras.plot(kind='bar', stacked=True, color=['#B0B7C3', '#F2B134', '#8E5BB5', '#2E86AB'], ax=ax)
    ax.set_title('Distribuição das pedras por ano (%)')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=0)
    ax.legend(title='', bbox_to_anchor=(1, 1))
    fig.tight_layout()
    return fig


def grafico_defasagem_fase_idade(df):
    fig, eixos = plt.subplots(1, 2, figsize=(11, 4))
    df.groupby('FASE')['DEFASADO'].mean().mul(100).plot(kind='bar', color='#D1495B', ax=eixos[0])
    eixos[0].set_title('% de alunos defasados por fase')
    eixos[0].set_ylabel('%')
    eixos[0].tick_params(axis='x', rotation=0)
    faixas = pd.cut(df['IDADE'], [6, 9, 11, 13, 15, 17, 30],
                    labels=['7-9', '10-11', '12-13', '14-15', '16-17', '18+'])
    df.groupby(faixas, observed=True)['DEFASADO'].mean().mul(100).plot(kind='bar', color='#D1495B', ax=eixos[1])
    eixos[1].set_title('% de alunos defasados por idade')
    eixos[1].set_xlabel('Idade')
    eixos[1].tick_params(axis='x', rotation=0)
    fig.tight_layout()
    return fig
