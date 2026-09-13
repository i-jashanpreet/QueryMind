from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse, ClarificationOption
from app.services.clarification_engine import ClarificationEngine


def test_clear_ranking_query():
    """1. Clear ranking query -> no clarification"""
    analysis = QueryAnalysis(
        question="Show me the top 5 products by revenue",
        intent="ranking",
        entities=["products"],
        metric="revenue",
        limit=5,
        sort_order="desc",
        needs_clarification=False
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False
    assert resp.question is None
    assert len(resp.options) == 0


def test_clear_aggregation():
    """2. Clear aggregation -> no clarification"""
    analysis = QueryAnalysis(
        question="How many users?",
        intent="aggregation",
        entities=["users"],
        metric="count",
        needs_clarification=False
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False


def test_ambiguous_best_products():
    """3. Ambiguous best products -> clarification -> multiple choice (2-5 options)"""
    analysis = QueryAnalysis(
        question="Show me the best products",
        intent="ranking",
        entities=["products"],
        metric=None,
        ambiguities=["What does best mean?"],
        missing_information=["metric"],
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert len(resp.options) > 1
    assert len(resp.options) <= 5
    assert resp.options[0].label == "Highest revenue"


def test_missing_time_range():
    """4. Missing time range -> clarification -> multiple choice"""
    analysis = QueryAnalysis(
        question="Show me sales",
        intent="aggregation",
        entities=["orders"],
        metric="sales",
        missing_information=["time period"],
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert "time period" in resp.question.lower()
    assert len(resp.options) == 4
    assert resp.options[0].value == "today"


def test_missing_entity():
    """5. Missing entity -> clarification -> open-ended"""
    analysis = QueryAnalysis(
        question="Show me the revenue",
        intent="aggregation",
        entities=[],
        metric="revenue",
        missing_information=["entity"],
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert "entity" in resp.question.lower()
    assert len(resp.options) == 0


def test_clear_filtered_query():
    """6. Already clear filtered query -> no clarification"""
    analysis = QueryAnalysis(
        question="Show products priced above 1000",
        intent="filtering",
        entities=["products"],
        metric=None,
        filters={"price": "> 1000"},
        needs_clarification=False
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False


def test_analyzer_explicitly_says_clarification_required():
    """7. Analyzer explicitly says clarification required -> engine respects it"""
    analysis = QueryAnalysis(
        question="Show me something",
        intent="lookup",
        entities=["users"],
        ambiguities=["meaning is completely unknown"],
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert len(resp.options) == 0
    assert resp.reason == "meaning is completely unknown"


def test_empty_ambiguity_missing_information():
    """8. Empty ambiguity/missing information -> safe behavior"""
    analysis = QueryAnalysis(
        question="Show me",
        intent="lookup",
        entities=["users"],
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert resp.reason == "The query is ambiguous."
    assert len(resp.options) == 0


def test_never_return_more_than_5_options():
    """9. Never return more than 5 options & 10. Every option has non-empty label and value"""
    analysis = QueryAnalysis(
        question="Show me the best products",
        intent="ranking",
        entities=["products"],
        metric=None,
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is True
    assert len(resp.options) <= 5
    for opt in resp.options:
        assert opt.label != ""
        assert opt.value != ""


def test_explicit_ranking_metric_revenue_override():
    """Regression test: explicit ranking metric 'revenue' does not trigger clarification."""
    analysis = QueryAnalysis(
        question="Show me the top 5 products by revenue",
        intent="ranking",
        entities=["products"],
        metric="revenue",
        limit=5,
        sort_order="desc",
        needs_clarification=True  # Simulate LLM false positive
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False

def test_explicit_ranking_metric_units_sold_override():
    """Regression test: explicit ranking metric 'units sold' does not trigger clarification."""
    analysis = QueryAnalysis(
        question="Show me the top products by units sold",
        intent="ranking",
        entities=["products"],
        metric="units_sold",
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False

def test_explicit_ranking_metric_rating_override():
    """Regression test: explicit ranking metric 'rating' does not trigger clarification."""
    analysis = QueryAnalysis(
        question="Show me the top products by rating",
        intent="ranking",
        entities=["products"],
        metric="rating",
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False

def test_explicit_ranking_metric_profit_override():
    """Regression test: explicit ranking metric 'profit' does not trigger clarification."""
    analysis = QueryAnalysis(
        question="Show me the top products by profit",
        intent="ranking",
        entities=["products"],
        metric="profit",
        needs_clarification=True
    )
    resp = ClarificationEngine.generate(analysis)
    assert resp.needs_clarification is False
