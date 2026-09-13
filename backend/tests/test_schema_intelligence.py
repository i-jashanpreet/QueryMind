from app.database import engine
from app.schemas.analysis import QueryAnalysis
from app.services.schema_intelligence import SchemaIntelligence


def test_schema_intelligence_revenue_metric():
    analysis = QueryAnalysis(
        question="Show me the top 5 products by revenue",
        intent="ranking",
        entities=["products"],
        metric="revenue"
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    # Revenue needs orders, order_items, and products
    assert "products" in table_names
    assert "order_items" in table_names
    assert "orders" in table_names
    # Shouldn't include unrelated tables
    assert "reviews" not in table_names
    assert "users" not in table_names


def test_schema_intelligence_units_sold_metric():
    analysis = QueryAnalysis(
        question="How many units of each product were sold?",
        intent="aggregation",
        entities=["products"],
        metric="units_sold"
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    assert "products" in table_names
    assert "order_items" in table_names
    assert "orders" not in table_names


def test_schema_intelligence_rating_metric():
    analysis = QueryAnalysis(
        question="Best products by rating",
        intent="ranking",
        entities=["products"],
        metric="rating"
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    assert "products" in table_names
    assert "reviews" in table_names
    assert "orders" not in table_names


def test_schema_intelligence_entity_mapping():
    analysis = QueryAnalysis(
        question="How many users are there?",
        intent="aggregation",
        entities=["customers"],
        metric="count"
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    assert "users" in table_names
    assert "orders" not in table_names


def test_schema_intelligence_unknown_metric_and_entity():
    """Fallback to full schema if we have no matches."""
    analysis = QueryAnalysis(
        question="What is the correlation between x and y?",
        intent="aggregation",
        entities=["something_unknown"],
        metric="something_unknown"
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    assert "users" in table_names
    assert "products" in table_names
    assert "orders" in table_names


def test_schema_intelligence_relationships_filtered():
    """Ensure that we only keep relationships pointing to included tables."""
    analysis = QueryAnalysis(
        question="Show me products",
        intent="listing",
        entities=["products"]
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    table_names = {t.name for t in relevant_schema.tables}
    
    # It includes products because of entity match
    assert "products" in table_names
    assert "categories" not in table_names
    
    # Make sure products doesn't have a relationship pointing to categories
    products_table = next(t for t in relevant_schema.tables if t.name == "products")
    rel_tables = {r.to_table for r in products_table.relationships}
    assert "categories" not in rel_tables


def test_schema_intelligence_to_llm_string():
    analysis = QueryAnalysis(
        question="How many users?",
        intent="aggregation",
        entities=["users"]
    )
    relevant_schema = SchemaIntelligence.get_relevant_schema(analysis, engine)
    schema_str = relevant_schema.to_llm_string()
    
    assert "Table: users" in schema_str
    assert "- id (INTEGER) [PK]" in schema_str
    assert "Table: orders" not in schema_str
