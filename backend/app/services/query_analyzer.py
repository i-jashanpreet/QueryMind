"""
Query Analyzer — uses Qwen3 via Ollama to produce a structured
understanding of a natural-language question.

The analyzer does NOT generate SQL.  It outputs a QueryAnalysis
JSON object that describes what the user is asking.
"""

import json
import re

from sqlalchemy import Engine

from app.services import ollama_service
from app.services.schema_service import get_schema_context
from app.schemas.analysis import QueryAnalysis


# ──────────────────────── system prompt ────────────────────────

_SYSTEM_PROMPT_TEMPLATE = """\
You are a query-understanding engine for an e-commerce PostgreSQL database.

Your ONLY job is to analyze the user's natural-language question and return a single, valid JSON object describing what the user is asking.

RULES:
1.  Return ONLY a JSON object — no markdown, no code fences, no explanation, no SQL.
2.  NEVER generate SQL.
3.  Use ONLY entities (tables/columns) that exist in the schema below.
4.  Do NOT invent tables or columns.

JSON SCHEMA (every key is required):
{{
    "intent":               string — one of: "aggregation", "ranking", "listing", "lookup", "comparison", "trend", "filtering",
    "entities":             list[string] — database tables referenced (e.g. ["products", "orders"]),
    "metric":               string | null — the measure requested (e.g. "revenue", "count", "price", "rating"),
    "filters":              object — key/value filters (e.g. {{"category": "Electronics"}}),
    "time_range":           string | null — temporal scope (e.g. "last_month", "2024"),
    "limit":                integer | null — number of results requested,
    "sort_order":           string | null — "asc" or "desc",
    "ambiguities":          list[string] — parts of the question open to interpretation,
    "missing_information":  list[string] — information the user did not provide,
    "confidence":           float — 0.0 to 1.0, your confidence in the analysis,
    "needs_clarification":  boolean — true if the question is too ambiguous
}}

GUIDELINES FOR CONFIDENCE AND CLARIFICATION:
- If the question clearly maps to specific tables, columns, and a metric → confidence ≥ 0.85, needs_clarification = false.
- If the question uses vague terms like "best", "good", "popular" without specifying a metric → confidence ≤ 0.6, needs_clarification = true, and explain the ambiguity.
- If a filter value does not match any known data (e.g. a category that does not exist) → note it in missing_information.

DATABASE SCHEMA:
{schema}
"""


# ──────────────────────── response cleaning ────────────────────

_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

_CODE_FENCE_RE = re.compile(
    r"^```(?:json)?\s*\n?(.*?)```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def _clean_json_response(raw: str) -> str:
    """Strip <think> tags, markdown code fences, and whitespace."""
    cleaned = _THINK_TAG_RE.sub("", raw).strip()

    match = _CODE_FENCE_RE.match(cleaned)
    if match:
        cleaned = match.group(1).strip()

    # Handle fences that don't wrap the whole string
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return cleaned


# ──────────────────────── public API ───────────────────────────

class QueryAnalysisError(Exception):
    """Raised when query analysis fails."""
    pass


def analyze_query(question: str, engine: Engine) -> QueryAnalysis:
    """
    Analyze a natural-language *question* and return structured JSON.

    Workflow:
        1. Fetch the live database schema.
        2. Build a system prompt instructing the LLM to return JSON.
        3. Call Ollama.
        4. Clean the response.
        5. Parse and validate via Pydantic.

    Args:
        question: The user's natural-language question.
        engine:   SQLAlchemy engine (used for schema introspection).

    Returns:
        A validated QueryAnalysis object.

    Raises:
        QueryAnalysisError on any failure.
    """
    # 1 — schema
    try:
        schema_text = get_schema_context(engine)
    except Exception as exc:
        raise QueryAnalysisError(f"Failed to read database schema: {exc}") from exc

    # 2 — prompt
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(schema=schema_text)

    # 3 — LLM
    try:
        raw = ollama_service.generate(prompt=question, system=system_prompt)
    except Exception as exc:
        raise QueryAnalysisError(f"Ollama error: {exc}") from exc

    if not raw:
        raise QueryAnalysisError("Ollama returned an empty response.")

    # 4 — clean
    json_str = _clean_json_response(raw)

    if not json_str:
        raise QueryAnalysisError("No JSON could be extracted from the model response.")

    # 5 — parse + validate
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise QueryAnalysisError(
            f"LLM returned invalid JSON: {exc}\n\nRaw response:\n{json_str[:500]}"
        ) from exc

    try:
        analysis = QueryAnalysis(question=question, **data)
    except Exception as exc:
        raise QueryAnalysisError(
            f"Pydantic validation failed: {exc}\n\nParsed JSON:\n{json.dumps(data, indent=2)[:500]}"
        ) from exc

    return analysis
