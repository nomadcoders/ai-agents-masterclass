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


class TechnicalOutputGuardRailOutput(BaseModel):

    contains_off_topic: bool
    contains_billing_data: bool
    contains_account_data: bool
    reason: str


class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str
