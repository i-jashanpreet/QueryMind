import datetime
from pydantic import BaseModel, Field

from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse

class ConversationState(BaseModel):
    """Stores the state of a user's query clarification conversation."""
    conversation_id: str = Field(description="Unique ID for the conversation.")
    original_question: str = Field(description="The user's initial question.")
    query_analysis: QueryAnalysis = Field(description="The structured analysis of the original question.")
    clarification: ClarificationResponse | None = Field(default=None, description="The last clarification response sent to the user.")
    clarification_type: str | None = Field(default=None, description="The type of ambiguity (e.g. 'ranking_metric', 'time_range', 'entity').")
    pending_clarification: bool = Field(default=False, description="True if waiting for user's answer.")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
