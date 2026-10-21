import pandas as pd
import streamlit as st

from utils.funcoes import (
    carregar_dados, carregar_modelo, carregar_ranking, faixa_risco, prever_risco,
    grafico_perfil_defasagem, grafico_ida_fase, grafico_dispersao, grafico_ips_queda,
    grafico_ipp_defasagem, grafico_corr_ipv, grafico_pesos_inde, grafico_pedras,
    grafico_defasagem_fase_idade,
)

st.set_page_config(page_title='Passos Mágicos – Risco de Defasagem', page_icon='📊', layout='wide')


@st.cache_data
def dados():
    return carregar_dados(), carregar_ranking()


@st.cache_resource
def modelo():
    return carregar_modelo()


df, ranking = dados()
artefato = modelo()

st.title('📊 Passos Mágicos — Indicadores e Alerta de Risco de Defasagem')
st.caption('Base PEDE 2022 a 2024. Defasagem negativa = aluno atrás da fase ideal para a sua idade escolar.')

aba_geral, aba_analises, aba_simulador, aba_ranking = st.tabs(
    ['📈 Visão geral', '🔍 Análises', '🧮 Simulador de risco', '🚨 Alunos em risco em 2025'])

# ============================================================
# 1. VISÃO GERAL
# ============================================================
with aba_geral:
    alunos_2024 = df[df['ANO'] == 2024]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Alunos em 2024', f"{len(alunos_2024):,}".replace(',', '.'))
    c2.metric('Sem defasagem em 2024', f"{(alunos_2024['DEFASAGEM'] >= 0).mean():.0%}",
              f"{(alunos_2024['DEFASAGEM'] >= 0).mean() - (df[df['ANO'] == 2022]['DEFASAGEM'] >= 0).mean():+.0%} desde 2022")
    c3.metric('INDE médio em 2024', f"{alunos_2024['INDE'].mean():.2f}")
    c4.metric('Alunos com risco alto para 2025', f"{(ranking['FAIXA_RISCO'] == 'Alto').sum()}")

    col1, col2 = st.columns(2)
    col1.pyplot(grafico_perfil_defasagem(df))
    col2.pyplot(grafico_pedras(df))

# ============================================================
# 2. ANÁLISES
# ============================================================
ANALISES = {
    '1. Perfil de defasagem (IAN)': (
        lambda: grafico_perfil_defasagem(df),
        'A parcela sem defasagem subiu de cerca de 30% (2022) para 54% (2024), e a defasagem severa '
        'ficou próxima de zero. Quase metade dos alunos ainda tem defasagem moderada.'),
    '2. Desempenho acadêmico (IDA)': (
        lambda: grafico_ida_fase(df),
        'O IDA subiu em 2023 e recuou em 2024, sem tendência clara. A fase 3 tem o menor desempenho nos três anos.'),
    '3. Engajamento x desempenho e ponto de virada': (
        lambda: grafico_dispersao(df, 'IEG', 'IDA', 'Engajamento x desempenho'),
        'Correlação moderada (cerca de 0,55) do engajamento com o IDA e com o IPV: alunos mais engajados '
        'tendem a ir melhor, mas a relação não é determinística.'),
    '4. Autoavaliação x desempenho': (
        lambda: grafico_dispersao(df, 'IDA', 'IAA', 'Autoavaliação x desempenho', diagonal=True),
        'A autoavaliação quase não acompanha o desempenho (correlação de cerca de 0,1), e os alunos se avaliam, '
        'em média, 1,5 ponto acima do IDA. Serve mais como ponto de conversa do que como sinal de desempenho.'),
    '5. Aspectos psicossociais (IPS) antes de quedas': (
        lambda: grafico_ips_queda(df),
        'Alunos com IPS mais baixo têm quedas de desempenho e engajamento no ano seguinte com mais frequência. '
        'O sinal é real, mas fraco: ajuda a priorizar acompanhamento, sem prever sozinho quem vai cair.'),
    '6. Avaliação psicopedagógica (IPP) x defasagem': (
        lambda: grafico_ipp_defasagem(df),
        'O IPP é só um pouco menor entre os defasados, e a correlação com o IAN é fraca (cerca de 0,1). '
        'A avaliação psicopedagógica capta algo diferente do atraso escolar.'),
    '7. O que influencia o ponto de virada (IPV)': (
        lambda: grafico_corr_ipv(df),
        'O IPV anda junto com IPP, IDA e IEG. Autoavaliação, aspectos psicossociais e adequação de nível '
        'quase não se relacionam com ele.'),
    '8. Composição do INDE': (
        lambda: grafico_pesos_inde(df),
        'O INDE é uma média ponderada fixa: IDA, IEG e IPV pesam 20% cada; IAN, IAA, IPS e IPP, 10% cada. '
        'Um ponto a mais em desempenho, engajamento ou ponto de virada vale o dobro no INDE.'),
    '10. Efetividade do programa (pedras)': (
        lambda: grafico_pedras(df),
        'A distribuição de pedras melhorou (Topázio passou de 15% para 31%), mas INDE, IEG e IPV não mostram '
        'melhora contínua. O ganho mais claro do período é a redução da defasagem.'),
    '11. Onde a defasagem se concentra': (
        lambda: grafico_defasagem_fase_idade(df),
        'A defasagem é maior na fase 1 e entre alunos de 16 e 17 anos: na entrada no programa e no fim do ensino '
        'médio, dois momentos candidatos a reforço.'),
}

