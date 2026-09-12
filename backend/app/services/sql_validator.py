"""
SQL validator — uses SQLGlot to parse and enforce read-only SELECT queries.
"""

import sqlglot
from sqlglot.errors import ParseError

# Statement types we must reject
_FORBIDDEN_TYPES: set[str] = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "MERGE",
    "COMMAND",
}


class SQLValidationError(Exception):
    """Raised when the generated SQL fails validation."""
    pass


def validate_sql(sql: str) -> str:
    """
    Parse *sql* with SQLGlot and enforce:

    1. Exactly one statement.
    2. The statement must be a SELECT (or a read-only expression).
    3. No forbidden DDL / DML keywords.

    Args:
        sql: The raw SQL string returned by the LLM.

    Returns:
        The validated SQL string (unchanged).

    Raises:
        SQLValidationError on any policy violation.
    """
    if not sql or not sql.strip():
        raise SQLValidationError("Empty SQL received from the model.")

    # ------------------------------------------------------------------ parse
    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except ParseError as exc:
        raise SQLValidationError(f"SQL parse error: {exc}") from exc

    # Filter out None / empty parses
    statements = [s for s in statements if s is not None]

    if len(statements) == 0:
        raise SQLValidationError("No valid SQL statement found.")

    if len(statements) > 1:
        raise SQLValidationError(
            "Multiple SQL statements detected. Only a single SELECT is allowed."
        )

    stmt = statements[0]

    # -------------------------------------------------------- type check
    stmt_type: str = stmt.key.upper() if hasattr(stmt, "key") else ""

    if stmt_type in _FORBIDDEN_TYPES:
        raise SQLValidationError(
            f"Forbidden SQL statement type: {stmt_type}. Only SELECT queries are allowed."
        )

    if stmt_type != "SELECT":
        # Extra caution: anything that isn't explicitly SELECT is refused
        raise SQLValidationError(
            f"Only SELECT queries are allowed, got: {stmt_type or 'unknown'}."
        )

    # ---- walk the tree for any forbidden nested nodes (e.g. sub-statements)
    upper_sql = sql.upper()
    for keyword in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
                    "TRUNCATE", "CREATE", "GRANT", "REVOKE"):
        # Only check for the keyword as a standalone token
        # (avoids false positives inside identifiers or strings)
        if keyword in upper_sql:
            # Use sqlglot to be precise: walk the AST
            for node in stmt.walk():
                node_key = getattr(node, "key", "").upper()
                if node_key in _FORBIDDEN_TYPES:
                    raise SQLValidationError(
                        f"Forbidden SQL construct found: {node_key}."
                    )

    return sql
