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
