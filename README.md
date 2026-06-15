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

## Justificativas Técnicas

### Escolha do modelo do Hugging Face

O projeto utiliza o modelo `Qwen/Qwen2.5-1.5B-Instruct` porque ele equilibra qualidade de resposta, custo computacional e facilidade de execução local. Por ser um modelo instruct, ele já é otimizado para seguir comandos em formato conversacional, o que combina com a proposta de um chatbot sobre Fórmula 1. O tamanho de 1.5B parâmetros também permite rodar em máquinas sem infraestrutura dedicada de GPU, mantendo o projeto reproduzível para desenvolvimento, testes e apresentação.

A integração via Hugging Face e `transformers` foi escolhida por oferecer um fluxo padronizado de download, cache, tokenização e inferência. Isso também facilita trocar o modelo por outro compatível no futuro usando a variável `F1_LLM_MODEL_ID`, sem alterar a arquitetura principal do chatbot.

### Construção do agente

O agente foi construído como uma camada de orquestração entre entrada do usuário, base estruturada e modelo generativo. A classe `F1Chatbot` mantém contexto simples da conversa, identifica entidades básicas, controla hooks conversacionais e decide qual fonte deve responder cada pergunta.

Essa abordagem evita depender exclusivamente do LLM para tudo. Perguntas com resposta objetiva, como classificação, vencedor recente ou projeção do campeonato, são tratadas primeiro pela base local. Isso reduz alucinações e garante que respostas estatísticas sejam derivadas dos dados carregados. O LLM fica responsável por perguntas abertas, conceituais ou explicativas, nas quais a linguagem natural é mais importante que uma consulta tabular.

### Implementação da lógica de decisão: base para LLM

A lógica segue um fluxo em camadas:

1. A mensagem é validada e normalizada.
2. O agente tenta resolver a pergunta com regras conversacionais e contexto já conhecido.
3. A base estruturada é consultada para intents ligadas a dados de corrida, pontuação, vencedores, pilotos e predição.
4. Se a base não produzir uma resposta completa, a pergunta é enviada ao LLM local.
5. Quando necessário, um resumo estatístico da base é incluído no prompt para orientar o modelo sem expor detalhes internos ao usuário.

Essa ordem foi escolhida porque dados estruturados são mais confiáveis para fatos mensuráveis, enquanto o LLM é mais adequado para explicar conceitos e responder perguntas menos previsíveis.

### Integração com APIs ou base externa

A coleta de dados usa a biblioteca `FastF1`, que fornece acesso a dados oficiais e históricos de sessões da Fórmula 1. O script `collect.py` busca corridas e sprints por ano e etapa, adiciona metadados do evento e salva os resultados localmente.

Após a coleta, a aplicação passa a operar sobre uma base local em `data/`. Isso diminui a dependência de chamadas externas durante o uso do chatbot, melhora o tempo de resposta e torna o comportamento mais estável mesmo quando há instabilidade de rede ou limitação de acesso à fonte original.

### Arquitetura do sistema

A arquitetura foi separada em responsabilidades claras:

- `app.py`: camada web Flask, rotas de chat e dashboard.
- `collect.py`: coleta e persistência dos dados da Fórmula 1.
- `chatbot/data_loader.py`: leitura, normalização, métricas, respostas estruturadas e predição.
- `chatbot/engine.py`: orquestração do agente e decisão entre base estruturada e LLM.
- `chatbot/llm_client.py`: carregamento e inferência do modelo Hugging Face.
- `templates/` e `static/`: interface web, estilos e scripts do dashboard.

Essa divisão facilita manutenção e evolução. A coleta pode ser atualizada sem alterar a interface, o modelo pode ser trocado sem reescrever a lógica do agente, e novas consultas estruturadas podem ser adicionadas na base sem depender de mudanças no front-end.

### Motivo de utilização de Parquet

O formato `.parquet` foi utilizado por ser eficiente para dados tabulares analíticos. Ele armazena os dados em formato colunar, o que melhora leitura, compressão e processamento com Pandas quando comparado a formatos textuais como CSV.

No contexto do projeto, os dados de corridas possuem várias colunas numéricas, categóricas e temporais. O Parquet preserva melhor os tipos de dados, reduz o tamanho dos arquivos e acelera o carregamento da base local. Isso é importante porque o chatbot consulta esses dados na inicialização e usa a base para gerar métricas, rankings, vencedores recentes e features do modelo de predição.

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
