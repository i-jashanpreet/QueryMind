"""
Tests for the Query Analyzer (Day 4).

Unit tests validate the Pydantic schema and JSON-cleaning logic.
Integration tests (marked with @pytest.mark.integration) call the live
Ollama server and the real /analyze endpoint.
"""

import json

import pytest

from app.schemas.analysis import QueryAnalysis
from app.services.query_analyzer import _clean_json_response, QueryAnalysisError


# ═══════════════════════════ UNIT — Pydantic model ═══════════════════════════


class TestQueryAnalysisModel:
    """Validate QueryAnalysis Pydantic model."""

    def test_minimal_valid(self):
        """Only the required fields (question + intent) should be needed."""
        analysis = QueryAnalysis(question="test", intent="lookup")
        assert analysis.question == "test"
        assert analysis.intent == "lookup"
        assert analysis.entities == []
        assert analysis.metric is None
        assert analysis.confidence == 0.5
        assert analysis.needs_clarification is False

    def test_full_valid(self):
        """All fields populated."""
        data = {
            "question": "Show me the top 5 products by revenue last month",
            "intent": "ranking",
            "entities": ["products", "order_items"],
            "metric": "revenue",
            "filters": {"category": "Electronics"},
            "time_range": "last_month",
            "limit": 5,
            "sort_order": "desc",
            "ambiguities": [],
            "missing_information": [],
            "confidence": 0.95,
            "needs_clarification": False,
        }
        analysis = QueryAnalysis(**data)
        assert analysis.intent == "ranking"
        assert analysis.limit == 5
        assert analysis.filters["category"] == "Electronics"

    def test_confidence_bounds_low(self):
        """Confidence below 0 should be rejected."""
        with pytest.raises(Exception):
            QueryAnalysis(question="q", intent="lookup", confidence=-0.1)

    def test_confidence_bounds_high(self):
        """Confidence above 1 should be rejected."""
        with pytest.raises(Exception):
            QueryAnalysis(question="q", intent="lookup", confidence=1.5)

    def test_serialization_round_trip(self):
        """model -> JSON -> model should be lossless."""
        original = QueryAnalysis(
            question="How many users?",
            intent="aggregation",
            entities=["users"],
            metric="count",
            confidence=0.9,
        )
        data = json.loads(original.model_dump_json())
        restored = QueryAnalysis(**data)
        assert original == restored


# ═══════════════════════════ UNIT — JSON cleaning ═══════════════════════════


class TestCleanJsonResponse:
    """Validate the _clean_json_response helper."""

    def test_plain_json(self):
        raw = '{"intent": "lookup"}'
        assert _clean_json_response(raw) == '{"intent": "lookup"}'

    def test_code_fenced_json(self):
        raw = '```json\n{"intent": "lookup"}\n```'
        assert json.loads(_clean_json_response(raw))["intent"] == "lookup"

    def test_code_fenced_no_lang(self):
        raw = '```\n{"intent": "lookup"}\n```'
        assert json.loads(_clean_json_response(raw))["intent"] == "lookup"

    def test_think_tags_stripped(self):
        raw = '<think>thinking...</think>\n{"intent": "lookup"}'
        cleaned = _clean_json_response(raw)
        assert "<think>" not in cleaned
        assert json.loads(cleaned)["intent"] == "lookup"

    def test_think_tags_with_code_fence(self):
        raw = '<think>hmm</think>\n```json\n{"intent": "lookup"}\n```'
        cleaned = _clean_json_response(raw)
        assert json.loads(cleaned)["intent"] == "lookup"

    def test_whitespace_only(self):
        assert _clean_json_response("   \n  ") == ""

    def test_malformed_json_passthrough(self):
        """Cleaning should not crash — just return the cleaned string."""
        raw = "this is not json at all"
        result = _clean_json_response(raw)
        assert result == "this is not json at all"


# ═════════════════════ UNIT — malformed LLM output ═════════════════════════


class TestMalformedLLMOutput:
    """Verify that malformed JSON from LLM does not crash the analyzer."""

    def test_pydantic_rejects_invalid_types(self):
        """entities must be a list, not a string."""
        with pytest.raises(Exception):
            QueryAnalysis(
                question="q",
                intent="lookup",
                entities="not_a_list",  # type: ignore
            )

    def test_missing_required_field(self):
        """question and intent are required."""
        with pytest.raises(Exception):
            QueryAnalysis(intent="lookup")  # type: ignore


# ═════════════════ INTEGRATION — live /analyze endpoint ═════════════════════


@pytest.mark.integration
class TestAnalyzeEndpointIntegration:
    """
    Integration tests that hit the real FastAPI + Ollama stack.

    Run with:  pytest -m integration -v

    These are SLOW (each call goes through Qwen3 inference).
    """

    @pytest.fixture(autouse=True)
    def _client(self):
        """Create a TestClient for the FastAPI app."""
        from fastapi.testclient import TestClient
        from app.main import app

        self.client = TestClient(app)

    # ─── clear queries ──────────────────────────────────────────────

    def test_aggregation_query(self):
        """'How many users are there?' → aggregation, users, count."""
        resp = self.client.post(
            "/analyze", json={"question": "How many users are there?"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "aggregation"
        assert "users" in data["entities"]
        assert data["metric"] == "count"
        assert data["needs_clarification"] is False
        assert data["confidence"] >= 0.7

    def test_ranking_query(self):
        """'Show me the top 5 products by revenue' → ranking."""
        resp = self.client.post(
            "/analyze",
            json={"question": "Show me the top 5 products by revenue"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "ranking"
        assert "products" in data["entities"]
        assert data["metric"] == "revenue"
        assert data["limit"] == 5
        assert data["sort_order"] == "desc"
        # Note: needs_clarification may vary — Qwen3 sometimes flags
        # "revenue" as ambiguous (total sales vs profit).  The core
        # structural analysis above is what matters.

    def test_filtering_query(self):
        """'Show me products from Electronics' → filtering."""
        resp = self.client.post(
            "/analyze",
            json={"question": "Show me products from Electronics"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] in ("filtering", "listing")
        assert "products" in data["entities"]
        assert data["needs_clarification"] is False

    def test_time_based_query(self):
        """'How much revenue did we make last month?' → time range."""
        resp = self.client.post(
            "/analyze",
            json={"question": "How much revenue did we make last month?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["time_range"] is not None
        assert data["metric"] is not None

    # ─── ambiguous query ────────────────────────────────────────────

    def test_ambiguous_query(self):
        """'Show me the best products' → needs_clarification = true."""
        resp = self.client.post(
            "/analyze",
            json={"question": "Show me the best products"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is True
        assert data["confidence"] <= 0.7
        assert len(data["ambiguities"]) > 0


# ═════════════ INTEGRATION — existing endpoints still work ═════════════════


@pytest.mark.integration
class TestExistingEndpoints:
    """Verify the pre-existing endpoints haven't broken."""

    @pytest.fixture(autouse=True)
    def _client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        self.client = TestClient(app)

    def test_root(self):
        resp = self.client.get("/")
        assert resp.status_code == 200
        assert "QueryMind" in resp.json()["message"]

    def test_health(self):
        resp = self.client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_db_health(self):
        resp = self.client.get("/db-health")
        assert resp.status_code == 200
        assert resp.json()["database"] == "connected"

    def test_docs(self):
        resp = self.client.get("/docs")
        assert resp.status_code == 200
