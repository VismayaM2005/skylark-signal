import os
from typing import Optional

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """Application configuration for Skylark Signal."""
    
    def __init__(self):
        # monday.com Configuration
        self.monday_api_token: Optional[str] = os.getenv("MONDAY_API_TOKEN")
        self.monday_deals_board_id: Optional[str] = os.getenv("MONDAY_DEALS_BOARD_ID")
        self.monday_work_orders_board_id: Optional[str] = os.getenv("MONDAY_WORK_ORDERS_BOARD_ID")
        
        self.monday_api_url: str = os.getenv("MONDAY_API_URL", "https://api.monday.com/v2")
        self.monday_api_timeout: int = int(os.getenv("MONDAY_API_TIMEOUT", "30"))
        self.monday_max_retries: int = int(os.getenv("MONDAY_MAX_RETRIES", "3"))
        self.monday_cache_ttl: int = int(os.getenv("MONDAY_CACHE_TTL", "300"))

        # OpenRouter & OpenAI Configuration
        self.openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_http_referer: str = os.getenv("OPENROUTER_HTTP_REFERER", "https://github.com/skylark-signal")
        self.openrouter_app_title: str = os.getenv("OPENROUTER_APP_TITLE", "Skylark Signal")
        
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

        # Analytics & Time Threshold Options
        self.stale_deal_days: int = int(os.getenv("STALE_DEAL_DAYS", "60"))
        self.overdue_wo_days: int = int(os.getenv("OVERDUE_WO_DAYS", "0"))
        self.reference_date_iso: Optional[str] = os.getenv("REFERENCE_DATE_ISO", "2026-07-27")
        
    @property
    def masked_token(self) -> str:
        """Returns a masked representation of the monday API token for logging safety."""
        if not self.monday_api_token:
            return "UNSET"
        if len(self.monday_api_token) <= 8:
            return "***"
        return f"***{self.monday_api_token[-4:]}"

    @property
    def masked_openrouter_token(self) -> str:
        """Returns a masked representation of the OpenRouter API key."""
        if not self.openrouter_api_key:
            return "UNSET"
        if len(self.openrouter_api_key) <= 8:
            return "***"
        return f"***{self.openrouter_api_key[-4:]}"

    @property
    def available_llm_providers(self) -> list:
        """
        Returns the list of LLM provider names to show in the UI.

        Rules:
          - "Deterministic" is always present (no key required).
          - "OpenRouter" is always listed; the user can paste a key in the sidebar.
          - "OpenAI" is included ONLY when OPENAI_API_KEY is set in the environment.
        """
        providers = ["Deterministic", "OpenRouter"]
        if self.openai_api_key:
            providers.append("OpenAI")
        return providers

    def __repr__(self) -> str:
        return (
            f"Config("
            f"monday_api_url='{self.monday_api_url}', "
            f"openrouter_base_url='{self.openrouter_base_url}', "
            f"monday_token='{self.masked_token}', "
            f"openrouter_token='{self.masked_openrouter_token}', "
            f"providers={self.available_llm_providers})"
        )

# Global singleton configuration instance
config = Config()
