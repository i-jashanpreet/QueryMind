import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
class TestQueryIntegration:

    def test_query_top_5_products_revenue(self):
        """TEST 1: Clear query -> SQL generated, results returned."""
        resp = client.post("/query", json={"question": "Show me the top 5 products by revenue"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is False
        assert data["clarification"] is None
        assert data["sql"] is not None
        assert data["results"] is not None
        assert len(data["results"]) <= 5

    def test_query_best_products(self):
        """TEST 2: Ambiguous query -> needs clarification, no SQL."""
        resp = client.post("/query", json={"question": "Show me the best products"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is True
        assert data["clarification"] is not None
        assert len(data["clarification"]["options"]) > 1
        assert data["sql"] is None
        assert data["results"] is None

    def test_query_how_many_users(self):
        """TEST 3: Clear query -> no clarification, SQL generated."""
        resp = client.post("/query", json={"question": "How many users?"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is False
        assert data["sql"] is not None
        assert data["results"] is not None
        # Could check that results has a count field

    def test_query_show_me_sales(self):
        """TEST 4: Missing time range -> clarification required."""
        resp = client.post("/query", json={"question": "Show me sales"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is True
        assert data["clarification"] is not None
        assert data["sql"] is None
        assert data["results"] is None

    def test_query_products_priced_above_1000(self):
        """TEST 5: Filters clear -> no clarification."""
        resp = client.post("/query", json={"question": "Show products priced above 1000"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is False
        assert data["sql"] is not None
        assert data["results"] is not None


class TestAmbiguousQuerySecurity:
    """Explicitly verify that SQL execution does not occur for ambiguous queries."""

    @patch("app.main.generate_sql")
    @patch("sqlalchemy.orm.Session.execute")
    def test_ambiguous_query_skips_sql_execution(self, mock_db_execute, mock_generate_sql):
        resp = client.post("/query", json={"question": "Show me the best products"})
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify it stopped at clarification
        assert data["needs_clarification"] is True
        assert data["sql"] is None
        assert data["results"] is None
        
        # Verify generate_sql and DB execute were never called
        mock_generate_sql.assert_not_called()
        mock_db_execute.assert_not_called()

class TestConversationFlow:
    """Tests the Day 7 conversation state and resolution flow."""
    
    def test_conversation_resolution_by_value(self):
        # 1. Initiate conversation
        resp1 = client.post("/query", json={"question": "Show me the best products"})
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["needs_clarification"] is True
        conv_id = data1.get("conversation_id")
        assert conv_id is not None
        
        # 2. Resolve with exact value
        resp2 = client.post("/query", json={
            "conversation_id": conv_id,
            "question": "revenue"
        })
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["needs_clarification"] is False
        assert data2["sql"] is not None
        assert data2["conversation_id"] == conv_id

    def test_conversation_resolution_by_label_case_insensitive(self):
        # 1. Initiate
        resp1 = client.post("/query", json={"question": "Show me the top products"})
        assert resp1.status_code == 200
        conv_id = resp1.json()["conversation_id"]
        
        # 2. Resolve with case-insensitive label
        resp2 = client.post("/query", json={
            "conversation_id": conv_id,
            "question": "HIGHEST RATING"
        })
        assert resp2.status_code == 200
        assert resp2.json()["needs_clarification"] is False
        assert resp2.json()["sql"] is not None

    def test_invalid_answer_returns_clarification(self):
        # 1. Initiate
        resp1 = client.post("/query", json={"question": "Show me the best products"})
        conv_id = resp1.json()["conversation_id"]
        
        # 2. Invalid answer
        resp2 = client.post("/query", json={
            "conversation_id": conv_id,
            "question": "purple bananas"
        })
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["needs_clarification"] is True
        assert data2["clarification"] is not None
        assert data2["sql"] is None

    @patch("app.main.generate_sql")
    @patch("sqlalchemy.orm.Session.execute")
    def test_invalid_answer_skips_execution(self, mock_db_execute, mock_generate_sql):
        resp1 = client.post("/query", json={"question": "Show me the best products"})
        conv_id = resp1.json()["conversation_id"]
        
        resp2 = client.post("/query", json={
            "conversation_id": conv_id,
            "question": "purple bananas"
        })
        
        mock_generate_sql.assert_not_called()
        mock_db_execute.assert_not_called()
