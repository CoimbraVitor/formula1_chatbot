from chatbot.llm_client import query_llm, check_connection

print("Conexão OK?", check_connection())

resposta, sucesso = query_llm("O que é o DRS na Fórmula 1?")
print("Sucesso:", sucesso)
print("Resposta:", resposta)