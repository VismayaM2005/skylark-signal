from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class OpenRouterModel(BaseModel):
    """Represents a model returned by the OpenRouter models API."""
    id: str = Field(..., description="Model slug ID e.g. openai/gpt-4o-mini")
    name: str = Field(..., description="Human readable model name")
    description: Optional[str] = Field(None, description="Model description if available")
    context_length: Optional[int] = Field(None, description="Context window size in tokens")

class LLMProviderConfig(BaseModel):
    """Configuration for LLM provider execution."""
    provider_name: str = Field("deterministic", description="Provider: deterministic, openrouter, or openai")
    model_slug: Optional[str] = Field(None, description="Selected model slug")
    api_key: Optional[str] = Field(None, description="API Key")
    base_url: Optional[str] = Field(None, description="API Base URL")

class LLMTrace(BaseModel):
    """Structured debug and proof trace of an LLM generation execution."""
    provider: str = Field("deterministic", description="Provider requested")
    model_slug: str = Field("none", description="Model slug requested")
    used_llm: bool = Field(False, description="True if remote LLM API successfully generated output")
    execution_path: str = Field("deterministic", description="Code path executed: openrouter, openai, or deterministic")
    fallback_reason: Optional[str] = Field(None, description="Reason why deterministic fallback was used, if any")
    raw_text: Optional[str] = Field(None, description="Raw generated text from LLM")
