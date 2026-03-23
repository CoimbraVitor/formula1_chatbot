import random
import nltk
from nltk.chat.util import Chat, reflections

pares = [
    [r"Olá|Oi|Bom dia|Boa tarde|Boa noite",
     ['Olá! Como posso ajudar você hoje?']],
    [r"Qual é o seu nome?|Como você se chama?",
     ['Eu sou um chatbot criado para ajudar você.']],
    [r"Como você está?|Tudo bem?",
     ['Estou bem, obrigado por perguntar! E você?']],
]

pares.extend([
    [r"(.+)", ["Entendi","Interessante","Talvez","Pode me contar mais sobre isso?"]]
])

reflections = {
    "eu": "você",
    "minha": "sua",
    "meu": "seu",
    "você": "eu",
    "sua": "minha",
}

chatbot = Chat(pares, reflections)

while True:
    entrada_usuario = input("Você: ")
    if entrada_usuario.lower() in ["sair", "tchau", "adeus"]:
        print("Chatbot: Até mais!")
        break
    resposta = chatbot.respond(entrada_usuario)
    print("Chatbot:", resposta)
