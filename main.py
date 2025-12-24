from fastapi import FastAPI
import os

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}

@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "globeship.quick_quote",
                "description": "Generate a fast Globeship shipping quote",
            }
        ]
    }

