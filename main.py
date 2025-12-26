from fastapi import FastAPI

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

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


