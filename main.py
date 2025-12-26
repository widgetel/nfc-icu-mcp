from fastapi import FastAPI

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# -------------------------
# Tool Definitions
# -------------------------

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

# -------------------------
# Health Check
# -------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}

# -------------------------
# Optional simple tools endpoint (your own testing)
# -------------------------

@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}

# -------------------------
# MCP Endpoints (IMPORTANT)
# -------------------------

@app.get("/mcp/manifest")
def mcp_manifest():
    return {
        "schema_version": "1.0",
        "name": "nfc.icu",
        "description": "AI-native infrastructure for logistics, identity, and real-world services",
        "version": "0.1.0",
        "base_url": "https://api.nfc.icu",
        "tools_endpoint": "/mcp/tools",
        "capabilities": {
            "tools": True
        },
        "contact": {
            "email": "info@nfc.icu"
        }
    }

@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": TOOLS}



