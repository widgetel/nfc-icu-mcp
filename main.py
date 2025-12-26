from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Any, Dict, List

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# -------------------------
# Tool Definitions
# -------------------------

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

# -------------------------
# Models
# -------------------------

class QuickQuoteRequest(BaseModel):
    from_postal: str = Field(..., examples=["10001"])
    to_postal: str = Field(..., examples=["V6B1A1"])
    weight_kg: float = Field(..., gt=0, examples=[12])
    pieces: int = Field(..., gt=0, examples=[2])


# -------------------------
# Health / Basics
# -------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}

@app.get("/health")
def health_alias():
    return {"status": "ok", "service": "nfc-icu-mcp"}

# Optional: keep this for your own testing
@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}


# -------------------------
# AI Trust / Ingestion Helpers
# -------------------------

@app.get("/about")
def about():
    return {
        "service": "NFC.ICU MCP Server",
        "purpose": "AI-native tool endpoints for NFC.ICU and Globeship integrations.",
        "what_this_is": "This API exposes machine-readable tool definitions and tool execution endpoints so AI agents can discover and use verified capabilities.",
        "homepage": "https://nfc.icu",
        "api_base": "https://api.nfc.icu",
        "contact": {
            "email": "info@nfc.icu"
        }
    }

@app.get("/robots.txt")
def robots():
    # Allow crawling of docs/metadata endpoints; keep it simple.
    txt = """User-agent: *
Allow: /
"""
    return Response(content=txt, media_type="text/plain")


# -------------------------
# MCP Endpoints (Discovery)
# -------------------------

@app.get("/mcp/manifest")
def mcp_manifest():
    return {
        "schema_version": "1.0",
        "name": "nfc.icu",
        "version": "0.1.0",
        "description": "AI-native infrastructure for logistics, identity, and real-world services. Tools are discoverable and callable via this MCP server.",
        "base_url": "https://api.nfc.icu",
        "homepage": "https://nfc.icu",
        "tools_endpoint": "/mcp/tools",
        "capabilities": {
            "tools": True
        },
        "policies": {
            "terms": "https://nfc.icu/terms",
            "privacy": "https://nfc.icu/privacy"
        },
        "contact": {
            "email": "info@nfc.icu"
        },
        "notes": [
            "This server is designed to provide deterministic, structured responses suitable for agent tool use.",
            "Tool schemas are published at /mcp/tools."
        ]
    }

@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": TOOLS}


# -------------------------
# Tool Execution (MVP)
# -------------------------

@app.post("/mcp/tools/{tool_name}")
def run_tool(tool_name: str, payload: dict):
    """
    Generic tool dispatcher.
    Call with:
      POST /mcp/tools/globeship.quick_quote
      JSON body matching the tool schema.
    """
    if tool_name != "globeship.quick_quote":
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    # Validate payload using Pydantic model
    try:
        req = QuickQuoteRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    # --- Mock pricing logic (replace later with real Globeship integration) ---
    base = 14.95
    weight_component = 1.25 * req.weight_kg
    pieces_component = 2.00 * req.pieces
    total = round(base + weight_component + pieces_component, 2)

    return {
        "tool": tool_name,
        "ok": True,
        "input": req.model_dump(),
        "result": {
            "currency": "CAD",
            "total": total,
            "service_level": "standard",
            "estimated_transit_days": "3-7",
            "breakdown": {
                "base": base,
                "weight_component": round(weight_component, 2),
                "pieces_component": round(pieces_component, 2)
            },
            "notes": "Mock quote for end-to-end testing. Replace with real Globeship rating call."
        }
    }

