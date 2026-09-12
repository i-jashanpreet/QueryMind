"""
Pydantic models for the /analyze endpoint — structured query understanding.
"""

from pydantic import BaseModel, Field


class QueryAnalysis(BaseModel):
    """Structured representation of an analyzed user question."""

    question: str = Field(
        description="The original user question.",
    )
    intent: str = Field(
        description=(
            "High-level intent, e.g. 'aggregation', 'ranking', 'listing', "
            "'lookup', 'comparison', 'trend'."
        ),
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Database tables / domain objects referenced (e.g. ['products', 'orders']).",
    )
    metric: str | None = Field(
        default=None,
        description="Requested measure — e.g. 'revenue', 'count', 'price', 'rating'.",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Key-value filters extracted from the question (e.g. {'category': 'Electronics'}).",
    )
    time_range: str | None = Field(
        default=None,
        description="Temporal scope if mentioned — e.g. 'last_month', '2024', 'last_7_days'.",
    )
    limit: int | None = Field(
        default=None,
        description="Requested number of results (e.g. 5, 10).",
    )
    sort_order: str | None = Field(
        default=None,
        description="'asc' or 'desc' if a ranking/ordering was requested.",
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="Aspects of the question that are open to interpretation.",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Information the user did not supply that would be needed for a precise query.",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Estimated confidence that the analysis is correct (0.0–1.0).",
    )
    needs_clarification: bool = Field(
        default=False,
        description="True when the question is too ambiguous to generate reliable SQL.",
    )
