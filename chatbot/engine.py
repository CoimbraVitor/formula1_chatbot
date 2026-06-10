import random
import re

from chatbot.llm_client import query_llm
from chatbot.data_loader import build_knowledge_base
from chatbot.hooks import get_f1_hooks


class F1Chatbot:

    def __init__(self):
        self.context = {}
        self.hooks = get_f1_hooks()
        self.history = []

        self.interaction_count = 0
        self.current_phase = "WELCOME"
        self.used_hooks = set()
        self.last_hook = ""

        self.phases = ["WELCOME", "BASICS", "TECH", "STRATEGY", "DRIVERS", "CLOSING"]

        self.known_drivers = [
            "hamilton", "verstappen", "leclerc", "alonso",
            "senna", "perez", "russell", "norris", "piastri",
        ]
        self.known_topics = [
            "drs", "pit stop", "f1", "formula 1",
            "pneus", "aerodinâmica", "safety car",
        ]

        self.knowledge_base = build_knowledge_base()
        self.data_context = self.knowledge_base.context

    def _get_next_hook(self):
        available_hooks = [
            h for h in self.hooks[self.current_phase] if h not in self.used_hooks
        ]

        if not available_hooks:
            current_index = self.phases.index(self.current_phase)
            if current_index < len(self.phases) - 1:
                self.current_phase = self.phases[current_index + 1]
                available_hooks = self.hooks[self.current_phase]
            else:
                return "O que mais você gostaria de saber sobre este mundo incrível da F1?"

        hook = random.choice(available_hooks)
        self.used_hooks.add(hook)
        self.last_hook = hook
        return hook

    def extract_entities(self, text: str):
        entities = {}
        for driver in self.known_drivers:
            if driver in text:
                entities["driver"] = driver
        for topic in self.known_topics:
            if topic in text:
                entities["topic"] = topic
        return entities

    def _remember(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        self.history = self.history[-8:]

    def get_response(self, user_input: str) -> str:
        """
        Gera a resposta do chatbot a partir da mensagem do usuário.
        Valida se a entrada é uma string não vazia antes de processar.
        """
        self.interaction_count += 1

        if not isinstance(user_input, str) or not user_input.strip():
            return "Desculpe, não entendi sua mensagem. Poderia reformular?"

        original_input = user_input.strip()
        user_input = original_input.lower()

        entities = self.extract_entities(user_input)
        self.context.update(entities)

        response = ""

        if re.search(r"\b(sim|quero|claro|conta|explica|quero saber|bora|manda)\b", user_input):
            if "primeira corrida" in self.last_hook.lower():
                response = (
                    "A primeira corrida oficial da F1 foi o GP da Grã-Bretanha em Silverstone, "
                    "em 13 de maio de 1950. Giuseppe Farina venceu com uma Alfa Romeo! "
                    "Imagine a emoção daquela largada histórica."
                )
            elif "funciona" in self.last_hook.lower() and "drs" in self.last_hook.lower():
                response = (
                    "O DRS funciona assim: quando um piloto está a menos de 1 segundo do carro "
                    "à frente, ele pode abrir a asa traseira em zonas específicas. Isso reduz o "
                    "arrasto e dá uns 10 a 12 km/h a mais de velocidade final!"
                )
            elif "controlam" in self.last_hook.lower() and "botões" in self.last_hook.lower():
                response = (
                    "No volante, os pilotos controlam desde a mistura de combustível e o balanço "
                    "dos freios até o rádio e o 'drink' (água). É como operar um computador a 300 km/h!"
                )
            elif "pit stop" in self.last_hook.lower() and "dura" in self.last_hook.lower():
                response = (
                    "Hoje, um pit stop perfeito dura cerca de 2 segundos! A Red Bull já chegou a "
                    "fazer em incríveis 1.82 segundos. É um trabalho de equipe sincronizado ao milésimo."
                )
            elif "significa" in self.last_hook.lower() and "bandeira quadriculada" in self.last_hook.lower():
                response = (
                    "A bandeira quadriculada preta e branca (dividida diagonalmente) é um aviso de "
                    "conduta antidesportiva. É como o 'cartão amarelo' do futebol na F1!"
                )

        if not response and "favorito" in user_input and ("piloto" in user_input or "meu" in user_input):
            fav_match = re.search(r"favorito é (.*)", user_input)
            if fav_match:
                driver = fav_match.group(1)
                self.context["favorite_driver"] = driver
                response = f"{driver.title()} é uma ótima escolha! Vou guardar isso comigo 😄"

        if not response and "qual meu piloto favorito" in user_input:
            if "favorite_driver" in self.context:
                response = f"Seu piloto favorito é {self.context['favorite_driver'].title()} 🏎️"
            else:
                response = "Ainda não tive o prazer de saber sua preferência! 😄"

        if not response and user_input in ["por que", "por quê", "pq"]:
            if "driver" in self.context:
                response = f"{self.context['driver'].title()} é reconhecido pelo seu talento e consistência nas pistas!"
            elif "topic" in self.context:
                response = f"{self.context['topic'].upper()} é um dos pilares para entender como a F1 funciona hoje."
            else:
                response = "Fiquei curioso com sua pergunta! Pode me dar um pouco mais de contexto? 😅"

        if not response and any(kw in user_input for kw in ["fala mais", "explica mais", "conte-me mais"]):
            if "topic" in self.context:
                response = f"Claro! O assunto {self.context['topic']} é fascinante. Quer focar na parte técnica ou em exemplos reais?"
            else:
                response = "Tem tantos assuntos na F1! Qual exatamente você quer aprofundar agora?"

        if not response:
            data_answer = self.knowledge_base.answer(user_input)
            if data_answer:
                response = data_answer

        if not response:
            print("[ENGINE] Base estruturada sem resposta completa → acionando LLM...")
            llm_answer, _ = query_llm(
                user_message=original_input,
                data_context=self.data_context,
                history=self.history,
            )
            response = llm_answer

        next_hook = self._get_next_hook()
        response = response.rstrip()
        if response and response[-1] not in ".!?":
            response += "."
        
        
        connectors = [
            "\n\nMas me diga uma coisa: ",
            " Por sinal, ",
            " Mudando um pouco o rumo da conversa, ",
            " Além disso, ",
            " Aliás, ",
        ]

        final_response = f"{response}{random.choice(connectors)}{next_hook}"
        self._remember("user", original_input)
        self._remember("assistant", final_response)
        return final_response
