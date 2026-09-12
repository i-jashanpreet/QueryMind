"""
Schema context generator — introspects the PostgreSQL database via
SQLAlchemy metadata and produces a text description the LLM can consume.
"""

from sqlalchemy import inspect, Engine


def get_schema_context(engine: Engine) -> str:
    """
    Build a human-readable schema description from the live database.

    Includes:
        • Table names
        • Column names + types
        • Primary keys
        • Foreign-key relationships

    Returns:
        A multi-line string suitable for inclusion in an LLM prompt.
    """
    inspector = inspect(engine)
    lines: list[str] = []

    for table_name in sorted(inspector.get_table_names()):
        lines.append(f"Table: {table_name}")

        # Columns
        columns = inspector.get_columns(table_name)
        pk_cols = inspector.get_pk_constraint(table_name)
        pk_names: set[str] = set(pk_cols.get("constrained_columns", []))

        for col in columns:
            col_name: str = col["name"]
            col_type: str = str(col["type"])
            nullable: bool = col.get("nullable", True)

            parts = [f"  - {col_name} ({col_type})"]
            if col_name in pk_names:
                parts.append("[PK]")
            if not nullable:
                parts.append("[NOT NULL]")
            lines.append(" ".join(parts))

        # Foreign keys
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            local_cols = ", ".join(fk["constrained_columns"])
            ref_table = fk["referred_table"]
            ref_cols = ", ".join(fk["referred_columns"])
            lines.append(
                f"  FK: {local_cols} -> {ref_table}({ref_cols})"
            )

        lines.append("")  # blank line between tables

    return "\n".join(lines)
