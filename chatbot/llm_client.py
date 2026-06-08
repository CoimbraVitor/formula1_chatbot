import os
import time
 
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "1")
 
import torch
from huggingface_hub import get_token, snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = os.getenv("F1_LLM_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
 
_device = None
_model = None
_tokenizer = None
_model_path = None
 
_SYSTEM_PROMPT = """\
Você é o "F1 Bot", um especialista apaixonado em Fórmula 1.
Responda SEMPRE em português brasileiro, de forma amigável e precisa.
Seja conciso: no máximo 10 parágrafos por resposta.
Use as estatísticas abaixo para embasar análises e previsões.
Nunca invente dados — se não souber, diga claramente.
Não mencione arquivos, parquet, pasta data, base estruturada, contexto interno,
fallback ou detalhes de implementação. Para o usuário, você simplesmente conhece F1.
 
{data_context}"""


def _detect_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _load_model():
    global _device, _model, _tokenizer, _model_path

    if _model is not None and _tokenizer is not None:
        return _tokenizer, _model, _device

    _device = _detect_device()
    print(f"[LLM] Dispositivo detectado: {_device.upper()}")
    print(f"[LLM] Preparando download/cache de {MODEL_ID}...")

    token = get_token()
    if token:
        print("[LLM] Token do Hugging Face encontrado. Download autenticado habilitado.")
    else:
        print("[LLM] Nenhum token do Hugging Face encontrado. Download anônimo pode ser mais lento.")
        print("[LLM] Para autenticar, rode: huggingface-cli login")

    _model_path = snapshot_download(
        repo_id=MODEL_ID,
        token=token,
        allow_patterns=[
            "*.json",
            "*.model",
            "*.safetensors",
            "*.txt",
            "merges.txt",
            "vocab.json",
        ],
    )

    print(f"[LLM] Modelo baixado/em cache em: {_model_path}")
    print("[LLM] Carregando modelo na memória...")

    _tokenizer = AutoTokenizer.from_pretrained(_model_path)

    if _device == "cuda":
        _model = AutoModelForCausalLM.from_pretrained(
            _model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
    else:
        dtype = torch.float16 if _device == "mps" else torch.float32
        _model = AutoModelForCausalLM.from_pretrained(
            _model_path,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
        ).to(_device)

    _model.eval()
    print("[LLM] Modelo pronto!")
    return _tokenizer, _model, _device


def preload_model() -> bool:
    """Baixa/carrega o modelo no início da aplicação."""
    try:
        _load_model()
        return True
    except Exception as e:
        print(f"[LLM] Erro ao carregar modelo no startup: {e}")
        return False
 
 
def query_llm(
    user_message: str,
    data_context: str = "",
    history: list[dict[str, str]] | None = None,
) -> tuple[str, bool]:
    """
    Gera uma resposta local com o modelo CausalLM.
 
    Parâmetros:
        user_message — pergunta/mensagem atual do usuário.
        data_context — resumo estatístico dos dados históricos de corridas.
        history — últimas mensagens da conversa.
 
    Retorna:
        (texto_da_resposta, sucesso: bool)
    """
    try:
        tokenizer, model, device = _load_model()
        system_content = _SYSTEM_PROMPT.format(data_context=data_context)
 
        messages = [{"role": "system", "content": system_content}]
        if history:
            messages.extend(history[-8:])
        messages.append({"role": "user", "content": user_message})
 
        prompt_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
 
        inputs = tokenizer(
            prompt_text,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        ).to(device)
 
        prompt_len = inputs["input_ids"].shape[1]
 
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.15,
                pad_token_id=tokenizer.eos_token_id,
            )
        elapsed = time.time() - start
 
        new_tokens = outputs[0][prompt_len:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
 
        print(f"[LLM] Respondeu em {elapsed:.1f}s ({len(new_tokens)} tokens)")
        return response, True
 
    except Exception as e:
        print(f"[LLM] Erro na geração: {e}")
        return _fallback_response(), False
 
 
def _fallback_response() -> str:
    return (
        "Não consegui gerar uma resposta agora. "
        "Tente perguntar sobre DRS, pit stop, pilotos ou equipes da F1!"
    )
 
 
def check_connection() -> bool:
    """Sempre True — o modelo roda localmente depois do primeiro download."""
    return True
