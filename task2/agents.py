"""
agents.py – Multi-Agent System (Step 2 of the unified system)

Agent 1 – Data Extractor
    Uses Anthropic tool-use to call the PostgreSQL database and pull
    the exact phone records needed to answer the user's query.

Agent 2 – Review Generator
    Receives the structured data from Agent 1 and produces a polished
    natural-language review, comparison, or recommendation.
"""

import json
import logging
import re

import anthropic

from config import ANTHROPIC_API_KEY
from database import search_phones_by_name, get_all_phones

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL  = "claude-haiku-4-5-20251001"


# ══════════════════════════════════════════════════════════════════════
# Tool definitions  (used by Agent 1)
# ══════════════════════════════════════════════════════════════════════

AGENT1_TOOLS = [
    {
        "name": "search_phones_by_name",
        "description": (
            "Search the Samsung phone database for models matching a name. "
            "Use when the user mentions a specific model (e.g. 'Galaxy S23 Ultra')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Partial or full model name (e.g. 'S23 Ultra', 'Galaxy A54').",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_all_phones",
        "description": (
            "Retrieve all Samsung phones from the database. "
            "Use for general questions, recommendations, or when no specific model is mentioned."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    """Run a tool call and return the result as a JSON string."""
    if tool_name == "search_phones_by_name":
        phones = search_phones_by_name(tool_input["name"])
    elif tool_name == "get_all_phones":
        phones = get_all_phones()
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    if not phones:
        return json.dumps({"result": "No matching phones found."})

    # Return only the key fields so the context stays concise
    slim = [
        {
            "model":    p["model_name"],
            "released": p["release_date"],
            "display":  p["display"],
            "battery":  p["battery"],
            "camera":   p["camera"],
            "ram":      p["ram"],
            "storage":  p["storage"],
            "price":    p["price"],
        }
        for p in phones
    ]
    return json.dumps(slim, indent=2)


# ══════════════════════════════════════════════════════════════════════
# Agent 1 – Data Extractor
# ══════════════════════════════════════════════════════════════════════

class DataExtractorAgent:
    """
    Drives an agentic tool-use loop.
    Calls the database tools as many times as needed, then returns a
    structured summary plus the raw list of phone dicts.
    """

    SYSTEM = """You are a data-extraction agent for a Samsung phone advisor.

Your job:
1. Analyse the user query to decide which phones are relevant.
2. Call the available tools to retrieve those phone records.
3. After retrieving the data, write a concise JSON summary:
   {
     "phones": [<model names>],
     "query_type": "specs" | "comparison" | "recommendation",
     "key_attributes": [<attributes the user cares about>]
   }

Always call at least one tool before writing your final answer."""

    def run(self, query: str) -> tuple[dict, list[dict]]:
        """
        Returns
        -------
        meta        : dict with query_type, phones, key_attributes
        phones_data : list of raw phone dicts from the DB
        """
        messages      = [{"role": "user", "content": query}]
        phones_data: list[dict] = []

        # ── Agentic loop ───────────────────────────────────────────────
        while True:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system=self.SYSTEM,
                tools=AGENT1_TOOLS,
                messages=messages,
            )

            # Collect and execute any tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("[Agent 1] → %s(%s)", block.name, block.input)
                    result_str = _execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type":        "tool_result",
                            "tool_use_id": block.id,
                            "content":     result_str,
                        }
                    )
                    # Accumulate phone records
                    try:
                        parsed = json.loads(result_str)
                        if isinstance(parsed, list):
                            phones_data.extend(parsed)
                    except Exception:
                        pass

            if response.stop_reason == "end_turn":
                # Extract the text summary
                text = "".join(
                    b.text for b in response.content if hasattr(b, "text")
                )
                # Try to pull out the JSON meta block
                meta: dict = {"query_type": "specs", "phones": [], "key_attributes": []}
                try:
                    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
                    if m:
                        meta = json.loads(m.group())
                except Exception:
                    pass
                return meta, phones_data

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user",      "content": tool_results})
            else:
                break   # Unexpected stop reason

        return {"query_type": "specs"}, phones_data


# ══════════════════════════════════════════════════════════════════════
# Agent 2 – Review Generator
# ══════════════════════════════════════════════════════════════════════

class ReviewGeneratorAgent:
    """
    Receives structured phone data from Agent 1 and generates a
    polished natural-language answer for the user.
    """

    SYSTEM = """You are an expert Samsung smartphone advisor and tech reviewer.

Rules:
- Specs query   → List the key specifications in a readable format.
- Comparison    → Compare phones across display, camera, battery, performance, and value.
- Recommendation → Give a clear recommendation with specific reasoning.
- Only use data provided; never invent specifications.
- Keep answers concise, helpful, and free of marketing fluff.
- If data is missing for a field, say "Not available"."""

    def run(self, query: str, meta: dict, phones_data: list[dict]) -> str:
        """Generate a natural-language answer."""
        query_type = meta.get("query_type", "specs")

        if query_type == "comparison":
            task = "Provide a detailed side-by-side comparison."
        elif query_type == "recommendation":
            task = "Provide a clear recommendation with reasoning based on the user's needs."
        else:
            task = "Provide detailed specifications and relevant information."

        context = json.dumps(phones_data, indent=2) if phones_data else "No data retrieved."

        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=self.SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"User question: {query}\n\n"
                        f"Phone data:\n{context}\n\n"
                        f"Task: {task}"
                    ),
                }
            ],
        )
        return response.content[0].text


# ══════════════════════════════════════════════════════════════════════
# Orchestrator
# ══════════════════════════════════════════════════════════════════════

def run_multi_agent(query: str) -> str:
    """
    Runs the full two-agent pipeline and returns the final answer.

    Flow:
        User query
            → Agent 1 (Data Extractor)  – queries PostgreSQL via tools
            → Agent 2 (Review Generator) – writes the natural-language answer
    """
    logger.info("[Agent 1 – Data Extractor]  Query: %r", query)
    agent1            = DataExtractorAgent()
    meta, phones_data = agent1.run(query)
    logger.info("[Agent 1]  Retrieved %d phone record(s).", len(phones_data))

    logger.info("[Agent 2 – Review Generator] Generating response...")
    agent2 = ReviewGeneratorAgent()
    answer = agent2.run(query, meta, phones_data)
    logger.info("[Agent 2]  Done.")

    return answer
