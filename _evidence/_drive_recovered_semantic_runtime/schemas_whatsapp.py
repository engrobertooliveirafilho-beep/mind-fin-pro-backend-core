
from pydantic import BaseModel
from typing import Any, Optional, Dict

class WhatsAppPayload(BaseModel):
    sender_id: str
    message: Optional[str] = ""
    timestamp: str
    media_type: str = "text"
    media_url: Optional[str] = None
    provider_payload: Dict[str, Any] = {}
