from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# ---- Tool schema (what /mcp/tools returns) ----
TOOLS = [
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

# ---- Request model for the quote tool ----
class QuickQuoteRequest(BaseModel):
    from_postal: str = Field(..., examples=["10001"])
    to_postal: str = Field(..., examples=["V6B1A1"])
    weight_kg: float = Field(..., gt=0, examples=[12])
    pieces: int = Field(..., gt=0, examples=[2])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}


# Optional: keep this for your own testing
@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}


# ✅ MCP style endpoints
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


# ✅ THIS is the missing piece: execute a tool
@app.post("/mcp/tools/{tool_name}")
def run_tool(tool_name: str, payload: dict):
    """
    Generic dispatcher. Calls the tool based on tool_name.
    """
    if tool_name != "globeship.quick_quote":
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    # Validate payload using Pydantic model
    try:
        req = QuickQuoteRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    # --- For now: return a mock quote (we can wire real Globeship later) ---
    base = 14.95
    weight_component = 1.25 * req.weight_kg
    pieces_component = 2.00 * req.pieces
    total = round(base + weight_component + pieces_component, 2)

    return {
        "tool": tool_name,
        "input": req.model_dump(),
        "quote": {
            "currency": "CAD",
            "total": total,
            "breakdown": {
                "base": base,
                "weight_component": round(weight_component, 2),
                "pieces_component": round(pieces_component, 2),
            },
            "service_level": "standard",
            "estimated_transit_days": "3-7"
        }
    }

