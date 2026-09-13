"""
Schema context generator — introspects the PostgreSQL database via
SQLAlchemy metadata and produces a text description the LLM can consume.
"""

from sqlalchemy import inspect, Engine
from app.schemas.schema_context import SchemaColumn, SchemaTable, SchemaRelationship, RelevantSchemaContext

def get_structured_schema(engine: Engine) -> RelevantSchemaContext:
    """
    Build a structured schema description from the live database.
    """
    inspector = inspect(engine)
    tables = []

    for table_name in sorted(inspector.get_table_names()):
        table = SchemaTable(name=table_name)
        
        # Columns
        columns = inspector.get_columns(table_name)
        pk_cols = inspector.get_pk_constraint(table_name)
        pk_names: set[str] = set(pk_cols.get("constrained_columns", []))

        for col in columns:
            col_name: str = col["name"]
            col_type: str = str(col["type"])
            nullable: bool = col.get("nullable", True)
            is_pk: bool = col_name in pk_names

            table.columns.append(SchemaColumn(
                name=col_name,
                data_type=col_type,
                nullable=nullable,
                is_primary_key=is_pk,
                is_foreign_key=False  # updated below
            ))

        # Foreign keys
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            local_cols = fk["constrained_columns"]
            ref_table = fk["referred_table"]
            ref_cols = fk["referred_columns"]
            
            # Since our model assumes single-column foreign keys for simplicity (or we can join them)
            # The existing code did: local_cols = ", ".join(fk["constrained_columns"])
            # Let's map each constrained column to a relationship
            for local_col, ref_col in zip(local_cols, ref_cols):
                table.relationships.append(SchemaRelationship(
                    from_table=table_name,
                    from_column=local_col,
                    to_table=ref_table,
                    to_column=ref_col
                ))
                # Update the column's is_foreign_key flag
                for c in table.columns:
                    if c.name == local_col:
                        c.is_foreign_key = True

        tables.append(table)

    return RelevantSchemaContext(tables=tables)


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
    return get_structured_schema(engine).to_llm_string()
