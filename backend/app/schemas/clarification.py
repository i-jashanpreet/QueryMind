from pydantic import BaseModel, Field

class ClarificationOption(BaseModel):
    label: str = Field(description="Human-readable label for the option.")
    value: str = Field(description="Machine-readable value for the option.")

class ClarificationResponse(BaseModel):
    needs_clarification: bool = Field(description="True if clarification is required.")
    question: str | None = Field(default=None, description="The clarification question to ask the user.")
    options: list[ClarificationOption] = Field(default_factory=list, description="Multiple choice options, if applicable.")
    reason: str | None = Field(default=None, description="Reason why clarification is needed.")
