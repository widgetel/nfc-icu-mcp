from fastapi import FastAPI

app = FastAPI(
    title="NFC.ICU MCP Server",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "nfc-icu-mcp"
    }

@app.get("/health")
def health():
    return {"ok": True}
