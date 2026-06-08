import random
import re
from nltk.chat.util import Chat

from chatbot.intents import get_f1_intents
from chatbot.reflections import get_reflections
from chatbot.hooks import get_f1_hooks


class F1Chatbot:

    def __init__(self):
        self.chat = Chat(get_f1_intents(), get_reflections())
        self.context = {}
        self.hooks = get_f1_hooks()
        
        # Estado do Diálogo
        self.interaction_count = 0
        self.current_phase = "WELCOME"
        self.used_hooks = set()
        self.last_hook = ""
        
        # Ordem das fases para guiar a conversa
        self.phases = ["WELCOME", "BASICS", "TECH", "STRATEGY", "DRIVERS", "CLOSING"]

        # 🔥 entidades conhecidas
        self.known_drivers = ["hamilton", "verstappen", "leclerc", "alonso", "senna", "perez", "russell"]
        self.known_topics = ["drs", "pit stop", "f1", "formula 1", "pneus", "aerodinâmica", "safety car"]

    def _get_next_hook(self):
        """Seleciona o próximo gancho de conversa baseado na fase atual."""
        available_hooks = [h for h in self.hooks[self.current_phase] if h not in self.used_hooks]
        
        # Se esgotou os ganchos da fase atual, avança para a próxima
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

    # ---------------- EXTRAÇÃO DINÂMICA ----------------
    def extract_entities(self, text: str):
        entities = {}
        for driver in self.known_drivers:
            if driver in text:
                entities["driver"] = driver
        for topic in self.known_topics:
            if topic in text:
                entities["topic"] = topic
        return entities

    # ---------------- RESPOSTA ----------------
    def get_response(self, user_input: str) -> str:
        """
        Gera a resposta do chatbot a partir da mensagem do usuário.
        Valida se a entrada é uma string não vazia antes de processar.
        """
        self.interaction_count += 1

        # ---------- Validação ----------
        if not isinstance(user_input, str) or not user_input.strip():
            return "Desculpe, não entendi sua mensagem. Poderia reformular?"
        user_input = user_input.lower()

        entities = self.extract_entities(user_input)
        self.context.update(entities)

        response = ""

        # ---------------- TRATAMENTO DE RESPOSTAS AFIRMATIVAS BASEADAS NO GANCHO ----------------
        # Se o usuário disse "sim", "quero", "conta", etc.
        if re.search(r"\b(sim|quero|claro|conta|explica|quero saber|bora|manda)\b", user_input):
            if "primeira corrida" in self.last_hook.lower():
                response = "A primeira corrida oficial da F1 foi o GP da Grã-Bretanha em Silverstone, em 13 de maio de 1950. Giuseppe Farina venceu com uma Alfa Romeo! Imagine a emoção daquela largada histórica."
            elif "funciona" in self.last_hook.lower() and "drs" in self.last_hook.lower():
                response = "O DRS funciona assim: quando um piloto está a menos de 1 segundo do carro à frente, ele pode abrir a asa traseira em zonas específicas. Isso reduz o arrasto e dá uns 10 a 12 km/h a mais de velocidade final!"
            elif "controlam" in self.last_hook.lower() and "botões" in self.last_hook.lower():
                response = "No volante, os pilotos controlam desde a mistura de combustível e o balanço dos freios até o rádio e o 'drink' (água). É como operar um computador a 300 km/h!"
            elif "pit stop" in self.last_hook.lower() and "dura" in self.last_hook.lower():
                response = "Hoje, um pit stop perfeito dura cerca de 2 segundos! A Red Bull já chegou a fazer em incríveis 1.82 segundos. É um trabalho de equipe sincronizado ao milésimo."
            elif "significa" in self.last_hook.lower() and "bandeira quadriculada" in self.last_hook.lower():
                response = "A bandeira quadriculada preta e branca (dividida diagonalmente) é um aviso de conduta antidesportiva. É como o 'cartão amarelo' do futebol na F1!"

        # ---------------- FAVORITO DINÂMICO ----------------
        if not response and "favorito" in user_input and ("piloto" in user_input or "meu" in user_input):
            fav_match = re.search(r"favorito é (.*)", user_input)
            if fav_match:
                driver = fav_match.group(1)
                self.context["favorite_driver"] = driver
                response = f"{driver.title()} é uma ótima escolha! Vou guardar isso comigo 😄"

        # ---------------- USO DO CONTEXTO ----------------
        if not response and "qual meu piloto favorito" in user_input:
            if "favorite_driver" in self.context:
                response = f"Seu piloto favorito é {self.context['favorite_driver'].title()} 🏎️"
            else:
                response = "Ainda não tive o prazer de saber sua preferência! 😄"

        # ---------------- PERGUNTAS CONTEXTUAIS ----------------
        if not response and user_input in ["por que", "por quê", "pq"]:
            if "driver" in self.context:
                response = f"{self.context['driver'].title()} é reconhecido pelo seu talento e consistência nas pistas!"
            elif "topic" in self.context:
                response = f"{self.context['topic'].upper()} é um dos pilares para entender como a F1 funciona hoje."
            else:
                response = "Fiquei curioso com sua pergunta! Pode me dar um pouco mais de contexto? 😅"

        # ---------------- CONTINUAÇÃO ----------------
        if not response and any(kw in user_input for kw in ["fala mais", "explica mais", "conte-me mais"]):
            if "topic" in self.context:
                response = f"Claro! O assunto {self.context['topic']} é fascinante. Quer focar na parte técnica ou em exemplos reais?"
            else:
                response = "Tem tantos assuntos na F1! Qual exatamente você quer aprofundar agora?"

        # ---------------- FALLBACK NLTK ----------------
        if not response:
            nltk_response = self.chat.respond(user_input)
            response = nltk_response if nltk_response else "Interessante sua colocação! A F1 sempre nos surpreende com esses detalhes."

        # ---------------- ADIÇÃO DO GANCHO (HOOK) ----------------
        next_hook = self._get_next_hook()
        
        # Conectores variados para soar mais natural
        connectors = [
            "\n\nMas me diga uma coisa: ",
            " Por sinal, ",
            " Mudando um pouco o rumo da conversa, ",
            " Além disso, ",
            " Aliás, "
        ]
        
        full_response = f"{response}{random.choice(connectors)}{next_hook}"

        return full_response