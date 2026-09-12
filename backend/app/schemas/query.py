"""
Pydantic models for the /query endpoint.
"""

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Body for POST /query."""
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="A natural-language question about the database.",
        examples=["Show me the top 5 products by revenue"],
    )


from app.schemas.clarification import ClarificationResponse

class QueryResponse(BaseModel):
    """Response from POST /query."""
    question: str
    needs_clarification: bool = False
    clarification: ClarificationResponse | None = None
    sql: str | None = None
    results: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    """Returned when the pipeline encounters an error."""
    error: str
    detail: str | None = None
