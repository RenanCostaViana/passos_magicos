# 📊 Passos Mágicos — Indicadores e Alerta de Risco de Defasagem

Análise dos indicadores educacionais da Associação Passos Mágicos (base PEDE, 2022 a 2024) e modelo de Machine Learning que estima a probabilidade de cada aluno estar defasado **no ano seguinte**, disponibilizado em um app Streamlit para a equipe da ONG.

Projeto desenvolvido individualmente como Datathon da Fase 5 da Pós-Graduação em Data Analytics (FIAP).

🔗 **App:** [Passos Mágicos](https://paappsmagicos-i7uebmh3gfjwuprwya99x9.streamlit.app/)

> **Convenção:** a defasagem é a diferença entre a fase do aluno no programa e a fase ideal para a sua idade escolar. **Valores negativos indicam aluno atrasado.**

---

## 🔍 Principais Achados

| Pergunta | Resposta curta |
|---|---|
| Perfil de defasagem (IAN) | Alunos sem defasagem passaram de **30% (2022) para 54% (2024)**; a defasagem severa ficou próxima de zero |
| Desempenho (IDA) | Sem tendência clara: subiu em 2023 e recuou em 2024. A **fase 3** tem o menor IDA nos três anos |
| Engajamento x desempenho | Correlação moderada (~0,55) do IEG com IDA e IPV |
| Autoavaliação (IAA) | Pouco coerente com o desempenho (correlação ~0,1); alunos se avaliam **1,5 ponto acima** do IDA |
| Psicossocial (IPS) | Sinal fraco: IPS baixo antecede quedas com um pouco mais de frequência |
| Psicopedagógico (IPP) | Confirma pouco a defasagem (correlação ~0,1 com o IAN) |
| Ponto de virada (IPV) | Anda junto com IPP, IDA e IEG |
| Composição do INDE | É uma **média ponderada fixa**: IDA, IEG e IPV pesam 20% cada; IAN, IAA, IPS e IPP, 10% cada |
| Efetividade do programa | Pedras melhoraram (Topázio de 15% para 31%), mas INDE, IEG e IPV não mostram melhora contínua |
| Onde está o risco | Defasagem concentrada na **fase 1** e entre alunos de **16 e 17 anos** |

O notebook traz os gráficos e a interpretação de cada pergunta.

---

## 🤖 Modelo de Alerta de Risco

### Como o problema foi definido

- **Alvo:** o aluno estará defasado (defasagem < 0) **no ano seguinte**?
- **Variáveis:** indicadores do ano atual (IAN, IDA, IEG, IAA, IPS, IPV), idade e fase.
- **Fora do modelo:** INDE e pedra (são combinações dos próprios indicadores) e IPP (não existe em 2022, primeiro ano de treino).
- **Validação temporal:** treino com a passagem 2022 → 2023 e teste com 2023 → 2024, simulando o uso real: aprender com o passado para prever um ano que o modelo nunca viu.

### Resultados no teste (765 alunos)

| | AUC | Acurácia |
|---|---|---|
| Regra simples ("quem está defasado continua defasado") | 0,68 | 67% |
| **Modelo (Gradient Boosting)** | **0,88** | **79%** |

Entre os **370 alunos sem defasagem em 2023**, 84 entraram em defasagem em 2024. A regra simples não identifica nenhum deles; o modelo os separa dos demais com **AUC de 0,89**. É justamente o caso de maior valor para a ONG: agir antes de o atraso aparecer.

### O que o modelo usa

**Fase e idade** são, de longe, as variáveis mais importantes: a fase ideal depende da idade escolar, então o aluno que envelhece sem avançar de fase entra em defasagem. Os indicadores de desempenho e socioemocionais acrescentam pouco à previsão de um ano para o outro.

### Ranking para 2025

O modelo final, treinado com as duas passagens, foi aplicado aos 1.156 alunos de 2024: **488 aparecem com risco alto** de estar defasados em 2025, sendo **68 deles hoje sem defasagem**.

---

## 🛠️ Revisão em relação à entrega original

Este repositório é uma revisão da versão entregue no Datathon, que tinha problemas metodológicos:

| Versão entregue | Esta versão |
|---|---|
| Alvo `DEFAS > 0`, que identifica alunos **adiantados**, e não em risco | Alvo correto: defasagem negativa |
| IAN e INDE como variáveis do mesmo ano do alvo (o IAN é a própria defasagem em outra escala) | Indicadores de um ano preveem a situação do ano seguinte |
| Só os dados de 2024 entravam no modelo (filtro de nulos em `INDE_2024`) | Usa as três bases, com padronização de nomes, fases e idades |
| SMOTE aplicado antes da divisão treino/teste | Sem balanceamento: as classes já são equilibradas, e a saída principal é a probabilidade |
| Acurácia de 96% sobre dados sintéticos | AUC de 0,88 em validação temporal, com dados reais |

---

## 🖥️ O App

- **Visão geral:** principais números e evolução da defasagem e das pedras.
- **Análises:** gráfico e leitura de cada pergunta do Datathon.
- **Simulador de risco:** indicadores atuais de um aluno → probabilidade de defasagem no ano seguinte.
- **Alunos em risco em 2025:** ranking filtrável por faixa de risco e situação atual, com download em CSV.

---

## ⚠️ Limitações

- **Poucos anos de histórico:** só duas passagens de ano para treinar e testar. O desempenho deve ser reavaliado a cada novo ano de dados.
- **Mudança de cenário entre anos:** a proporção de alunos defasados caiu de 61% para 40% entre os períodos de treino e teste. As probabilidades devem ser lidas como ordem de prioridade, mais do que como valores exatos.
- **Correlação não é causa:** as análises mostram associações entre indicadores, não o efeito de cada ação do programa.
- **Fase e idade dominam a previsão:** o modelo sinaliza bem quem está perto de ficar para trás no calendário escolar, mas diz pouco sobre fatores socioemocionais.

---

## 📁 Estrutura

```
passos_magicos/
├── README.md
├── app.py                        ← aplicação Streamlit
├── analise_passos_magicos.ipynb  ← tratamento, respostas às perguntas e modelo
├── utils/
│   ├── preparacao.py             ← leitura e padronização da base (usado pelo notebook e pelo app)
│   └── funcoes.py                ← gráficos, carregamento e previsão
├── data/
│   └── BASE DE DADOS PEDE 2024 - DATATHON.xlsx
├── dados_limpos.csv              ← base tratada (gerada pelo notebook)
├── ranking_risco_2025.csv        ← risco previsto para 2025 (gerado pelo notebook)
├── modelo_risco.joblib           ← modelo treinado
├── requirements.txt              ← dependências do app
├── requirements-dev.txt          ← dependências extras para o notebook
├── .streamlit/config.toml
└── .gitignore
```

---

## 🚀 Como Executar

```
pip install -r requirements-dev.txt

# notebook (gera as bases e o modelo)
jupyter notebook analise_passos_magicos.ipynb

# app
streamlit run app.py
```

---

## 📬 Contato

LinkedIn: <https://linkedin.com/in/renancostaviana>
E-mail: <renan.cv@outlook.com.br>
