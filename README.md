# 🏎️ Formula 1 Chatbot (FastF1)

## 📌 Sobre o Projeto

O **Formula 1 Chatbot** é um assistente virtual desenvolvido para fornecer informações detalhadas sobre o mundo da Fórmula 1. Utilizando a biblioteca **FastF1**, o chatbot é capaz de acessar e processar dados oficiais das corridas para responder perguntas em tempo real ou históricas.

O projeto tem como foco oferecer uma experiência interativa para fãs da Fórmula 1, permitindo consultar estatísticas, resultados e informações sobre pilotos, equipes e corridas de forma rápida e intuitiva.

## 🎯 Objetivo

O objetivo do chatbot é **facilitar o acesso a dados da Fórmula 1**, transformando informações técnicas e complexas em respostas simples e acessíveis através de uma interface conversacional.

## 💡 Conceito

O chatbot atua como um **assistente inteligente para fãs de Fórmula 1**, sendo capaz de interpretar perguntas e retornar dados relevantes com base nas informações obtidas via FastF1.

Entre as principais interações esperadas, estão:

- Consulta de **resultados de corridas**
- Informações sobre **classificações (qualifying)**
- Dados de **pilotos e equipes**
- Comparação de desempenho entre pilotos
- Informações sobre **voltas rápidas e telemetria**
- Estatísticas de temporadas e corridas específicas

## ⚙️ Tecnologia Base

O projeto utiliza a biblioteca **FastF1**, que fornece acesso a dados detalhados da Fórmula 1, incluindo:

- Tempos de volta
- Telemetria
- Dados de sessões (treinos, classificação e corrida)
- Informações de clima e pista

Esses dados são processados pelo chatbot para gerar respostas dinâmicas e informativas.

## 🧠 Funcionamento

O fluxo básico do chatbot segue os seguintes passos:

1. O usuário faz uma pergunta (ex: “Quem venceu o GP de Mônaco de 2023?”)
2. O chatbot interpreta a intenção da pergunta
3. O sistema consulta primeiro a base local estruturada em `data/`
4. Se a base local não tiver informação suficiente, o LLM é usado como fallback
5. A resposta é processada e retornada ao usuário de forma clara

No código, os dados importados ficam organizados em camadas:

- **Bronze:** leitura direta dos arquivos `.parquet`
- **Silver:** normalização de tipos, nomes, datas, posições e pontuação
- **ABT local:** tabela analítica usada para treinar a predição do campeão de pilotos

## 🤖 LLM utilizado

O fallback generativo usa o modelo [`Qwen/Qwen2.5-1.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct), disponível no Hugging Face.

Esse modelo foi mantido porque é uma boa escolha para o contexto do trabalho: é pequeno o bastante para rodar localmente em máquinas comuns, é ajustado para seguir instruções, tem suporte a português e lida bem com dados estruturados no prompt. Modelos maiores, como `Qwen/Qwen2.5-3B-Instruct`, podem responder melhor, mas aumentam bastante o custo de memória e tempo de execução para um projeto de faculdade.

Para testar outro modelo compatível com `transformers`, execute definindo a variável:

```bash
F1_LLM_MODEL_ID="Qwen/Qwen2.5-3B-Instruct" python app.py
```

### Download do modelo

Ao executar `python app.py`, o projeto baixa/carrega o modelo do Hugging Face antes de iniciar o Flask. Para evitar limite de requisições anônimas e melhorar a velocidade, crie um token de leitura em <https://huggingface.co/settings/tokens> e autentique uma vez no terminal:

```bash
huggingface-cli login
```

Também é possível usar variável de ambiente diretamente no terminal:

```bash
export HF_TOKEN=hf_seu_token_aqui
python app.py
```

Se quiser cancelar um download em andamento, pressione `Ctrl+C` no terminal. Ao executar novamente, o Hugging Face normalmente reaproveita o que já ficou em cache e continua o download.

## 🏆 Predição do campeonato de pilotos

O chatbot consegue projetar o próximo campeão de pilotos usando um modelo treinado localmente com os dados importados via FastF1.

Perguntas sugeridas:

- `Prever campeão do campeonato de pilotos`
- `Classificação dos pilotos em 2026`

A previsão segue a ideia do projeto [`speed-f1`](https://github.com/TeoMeWhy/speed-f1), mas sem Spark, MLflow ou armazenamento em nuvem. A aplicação monta uma ABT com pandas e treina uma `RandomForestClassifier` local usando temporadas anteriores. A resposta ao usuário fica em linguagem natural, sem expor detalhes internos de arquivos ou pipeline.

Além da conversa, a interface possui uma aba **Dashboard** com a predição do campeão, barras comparando os principais candidatos, classificação atual, vencedores recentes e vitórias por equipe.

## 👥 Público-Alvo

Este projeto é voltado para:

- Fãs de Fórmula 1
- Entusiastas de análise de dados esportivos
- Desenvolvedores interessados em aplicações com dados esportivos

## Tecnologias utilizadas
- Python
- Flask
- Pandas
- scikit-learn
- Transformers
- HTML/CSS/JavaScript

## Como executar
1. Clone o repositório
2. Crie um ambiente virtual
3. Instale as dependências:
   pip install -r requirements.txt
4. Execute:
   python app.py

## Estrutura do projeto
- `app.py`: inicialização da aplicação Flask
- `chatbot/engine.py`: lógica principal do chatbot
- `templates/`: interface HTML
- `static/`: arquivos estáticos

## Funcionalidades atuais
- Interface web de chat
- Conversa livre com LLM local como fallback
- Consulta prévia à base estruturada de F1
- Predição local do campeonato de pilotos
- Dashboard com gráfico de predição e recortes estatísticos
- Contexto básico de conversa sobre Fórmula 1
