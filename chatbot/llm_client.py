import os
import time

# Suprimir warnings desnecessários do transformers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_ID = "google/flan-t5-small"

# Carrega modelo e tokenizer uma única vez, demora uns 10s, mas as chamadas seguintes ficam instantâneas.
print(f"[LLM] Carregando {MODEL_ID}... (só na primeira vez)")
_tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
_model.eval()
print("[LLM] Modelo pronto!")


def _build_prompt(user_message: str) -> str:
    return f"answer the following question about Formula 1 in Portuguese: {user_message}"


def query_llm(user_message: str) -> tuple[str, bool]:
    """
    Gera resposta localmente com flan-t5-small.

    Parâmetros de geração:
    - max_new_tokens: 200 — suficiente para respostas objetivas
    - num_beams: 4 — beam search, melhor qualidade que greedy
    - early_stopping: para quando todos os beams terminam
    - no_repeat_ngram_size: evita repetição de frases
    """
    try:
        prompt = _build_prompt(user_message)

        inputs = _tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        start = time.time()
        with torch.no_grad():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=200,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )
        elapsed = time.time() - start

        text = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        print(f"[LLM] flan-t5-small respondeu em {elapsed:.1f}s")
        return text, True

    except Exception as e:
        print(f"[LLM] Erro na geração: {e}")
        return _fallback_response(), False


def _fallback_response() -> str:
    return (
        "Não consegui gerar uma resposta agora. "
        "Tente perguntar sobre DRS, pit stop, pilotos ou equipes da F1!"
    )


def check_connection() -> bool:
    """Sempre True — modelo local não depende de rede."""
    return True
