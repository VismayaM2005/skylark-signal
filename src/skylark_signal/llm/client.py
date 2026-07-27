import requests
from typing import Optional, Dict, Any, Tuple
from skylark_signal.config import config
from skylark_signal.llm.schemas import LLMTrace

class LLMClient:
    """
    Unified multi-provider LLM Client supporting OpenRouter, OpenAI, and Deterministic modes,
    complete with execution tracing and fallback proof logging.
    """
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        openai_key: Optional[str] = None
    ):
        self.openrouter_key = openrouter_key or config.openrouter_api_key
        self.openai_key = openai_key or config.openai_api_key

    def generate_text_with_trace(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: str = "deterministic",
        model_slug: Optional[str] = None
    ) -> LLMTrace:
        """
        Generates text using requested provider and model slug, returning a detailed LLMTrace object.
        """
        provider_clean = (provider or "deterministic").lower().strip()
        target_model = model_slug or "none"

        if provider_clean == "deterministic":
            return LLMTrace(
                provider="Deterministic",
                model_slug="None (Deterministic)",
                used_llm=False,
                execution_path="deterministic",
                fallback_reason="Provider explicitly set to Deterministic",
                raw_text=None
            )

        elif provider_clean == "openrouter":
            target_model = model_slug or "openai/gpt-4o-mini"
            if not self.openrouter_key:
                return LLMTrace(
                    provider="OpenRouter",
                    model_slug=target_model,
                    used_llm=False,
                    execution_path="deterministic",
                    fallback_reason="OPENROUTER_API_KEY is missing or unset",
                    raw_text=None
                )

            endpoint = config.openrouter_base_url.rstrip("/") + "/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": config.openrouter_http_referer,
                "X-Title": config.openrouter_app_title
            }

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": target_model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 250
            }

            try:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=15)
                if resp.status_code != 200:
                    err_msg = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    return LLMTrace(
                        provider="OpenRouter",
                        model_slug=target_model,
                        used_llm=False,
                        execution_path="deterministic",
                        fallback_reason=f"OpenRouter API Error ({err_msg})",
                        raw_text=None
                    )

                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "").strip()
                    if content:
                        return LLMTrace(
                            provider="OpenRouter",
                            model_slug=target_model,
                            used_llm=True,
                            execution_path="openrouter",
                            fallback_reason=None,
                            raw_text=content
                        )
                return LLMTrace(
                    provider="OpenRouter",
                    model_slug=target_model,
                    used_llm=False,
                    execution_path="deterministic",
                    fallback_reason="OpenRouter response choices were empty",
                    raw_text=None
                )
            except Exception as e:
                return LLMTrace(
                    provider="OpenRouter",
                    model_slug=target_model,
                    used_llm=False,
                    execution_path="deterministic",
                    fallback_reason=f"Network Exception ({str(e)})",
                    raw_text=None
                )

        elif provider_clean == "openai":
            target_model = model_slug or "gpt-4o-mini"
            if not self.openai_key:
                return LLMTrace(
                    provider="OpenAI",
                    model_slug=target_model,
                    used_llm=False,
                    execution_path="deterministic",
                    fallback_reason="OPENAI_API_KEY is missing or unset",
                    raw_text=None
                )

            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                resp = client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=250
                )
                content = resp.choices[0].message.content.strip()
                return LLMTrace(
                    provider="OpenAI",
                    model_slug=target_model,
                    used_llm=True,
                    execution_path="openai",
                    fallback_reason=None,
                    raw_text=content
                )
            except Exception as e:
                return LLMTrace(
                    provider="OpenAI",
                    model_slug=target_model,
                    used_llm=False,
                    execution_path="deterministic",
                    fallback_reason=f"OpenAI Exception ({str(e)})",
                    raw_text=None
                )

        return LLMTrace(
            provider=provider,
            model_slug=target_model,
            used_llm=False,
            execution_path="deterministic",
            fallback_reason="Unknown provider requested",
            raw_text=None
        )

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: str = "deterministic",
        model_slug: Optional[str] = None
    ) -> Optional[str]:
        """Convenience wrapper returning text string or None."""
        trace = self.generate_text_with_trace(prompt, system_prompt, provider, model_slug)
        return trace.raw_text
