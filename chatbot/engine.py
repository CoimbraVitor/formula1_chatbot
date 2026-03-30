import random
from nltk.chat.util import Chat

from chatbot.intents import get_f1_intents
from chatbot.reflections import get_reflections


class F1Chatbot:

    def __init__(self):
        self.chat = Chat(get_f1_intents(), get_reflections())

    def get_response(self, user_input: str) -> str:
        response = self.chat.respond(user_input.lower())
        return response if response else self.get_fallback()

    def get_fallback(self):
        return random.choice([
            "Não entendi. Escolha uma opção do menu 😊",
            "Tente digitar um número de 1 a 5!"
        ])