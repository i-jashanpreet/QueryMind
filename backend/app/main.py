from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, engine
from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.analysis import QueryAnalysis
from app.services.text_to_sql import generate_sql, TextToSQLError
from app.services.query_analyzer import analyze_query, QueryAnalysisError

app = FastAPI(title="QueryMind API")


# ───────────────────────────── health ─────────────────────────────


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "QueryMind API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/db-health")
def db_health(db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Check that FastAPI can reach PostgreSQL.
    Returns 503 if the database is unreachable.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {exc}",
        )


# ───────────────────────────── analyze ────────────────────────────


@app.post("/analyze", response_model=QueryAnalysis)
def analyze(body: QueryRequest) -> QueryAnalysis:
    """
    Analyze a natural-language question and return structured JSON
    describing intent, entities, metrics, ambiguities, etc.

    Does NOT generate or execute SQL.
    """
    try:
        return analyze_query(question=body.question, engine=engine)
    except QueryAnalysisError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ───────────────────────────── query ──────────────────────────────


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    """
    Accept a natural-language question, generate SQL via Ollama,
    validate it, execute it against PostgreSQL, and return the results.
    """
    # 1 — Generate + validate SQL
    try:
        sql = generate_sql(question=body.question, engine=engine)
    except TextToSQLError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # 2 — Execute the validated SELECT
    try:
        result = db.execute(text(sql))
        columns: list[str] = list(result.keys())
        rows: list[dict[str, Any]] = [
            dict(zip(columns, row)) for row in result.fetchall()
        ]
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"SQL execution error: {exc}",
        )

    # 3 — Return
    return QueryResponse(
        question=body.question,
        sql=sql,
        results=rows,
    )
