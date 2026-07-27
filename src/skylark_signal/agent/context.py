import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

KNOWN_SECTORS = ["Mining", "Powerline", "Renewables", "Solar", "Infrastructure", "Energy", "Oil & Gas"]

class ConversationTurn(BaseModel):
    """Represents a single turn in a multi-turn conversation."""
    user_query: str
    intent: str
    sector: Optional[str] = None
    response_summary: str

class ConversationContext(BaseModel):
    """
    Maintains multi-turn conversational memory and filter context across query turns.
    """
    active_intent: Optional[str] = None
    active_sector: Optional[str] = None
    active_owner: Optional[str] = None
    active_status_filter: Optional[str] = None
    turns_count: int = 0
    history: List[ConversationTurn] = Field(default_factory=list)

    def extract_sector_from_text(self, text: str) -> Optional[str]:
        """Extracts known sector name from query text if explicitly mentioned."""
        if not text:
            return None
        for sec in KNOWN_SECTORS:
            if re.search(r'\b' + re.escape(sec) + r'\b', text, re.IGNORECASE):
                return sec
        return None

    def process_query_turn(self, query: str, intent: str, response_summary: str = "") -> "ConversationContext":
        """
        Updates conversational context with details from the latest turn.
        """
        explicit_sector = self.extract_sector_from_text(query)
        if explicit_sector:
            self.active_sector = explicit_sector

        self.active_intent = intent
        self.turns_count += 1

        self.history.append(ConversationTurn(
            user_query=query,
            intent=intent,
            sector=self.active_sector,
            response_summary=response_summary
        ))
        return self

    def clear(self):
        """Clears conversational memory."""
        self.active_intent = None
        self.active_sector = None
        self.active_owner = None
        self.active_status_filter = None
        self.turns_count = 0
        self.history = []
