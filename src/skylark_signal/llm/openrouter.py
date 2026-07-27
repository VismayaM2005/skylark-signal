import time
import requests
from typing import List, Optional, Dict, Any, Tuple
from skylark_signal.config import config
from skylark_signal.llm.schemas import OpenRouterModel

FALLBACK_MODELS = [
    OpenRouterModel(id="openai/gpt-4o-mini", name="OpenAI: GPT-4o Mini"),
    OpenRouterModel(id="openai/gpt-4o", name="OpenAI: GPT-4o"),
    OpenRouterModel(id="anthropic/claude-3.5-sonnet", name="Anthropic: Claude 3.5 Sonnet"),
    OpenRouterModel(id="meta-llama/llama-3.3-70b-instruct", name="Meta: Llama 3.3 70B Instruct"),
    OpenRouterModel(id="google/gemini-2.0-flash-001", name="Google: Gemini 2.0 Flash"),
    OpenRouterModel(id="deepseek/deepseek-chat", name="DeepSeek: DeepSeek V3"),
    OpenRouterModel(id="mistralai/mistral-large-2411", name="Mistral: Mistral Large 2411")
]

# Cache: (timestamp, models_list)
_OPENROUTER_CACHE: Optional[Tuple[float, List[OpenRouterModel]]] = None

def fetch_openrouter_models(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    cache_ttl: int = 600,
    force_refresh: bool = False
) -> List[OpenRouterModel]:
    """
    Fetches the live list of models from OpenRouter API with TTL caching and fallback support.
    """
    global _OPENROUTER_CACHE
    now = time.time()

    if not force_refresh and _OPENROUTER_CACHE is not None:
        ts, cached_models = _OPENROUTER_CACHE
        if now - ts < cache_ttl:
            return cached_models

    target_url = (base_url or config.openrouter_base_url).rstrip("/") + "/models"
    key = api_key or config.openrouter_api_key

    headers = {
        "HTTP-Referer": config.openrouter_http_referer,
        "X-Title": config.openrouter_app_title
    }
    if key:
        headers["Authorization"] = f"Bearer {key}"

    try:
        resp = requests.get(target_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        models_data = data.get("data", [])
        if not models_data:
            _OPENROUTER_CACHE = (now, FALLBACK_MODELS)
            return FALLBACK_MODELS

        parsed_models: List[OpenRouterModel] = []
        for m in models_data:
            m_id = m.get("id")
            m_name = m.get("name", m_id)
            if m_id:
                parsed_models.append(OpenRouterModel(
                    id=m_id,
                    name=m_name,
                    description=m.get("description"),
                    context_length=m.get("context_length")
                ))

        if not parsed_models:
            parsed_models = FALLBACK_MODELS

        # Sort models alphabetically by name
        parsed_models = sorted(parsed_models, key=lambda x: x.name.lower())

        _OPENROUTER_CACHE = (now, parsed_models)
        return parsed_models

    except Exception:
        # Fallback to predefined models if fetch fails
        _OPENROUTER_CACHE = (now, FALLBACK_MODELS)
        return FALLBACK_MODELS
