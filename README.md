# Formula 1 Chatbot

Aplicação web para consulta conversacional sobre Fórmula 1, com dados estruturados de corridas, respostas geradas por modelo local e dashboard com indicadores da temporada.

## Objetivo

O projeto organiza dados históricos e recentes da Fórmula 1 para responder perguntas sobre pilotos, equipes, resultados, classificação e projeção do campeonato de pilotos. A aplicação combina uma base local em arquivos `.parquet` com um modelo de linguagem executado localmente para perguntas gerais sobre a categoria.

## Coleta de Dados

Os dados são obtidos pelo script `collect.py`, utilizando a biblioteca `FastF1`. O processo coleta sessões de corrida e sprint, adiciona metadados do evento e grava os resultados em `data/` no formato `.parquet`.

Exemplo de atualização da temporada:

```bash
python collect.py --years 2026 --modes R S
```

Cada arquivo segue o padrão:

```text
data/{ano}_{etapa}_{modo}.parquet
```

Exemplos:

- `data/2026_07_R.parquet`
- `data/2026_05_S.parquet`

## Tratamento dos Dados

O carregamento dos dados é feito em `chatbot/data_loader.py`. O pipeline local possui três etapas principais:

- **Leitura:** carregamento dos arquivos `.parquet` de corridas e sprints.
- **Normalização:** conversão de tipos, padronização de nomes, datas, equipes, pontuação e posições.
- **Métricas derivadas:** cálculo de vitórias, pódios, média de chegada, média de largada, pontos por etapa, taxa de finalização e abandonos.

Também são preservadas informações como `Status`, `ClassifiedPosition` e `Laps`, usadas para diferenciar chegada, abandono e ausência de largada.

## Funcionamento do Chatbot

O chatbot segue uma ordem de resposta definida:

1. Validação da mensagem recebida.
2. Consulta à base estruturada para perguntas com resposta direta nos dados locais.
3. Uso do modelo de linguagem local para perguntas gerais sobre Fórmula 1.
4. Inclusão de um hook conversacional ao final da resposta para manter a interação ativa.

Consultas estruturadas cobrem casos como:

- classificação de pilotos;
- vencedor da corrida mais recente;
- vencedores recentes;
- perfil básico de pilotos presentes nos dados;
- previsão do campeonato de pilotos.

Perguntas conceituais, técnicas ou abertas são encaminhadas ao modelo de linguagem.

## Modelo de Linguagem

O fallback generativo utiliza o modelo `Qwen/Qwen2.5-1.5B-Instruct` por meio da biblioteca `transformers`.

O modelo é carregado localmente na inicialização da aplicação, salvo quando o preload é desativado por variável de ambiente. A geração foi configurada para priorizar respostas determinísticas e focadas na pergunta atual.

Para usar outro modelo compatível com `transformers`:

```bash
F1_LLM_MODEL_ID="Qwen/Qwen2.5-3B-Instruct" python app.py
```

Para desativar o carregamento inicial do modelo:

```bash
F1_PRELOAD_LLM=0 python app.py
```

## Predição do Campeonato de Pilotos

A aplicação monta uma tabela analítica por piloto e etapa para treinar um modelo local de classificação. O modelo usa temporadas anteriores como histórico e aplica a projeção sobre a temporada mais recente.

As principais variáveis usadas na predição incluem:

- pontos acumulados;
- média de pontos por etapa;
- vitórias;
- pódios;
- média de chegada;
- média de largada;
- desempenho da temporada anterior;
- taxa de finalização;
- abandonos e ausências de largada;
- distância em pontos para o líder.

O modelo principal é um `RandomForestClassifier`. Após a previsão inicial, a pontuação é recalibrada com sinais da temporada atual para evitar superestimar pilotos com bom histórico, mas baixa consistência ou muitos abandonos no ano corrente.

## Dashboard

A interface possui uma aba de dashboard com:

- piloto projetado como favorito ao campeonato;
- probabilidades dos principais candidatos;
- classificação atual de pilotos;
- vencedores recentes;
- vitórias por equipe na temporada;
- resumo da temporada carregada.

As vitórias por equipe são calculadas apenas sobre a temporada mais recente disponível, não sobre todo o histórico.

## Estrutura do Projeto

```text
.
├── app.py
├── collect.py
├── chatbot/
│   ├── data_loader.py
│   ├── engine.py
│   ├── hooks.py
│   ├── intents.py
│   ├── llm_client.py
│   └── reflections.py
├── data/
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── requirements.txt
└── test_llm.py
```

## Tecnologias

- Python
- Flask
- Pandas
- FastF1
- scikit-learn
- Transformers
- PyTorch
- HTML
- CSS
- JavaScript

## Execução

Criar e ativar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Executar a aplicação:

```bash
python app.py
```

Depois da inicialização, a interface fica disponível no endereço exibido pelo Flask.

## Funcionalidades

- Chat web sobre Fórmula 1.
- Respostas estruturadas a partir dos dados locais.
- Fallback generativo com LLM local.
- Perfis básicos de pilotos.
- Consulta de classificação e vencedores recentes.
- Predição local do campeonato de pilotos.
- Dashboard com recortes da temporada atual.
