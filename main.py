from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# -----------------------------
# MCP Tool Catalog
# -----------------------------
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
    },
    {
        "name": "globeship.serviceability_check",
        "description": "Check if a shipment lane is serviceable and what service levels are available",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_postal": {"type": "string"},
                "to_postal": {"type": "string"},
                "pieces": {"type": "integer"},
                "weight_kg": {"type": "number"}
            },
            "required": ["from_postal", "to_postal", "pieces", "weight_kg"]
        }
    }
]


# -----------------------------
# Simple health
# -----------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}


@app.get("/about")
def about():
    return {
        "service": "NFC.ICU MCP Server",
        "purpose": "AI-native tool endpoints for NFC.ICU and Globeship integrations.",
        "what_this_is": "This API exposes machine-readable tool definitions and tool execution endpoints so AI agents can discover and use verified capabilities.",
        "homepage": "https://nfc.icu",
        "api_base": "https://api.nfc.icu",
        "contact": {"email": "info@nfc.icu"},
    }


@app.get("/robots.txt")
def robots():
    # Keep it simple: allow crawling
    return "User-agent: *\nAllow: /\n"


# -----------------------------
# MCP style endpoints
# -----------------------------
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
        "capabilities": {"tools": True},
        "policies": {
            "terms": "https://nfc.icu/terms",
            "privacy": "https://nfc.icu/privacy",
        },
        "contact": {"email": "info@nfc.icu"},
        "notes": [
            "This server is designed to provide deterministic, structured responses suitable for agent tool use.",
            "Tool schemas are published at /mcp/tools."
        ],
    }


@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": TOOLS}


# Optional: keep this for your own testing
@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}


# -----------------------------
# Tool execution
# -----------------------------
class ToolRequest(BaseModel):
    # allow any JSON payload, tool-specific validation happens manually
    __root__: Dict[str, Any]


def _get_tool(tool_name: str) -> Dict[str, Any]:
    for t in TOOLS:
        if t["name"] == tool_name:
            return t
    raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")


def _require_fields(payload: Dict[str, Any], required: list):
    missing = [k for k in required if k not in payload]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {missing}")


@app.post("/mcp/tools/{tool_name}")
def run_tool(tool_name: str, req: ToolRequest):
    payload = req.__root__

    tool = _get_tool(tool_name)
    required = tool["input_schema"].get("required", [])
    _require_fields(payload, required)

    # -----------------------------
    # Tool: globeship.quick_quote (mock)
    # -----------------------------
    if tool_name == "globeship.quick_quote":
        from_postal = str(payload["from_postal"])
        to_postal = str(payload["to_postal"])
        weight_kg = float(payload["weight_kg"])
        pieces = int(payload["pieces"])

        # Deterministic mock pricing (replace later with real carrier logic)
        base = 12.00
        per_kg = 1.25
        per_piece = 1.75
        total = round(base + (per_kg * weight_kg) + (per_piece * pieces), 2)

        return {
            "tool": tool_name,
            "ok": True,
            "input": {
                "from_postal": from_postal,
                "to_postal": to_postal,
                "weight_kg": weight_kg,
                "pieces": pieces
            },
            "result": {
                "currency": "CAD",
                "total": total,
                "service_level": "standard",
                "estimated_transit_days": "3-7",
                "breakdown": {
                    "base": base,
                    "per_kg": per_kg,
                    "per_piece": per_piece
                },
                "notes": "Mock quote for end-to-end testing. Replace with live rate logic."
            }
        }

    # -----------------------------
    # Tool: globeship.serviceability_check (mock)
    # -----------------------------
    if tool_name == "globeship.serviceability_check":
        from_postal = str(payload["from_postal"])
        to_postal = str(payload["to_postal"])
        weight_kg = float(payload["weight_kg"])
        pieces = int(payload["pieces"])

        # Simple deterministic mock logic:
        # - serviceable if both postals are non-empty and weight/pieces are reasonable
        serviceable = bool(from_postal.strip()) and bool(to_postal.strip()) and weight_kg > 0 and pieces > 0

        service_levels = []
        if serviceable:
            service_levels = ["standard", "express"] if weight_kg <= 30 else ["standard"]

        return {
            "tool": tool_name,
            "ok": True,
            "input": {
                "from_postal": from_postal,
                "to_postal": to_postal,
                "weight_kg": weight_kg,
                "pieces": pieces
            },
            "result": {
                "serviceable": serviceable,
                "available_service_levels": service_levels,
                "carrier_hint": "globeship",
                "notes": "Mock serviceability check for testing. Replace with lane/carrier validation."
            }
        }

    # If a tool exists but has no handler yet:
    raise HTTPException(status_code=501, detail=f"Tool not implemented yet: {tool_name}")