with aba_analises:
    escolha = st.selectbox('Selecione a análise', list(ANALISES))
    grafico, leitura = ANALISES[escolha]
    col1, col2 = st.columns([3, 2])
    col1.pyplot(grafico())
    col2.markdown(f'**Leitura:** {leitura}')

# ============================================================
# 3. SIMULADOR
# ============================================================
with aba_simulador:
    st.markdown(
        'Informe os indicadores **atuais** do aluno para estimar a probabilidade de ele estar **defasado no '
        'próximo ano**. O modelo foi validado prevendo 2024 a partir de 2023 (AUC 0,88).')

    with st.form('simulador'):
        c1, c2, c3 = st.columns(3)
        nivel = c1.selectbox('Situação atual de defasagem (IAN)',
                             ['Sem defasagem (IAN 10)', 'Moderada (IAN 5)', 'Severa (IAN 2,5)'])
        idade = c2.number_input('Idade', min_value=6, max_value=30, value=12)
        fase = c3.selectbox('Fase', list(range(0, 10)), index=3,
                            format_func=lambda f: 'ALFA' if f == 0 else f'Fase {f}')

        c4, c5, c6 = st.columns(3)
        ida = c4.slider('IDA — desempenho acadêmico', 0.0, 10.0, 6.5, 0.1)
        ieg = c5.slider('IEG — engajamento', 0.0, 10.0, 7.5, 0.1)
        ipv = c6.slider('IPV — ponto de virada', 0.0, 10.0, 7.5, 0.1)
        c7, c8, _ = st.columns(3)
        iaa = c7.slider('IAA — autoavaliação', 0.0, 10.0, 8.0, 0.1)
        ips = c8.slider('IPS — psicossocial', 0.0, 10.0, 7.0, 0.1)

        enviar = st.form_submit_button('Estimar risco', type='primary')

    if enviar:
        ian = {'Sem defasagem (IAN 10)': 10.0, 'Moderada (IAN 5)': 5.0, 'Severa (IAN 2,5)': 2.5}[nivel]
        prob = prever_risco(artefato, {'IAN': ian, 'IDA': ida, 'IEG': ieg, 'IAA': iaa,
                                       'IPS': ips, 'IPV': ipv, 'IDADE': idade, 'FASE': fase})
        faixa = faixa_risco(prob)
        r1, r2 = st.columns(2)
        r1.metric('Probabilidade de defasagem no próximo ano', f'{prob:.0%}')
        r2.metric('Faixa de risco', faixa)
        mensagem = {'Alto': st.error, 'Médio': st.warning, 'Baixo': st.success}[faixa]
        mensagem({'Alto': 'Priorizar acompanhamento e avaliar a progressão de fase deste aluno.',
                  'Médio': 'Acompanhar de perto ao longo do ano.',
                  'Baixo': 'Sem sinal de risco relevante para o próximo ano.'}[faixa])
        st.caption('Fase e idade são as variáveis mais importantes do modelo: o principal fator de risco é '
                   'o aluno ficar para trás na progressão de fase em relação à idade.')

# ============================================================
# 4. RANKING
# ============================================================
with aba_ranking:
    st.markdown('Probabilidade estimada de cada aluno de 2024 estar **defasado em 2025**.')
    c1, c2 = st.columns(2)
    faixas = c1.multiselect('Faixa de risco', ['Alto', 'Médio', 'Baixo'], default=['Alto'])
    situacao = c2.multiselect('Situação em 2024', ['Sem defasagem', 'Moderada', 'Severa'],
                              default=['Sem defasagem', 'Moderada', 'Severa'])
    so_novos = st.checkbox('Mostrar só alunos que hoje estão sem defasagem (risco de entrar em defasagem)')

    filtro = ranking['FAIXA_RISCO'].isin(faixas) & ranking['NIVEL_DEFASAGEM'].isin(situacao)
    if so_novos:
        filtro &= ranking['NIVEL_DEFASAGEM'] == 'Sem defasagem'
    tabela = ranking[filtro]

    st.write(f'**{len(tabela)} alunos**')
    st.dataframe(
        tabela, hide_index=True, width='stretch',
        column_config={'PROB_DEFASAGEM_2025': st.column_config.ProgressColumn(
            'Prob. defasagem 2025', format='percent', min_value=0, max_value=1)})
    st.download_button('Baixar lista (CSV)', tabela.to_csv(index=False).encode('utf-8'),
                       'alunos_risco_2025.csv', 'text/csv')
