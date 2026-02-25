"""
main.py – FastAPI Samsung Phone Advisor

Endpoints
---------
POST /ask     Natural-language query → answer (specs / comparison / recommendation)
GET  /phones  List all phones in the database
GET  /health  Health check

Run:
    uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import run_multi_agent
from database import initialize_db, get_all_phones

# ── Logging ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan: init DB on startup ───────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        initialize_db()
        logger.info("Application startup complete.")
    except Exception as exc:
        logger.warning("Could not initialise database: %s", exc)
    yield
    logger.info("Application shutdown.")


# ── App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Samsung Phone Advisor",
    description=(
        "Ask natural-language questions about Samsung smartphones. "
        "Powered by a RAG + Multi-Agent system backed by PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"question": "What are the specs of Samsung Galaxy S23 Ultra?"},
                {"question": "Compare Galaxy S23 Ultra and S22 Ultra for photography."},
                {"question": "Which Samsung phone has the best battery under $1000?"},
            ]
        }
    }


class AnswerResponse(BaseModel):
    answer: str


# ── Endpoints ──────────────────────────────────────────────────────────

@app.post(
    "/ask",
    response_model=AnswerResponse,
    summary="Ask a natural-language question about Samsung phones",
)
async def ask(request: QuestionRequest):
    """
    **RAG + Multi-Agent pipeline:**

    1. RAG module retrieves relevant phone specs from PostgreSQL.
    2. Agent 1 (Data Extractor) pulls structured data using tool calls.
    3. Agent 2 (Review Generator) composes the final answer.

    Example questions:
    - "What are the specs of Samsung Galaxy S23 Ultra?"
    - "Compare Galaxy S23 Ultra and S22 Ultra for photography."
    - "Which Samsung phone has the best battery under $1000?"
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        answer = run_multi_agent(request.question)
    except Exception as exc:
        logger.exception("Error processing question: %r", request.question)
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")
    return AnswerResponse(answer=answer)


@app.get("/phones", summary="List all Samsung phones in the database")
async def list_phones():
    """Return the names of all Samsung phone models currently stored in PostgreSQL."""
    phones = get_all_phones()
    return {"count": len(phones), "phones": [p["model_name"] for p in phones]}


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}


# ── Dev runner ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
