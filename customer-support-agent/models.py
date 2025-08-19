from pydantic import BaseModel


class UserAccountContext(BaseModel):

    customer_id: int
    name: str
    tier: str = "basic"  # premium entreprise
