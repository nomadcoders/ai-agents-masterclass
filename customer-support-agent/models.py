from pydantic import BaseModel
from typing import Optional


class UserAccountContext(BaseModel):

    customer_id: int
    name: str
    tier: str = "basic"
    email: Optional[str] = None  # premium entreprise


class InputGuardRailOutput(BaseModel):

    is_off_topic: bool
    reason: str
