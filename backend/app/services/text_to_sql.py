"""
Text-to-SQL service — orchestrates schema context, LLM prompt
construction, Ollama inference, response cleaning, and SQL validation.
"""

import re

from sqlalchemy import Engine

from app.services import ollama_service
from app.services.schema_service import get_schema_context
from app.services.sql_validator import validate_sql, SQLValidationError

# ------------------------------------------------------------------ prompt

_SYSTEM_PROMPT_TEMPLATE = """\
You are a PostgreSQL SQL expert.
Your ONLY job is to convert a natural-language question into a single, valid PostgreSQL SELECT query.

RULES:
1. Output ONLY the SQL query — no explanations, no markdown, no code fences.
2. Generate read-only queries ONLY (SELECT).
3. NEVER generate DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE statements.
4. Use ONLY the tables and columns listed in the schema below.
5. Do NOT invent tables or columns that are not in the schema.
6. Use proper JOINs based on the foreign-key relationships provided.
7. Return valid PostgreSQL syntax.
8. End the query with a semicolon.
9. Do NOT wrap the output in markdown code fences (``` or ```sql).
10. Do NOT include any text before or after the SQL.
11. If you use aggregate functions (e.g. SUM, AVG), you MUST include ALL non-aggregate columns from the SELECT clause in your GROUP BY clause to avoid GroupingErrors.

DATABASE SCHEMA:
{schema}
"""


# ------------------------------------------------------------------ helpers

_CODE_FENCE_RE = re.compile(
    r"^```(?:sql)?\s*\n?(.*?)```\s*$",
    re.DOTALL | re.IGNORECASE,
)

_THINK_TAG_RE = re.compile(
    r"<think>.*?</think>",
    re.DOTALL | re.IGNORECASE,
)


def _clean_response(raw: str) -> str:
    """Strip markdown code fences, <think> tags, and surrounding whitespace."""
    # Remove <think>...</think> blocks (Qwen3 thinking mode)
    cleaned = _THINK_TAG_RE.sub("", raw).strip()

    # Remove markdown code fences
    match = _CODE_FENCE_RE.match(cleaned)
    if match:
        cleaned = match.group(1).strip()

    # Also handle fences that don't cover the whole string
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Drop first and last lines if they are fences
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return cleaned


# ------------------------------------------------------------------ public

class TextToSQLError(Exception):
    """Raised when the Text-to-SQL pipeline fails."""
    pass


from app.schemas.analysis import QueryAnalysis
from app.services.schema_intelligence import SchemaIntelligence

def generate_sql(question: str, engine: Engine, analysis: QueryAnalysis | None = None) -> str:
    """
    Convert a natural-language *question* into a validated PostgreSQL
    SELECT query.

    Workflow:
        1. Introspect the database schema.
        2. Build the LLM system prompt.
        3. Call Ollama.
        4. Clean the response.
        5. Validate the SQL via SQLGlot.

    Args:
        question: The user's natural-language question.
        engine:   The SQLAlchemy engine (used for schema introspection).
        analysis: Optional structured QueryAnalysis to guide the generation (used after clarification).

    Returns:
        A validated SQL SELECT string.

    Raises:
        TextToSQLError on any failure (Ollama unreachable, invalid SQL, etc.).
    """
    # 1 — schema
    try:
        if analysis:
            relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
            schema_text = relevant_schema.to_llm_string()
        else:
            schema_text = get_schema_context(engine)
    except Exception as exc:
        raise TextToSQLError(f"Failed to read database schema: {exc}") from exc

    # 2 — prompt
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(schema=schema_text)
    
    if analysis:
        system_prompt += "\n\nADDITIONAL CONSTRAINTS FROM ANALYSIS:"
        if analysis.metric:
            system_prompt += f"\n- Ensure the query calculates or orders by the metric: '{analysis.metric}'"
        if analysis.time_range:
            system_prompt += f"\n- Ensure the query filters by the time range: '{analysis.time_range}'"
        if analysis.entities:
            system_prompt += f"\n- Ensure the query focuses on these entities: {', '.join(analysis.entities)}"

    # 3 — LLM
    try:
        raw_response = ollama_service.generate(prompt=question, system=system_prompt)
    except Exception as exc:
        raise TextToSQLError(f"Ollama error: {exc}") from exc

    if not raw_response:
        raise TextToSQLError("Ollama returned an empty response.")

    # 4 — clean
    sql = _clean_response(raw_response)

    if not sql:
        raise TextToSQLError("No SQL could be extracted from the model response.")

    # 5 — validate
    try:
        validate_sql(sql)
    except SQLValidationError as exc:
        raise TextToSQLError(f"SQL validation failed: {exc}") from exc

    return sql
