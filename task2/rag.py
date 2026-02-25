"""
rag.py – RAG Module (Step 1 of the unified system)

Retrieves structured Samsung phone specifications from PostgreSQL
and builds a context string for the language model.
"""

import re
from database import search_phones_by_name, get_all_phones


# ── Phone-name extraction ──────────────────────────────────────────────

# Patterns that match common Samsung model names inside free text
_MODEL_PATTERNS = [
    r"Galaxy\s+Z\s+(?:Fold|Flip)\s*\d*",          # Galaxy Z Fold 5
    r"Galaxy\s+[A-Z]\d+\s+(?:Ultra|Plus|\+|FE|Pro|Lite)",  # Galaxy S23 Ultra
    r"Galaxy\s+[A-Z]\d+",                          # Galaxy S23, Galaxy A54
    r"Galaxy\s+Note\s*\d+\s*(?:Ultra)?",           # Galaxy Note 20 Ultra
]

def extract_model_names(query: str) -> list[str]:
    """Return distinct Samsung model names found in *query*."""
    found = []
    for pattern in _MODEL_PATTERNS:
        for match in re.finditer(pattern, query, re.IGNORECASE):
            found.append(match.group().strip())
    return list(dict.fromkeys(found))   # preserve order, remove duplicates


# ── Retrieval ─────────────────────────────────────────────────────────

def rag_retrieve(query: str) -> tuple[list[dict], str]:
    """
    Retrieve the most relevant phone records from PostgreSQL.

    Returns
    -------
    phones  : list of phone dicts
    context : formatted string ready to be injected into an LLM prompt
    """
    model_names = extract_model_names(query)

    phones: list[dict] = []
    seen_ids: set[int] = set()

    for name in model_names:
        for p in search_phones_by_name(name):
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                phones.append(p)

    # Fallback: return every phone for open-ended / recommendation queries
    if not phones:
        phones = get_all_phones()

    context = _build_context(phones)
    return phones, context


# ── Context builder ───────────────────────────────────────────────────

def _build_context(phones: list[dict]) -> str:
    """Format a list of phone records as a readable spec sheet."""
    if not phones:
        return "No Samsung phone data is currently available in the database."

    sep   = "\n" + "─" * 50 + "\n"
    parts = []
    for p in phones:
        part = (
            f"Model:    {p['model_name']}\n"
            f"Released: {p['release_date']}\n"
            f"Display:  {p['display']}\n"
            f"Battery:  {p['battery']}\n"
            f"Camera:   {p['camera']}\n"
            f"RAM:      {p['ram']}\n"
            f"Storage:  {p['storage']}\n"
            f"Price:    {p['price']}"
        )
        parts.append(part)

    return sep + sep.join(parts) + sep
