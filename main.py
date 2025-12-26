from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List


app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# ---------- Tool definitions (what tools exist) ----------

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "globeship.quick_quote",
        "description": "Generate a fast Globeship shipping quote",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_postal": {"type": "string"},
                "to_postal": {"type": "string"},
                "weight_kg": {"type": "number"},
                "pieces": {"type": "integer"}
            },
            "required": ["from_postal", "to_postal", "weight_kg", "pieces"]
        }
    }
]


# ---------- Request/Response models (tool execution) ----------

class QuickQuoteInput(BaseModel):
    from_postal: str = Field(..., example="10001")
    to_postal: str = Field(..., example="V6B1A1")
    weight_kg: float = Field(..., gt=0, example=12.0)
    pieces: int = Field(..., ge=1, example=2)


# ---------- Basic health ----------

@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}


# Optional: keep this for your own testing
@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}


# ---------- MCP style endpoints ----------

@app.get("/mcp/manifest")
def mcp_manifest():
    return {
        "name": "nfc-icu-mcp",
        "version": "0.1.0",
        "description": "MCP server for NFC.ICU and Globeship tools",
        "tools_endpoint": "/mcp/tools"
    }


@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": TOOLS}


# ---------- Tool execution endpoint (THIS is what was missing) ----------

@app.post("/mcp/tools/globeship.quick_quote")
def run_globeship_quick_quote(payload: QuickQuoteInput):
    """
    Executes the globeship.quick_quote tool.
    Right now this returns a simple mock quote so you can test the MCP flow end-to-end.
    Later we can replace the pricing logic with a real carrier/Globeship integration.
    """

    # --- Mock pricing logic (replace later) ---
    base_fee = 8.50
    per_kg = 2.25
    per_piece = 1.10

    estimated_cost = base_fee + (payload.weight_kg * per_kg) + (payload.pieces * per_piece)

    # Super-light “service level” mock
    service_level = "EXPRESS" if payload.weight_kg <= 10 else "STANDARD"

    # MCP-style response shape (simple + predictable)
    return {
        "tool": "globeship.quick_quote",
        "ok": True,
        "input": payload.model_dump(),
        "result": {
            "service_level": service_level,
            "currency": "USD",
            "estimated_total": round(estimated_cost, 2),
            "notes": "Mock quote (replace with real Globeship rating call)."
        }
    }


