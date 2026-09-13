from sqlalchemy import Engine

from app.schemas.analysis import QueryAnalysis
from app.schemas.schema_context import RelevantSchemaContext, SchemaTable, SchemaRelationship
from app.services.schema_service import get_structured_schema


class SchemaIntelligence:
    """
    Determines relevant database schema subsets for a given query analysis.
    Provides a deterministic baseline to avoid passing the entire schema
    to the LLM when unnecessary.
    """

    METRIC_TABLE_MAP: dict[str, set[str]] = {
        "revenue": {"orders", "order_items", "products"},
        "units_sold": {"order_items", "products"},
        "rating": {"reviews", "products"},
        "profit": {"products", "order_items"},
    }

    ENTITY_TABLE_MAP: dict[str, str] = {
        "product": "products",
        "products": "products",
        "user": "users",
        "users": "users",
        "customer": "users",
        "customers": "users",
        "order": "orders",
        "orders": "orders",
        "category": "categories",
        "categories": "categories",
        "review": "reviews",
        "reviews": "reviews",
    }

    @classmethod
    def get_relevant_schema(cls, analysis: QueryAnalysis, engine: Engine) -> RelevantSchemaContext:
        """
        Produce a minimized RelevantSchemaContext based on deterministic mapping.
        If we cannot determine a confident subset, returns the full schema.
        """
        full_schema = get_structured_schema(engine)
        all_table_names = {t.name for t in full_schema.tables}

        required_tables: set[str] = set()

        # 1. Add tables by metric
        if analysis.metric:
            metric_lower = analysis.metric.lower()
            if metric_lower in cls.METRIC_TABLE_MAP:
                required_tables.update(cls.METRIC_TABLE_MAP[metric_lower])

        # 2. Add tables by entities
        if analysis.entities:
            for entity in analysis.entities:
                e_lower = entity.lower()
                if e_lower in cls.ENTITY_TABLE_MAP:
                    required_tables.add(cls.ENTITY_TABLE_MAP[e_lower])
                elif e_lower in all_table_names:
                    required_tables.add(e_lower)

        # 3. Add tables implicitly needed for filtering by time range
        # If time range is present, we likely need the table with the date/timestamp
        # But this can be table specific. Usually 'orders', 'users', 'reviews', 'payments'.
        # Since we don't know which one specifically, if required_tables is not empty and time_range is present,
        # we make sure the tables with timestamps are included IF they relate to the entity.
        # Actually, for simplicity, we don't aggressively add tables just for time_range,
        # because the metric mapping usually covers the core transaction table (e.g. orders).

        # If we failed to find any required tables, return the full schema safely
        if not required_tables:
            return full_schema

        # Filter the full schema to only include required_tables
        relevant_tables = []
        for table in full_schema.tables:
            if table.name in required_tables:
                # Create a new table object with filtered relationships
                filtered_relationships = [
                    rel for rel in table.relationships
                    if rel.to_table in required_tables
                ]
                
                # We could filter columns here, but to avoid breaking SQL generation with missing fields,
                # we keep all columns of the relevant tables as per the prompt's instruction to NOT aggressively remove columns.
                
                relevant_table = SchemaTable(
                    name=table.name,
                    columns=table.columns,
                    relationships=filtered_relationships
                )
                relevant_tables.append(relevant_table)

        return RelevantSchemaContext(tables=relevant_tables)
