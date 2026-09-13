from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db, engine
from app.schemas.query import QueryRequest, QueryResponse
from app.schemas.analysis import QueryAnalysis
from app.services.text_to_sql import generate_sql, TextToSQLError
from app.services.query_analyzer import analyze_query, QueryAnalysisError

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="QueryMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


from app.services.clarification_engine import ClarificationEngine
from app.services.conversation_manager import ConversationManager

@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    """
    Accept a natural-language question.
    Handles conversation state and clarification resolution.
    Generates SQL via Ollama, validates it, executes against PostgreSQL, and returns results.
    """
    conversation_id = body.conversation_id
    question_to_process = body.question
    analysis_for_sql = None

    if conversation_id:
        conv_state = ConversationManager.get_conversation(conversation_id)
        if not conv_state:
            raise HTTPException(status_code=404, detail="Conversation not found.")
            
        if conv_state.pending_clarification:
            answer = body.question.strip()
            answer_lower = answer.lower()
            matched_value = None
            
            if conv_state.clarification and conv_state.clarification.options:
                for opt in conv_state.clarification.options:
                    if answer_lower == opt.value.lower() or answer_lower == opt.label.lower():
                        matched_value = opt.value
                        break
                        
                if not matched_value:
                    # Invalid answer -> return clarification again
                    return QueryResponse(
                        conversation_id=conversation_id,
                        question=conv_state.original_question,
                        needs_clarification=True,
                        clarification=conv_state.clarification,
                        sql=None,
                        results=None
                    )
            else:
                matched_value = answer
                
            # Update analysis
            analysis = conv_state.query_analysis
            ctype = conv_state.clarification_type
            if ctype == "ranking_metric":
                analysis.metric = matched_value
            elif ctype == "time_range":
                analysis.time_range = matched_value
            elif ctype == "entity":
                if not analysis.entities:
                    analysis.entities = []
                analysis.entities.append(matched_value)
                
            ConversationManager.update_conversation(
                conversation_id,
                query_analysis=analysis,
                pending_clarification=False
            )
            
            question_to_process = conv_state.original_question
            analysis_for_sql = analysis

    # Standard flow (new query or re-analyzing non-pending)
    if not analysis_for_sql:
        try:
            analysis_for_sql = analyze_query(question=question_to_process, engine=engine)
        except QueryAnalysisError as exc:
            raise HTTPException(status_code=422, detail=str(exc))

        clarification_resp = ClarificationEngine.generate(analysis_for_sql)
        
        if clarification_resp.needs_clarification:
            if not conversation_id:
                conversation_id = ConversationManager.create_conversation(
                    original_question=question_to_process,
                    query_analysis=analysis_for_sql,
                    clarification=clarification_resp,
                    clarification_type=clarification_resp.clarification_type
                )
            else:
                ConversationManager.update_conversation(
                    conversation_id,
                    query_analysis=analysis_for_sql,
                    clarification=clarification_resp,
                    clarification_type=clarification_resp.clarification_type,
                    pending_clarification=True
                )
                
            return QueryResponse(
                conversation_id=conversation_id,
                question=question_to_process,
                needs_clarification=True,
                clarification=clarification_resp,
                sql=None,
                results=None
            )
            
        # Create conversation for a clear query if it doesn't exist
        if not conversation_id:
            conversation_id = ConversationManager.create_conversation(
                original_question=question_to_process,
                query_analysis=analysis_for_sql,
                clarification=None,
                clarification_type=None
            )

    # Generate + validate SQL
    try:
        sql = generate_sql(question=question_to_process, engine=engine, analysis=analysis_for_sql)
    except TextToSQLError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Execute the validated SELECT
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

    # Return
    return QueryResponse(
        conversation_id=conversation_id,
        question=question_to_process,
        needs_clarification=False,
        sql=sql,
        results=rows,
    )
