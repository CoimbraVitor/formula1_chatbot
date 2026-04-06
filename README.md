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
3. O sistema consulta os dados através do FastF1
4. A resposta é processada e retornada ao usuário de forma clara

## 👥 Público-Alvo

Este projeto é voltado para:

- Fãs de Fórmula 1
- Entusiastas de análise de dados esportivos
- Desenvolvedores interessados em aplicações com dados esportivos

## Tecnologias utilizadas
- Python
- Flask
- NLTK
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
- Respostas baseadas em padrões
- Contexto básico de conversa sobre Fórmula 1
- Integração com plataformas como Discord ou Telegram
- Atualizações em tempo real durante corridas
