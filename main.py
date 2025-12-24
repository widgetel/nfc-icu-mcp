from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# -------------------
# Health
# -------------------
@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}

# -------------------
# MCP Manifest
# -------------------
@app.get("/mcp/manifest")
def mcp_manifest():
    return {
        "name": "nfc-icu-mcp",
        "description": "MCP server for NFC.ICU and Globeship",
        "version": "0.1.0",
        "tools_endpoint": "/mcp/tools",
        "invoke_endpoint": "/mcp/invoke"
    }

# -------------------
# MCP Tools List
# -------------------
@app.get("/mcp/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "globeship.quick_quote",
                "description": "Generate a fast Globeship shipping quote",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string"},
                        "destination": {"type": "string"},
                        "weight_kg": {"type": "number"}
                    },
                    "required": ["origin", "destination", "weight_kg"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "price": {"type": "number"},
                        "currency": {"type": "string"},
                        "eta_days": {"type": "number"}
                    }
                }
            }
        ]
    }

# -------------------
# MCP Invoke
# -------------------
class InvokeRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

@app.post("/mcp/invoke")
def invoke_tool(req: InvokeRequest):
    if req.tool == "globeship.quick_quote":
        # STUB (we wire real Globeship logic next)
        return {
            "price": 123.45,
            "currency": "USD",
            "eta_days": 5
        }

    return {"error": "Unknown tool"}

