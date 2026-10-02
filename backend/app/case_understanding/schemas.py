from pydantic import BaseModel, Field


class UserCase(BaseModel):
    has_case_context: bool = False
    age: int | None = None
    has_existing_policy: bool | None = None
    policy_years: int | None = None
    action_considered: str | None = None
    cash_value_known: bool | None = None
    premium_status: str | None = None
    region: str | None = None
    asks_personal_advice: bool = False
    extracted_facts: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
