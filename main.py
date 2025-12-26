from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import re

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.0"
)

# --- CORS (so Hoppscotch / browser-based tools can call your API) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hoppscotch.io",
        "https://www.hoppscotch.io",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request schema shared by both tools ---
class QuoteRequest(BaseModel):
    from_postal: str = Field(..., description="Origin postal/zip code")
    to_postal: str = Field(..., description="Destination postal/zip code")
    weight_kg: float = Field(..., gt=0, description="Total shipment weight in kilograms")
    pieces: int = Field(..., ge=1, description="Number of pieces/boxes")

# --- MCP tool registry (what /mcp/tools returns) ---
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
        "description": "Check if a lane is serviceable and return constraints (mock logic for now)",
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

# --- Basic endpoints ---
@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp"}

@app.get("/about")
def about():
    return {
        "service": "NFC.ICU MCP Server",
        "purpose": "AI-native tool endpoints for NFC.ICU and Globeship integrations.",
        "homepage": "https://nfc.icu",
        "api_base": "https://api.nfc.icu",
        "contact": {"email": "info@nfc.icu"},
    }

@app.get("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\n"

# --- MCP-style discovery endpoints ---
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

# Optional: keep for your own testing
@app.get("/tools")
def list_tools_simple():
    return {"tools": TOOLS}

# --- Tool execution endpoints ---

@app.post("/mcp/tools/globeship.quick_quote")
def globeship_quick_quote(req: QuoteRequest):
    # Mock quote logic (replace with real Globeship rating later)
    base = 12.50
    per_kg = 1.45
    per_piece = 2.25

    total = base + (req.weight_kg * per_kg) + (req.pieces * per_piece)

    return {
        "tool": "globeship.quick_quote",
        "ok": True,
        "input": req.model_dump(),
        "result": {
            "currency": "CAD",
            "total": round(total, 2),
            "service_level": "standard",
            "estimated_transit_days": "3-7",
            "breakdown": {
                "base": base,
                "weight_component": round(req.weight_kg * per_kg, 2),
                "piece_component": round(req.pieces * per_piece, 2),
            },
            "notes": "Mock quote for end-to-end testing. Replace with real Globeship pricing engine."
        }
    }

@app.post("/mcp/tools/globeship.serviceability_check")
def globeship_serviceability_check(req: QuoteRequest):
    # Mock serviceability rules (replace later)
    issues = []

    # super-light validation examples
    if req.weight_kg > 70:
        issues.append("weight_kg exceeds 70kg mock limit")
    if req.pieces > 20:
        issues.append("pieces exceeds 20 mock limit")

    # basic postal sanity checks (US ZIP or CA postal)
    us_zip = re.compile(r"^\d{5}(-\d{4})?$")
    ca_postal = re.compile(r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$")

    def looks_valid(code: str) -> bool:
        c = code.strip()
        return bool(us_zip.match(c) or ca_postal.match(c))

    if not looks_valid(req.from_postal):
        issues.append("from_postal format not recognized (expected US ZIP or CA postal)")
    if not looks_valid(req.to_postal):
        issues.append("to_postal format not recognized (expected US ZIP or CA postal)")

    eligible = len(issues) == 0

    return {
        "tool": "globeship.serviceability_check",
        "ok": True,
        "input": req.model_dump(),
        "result": {
            "eligible": eligible,
            "issues": issues,
            "constraints": {
                "max_weight_kg": 70,
                "max_pieces": 20,
                "supported_postal_formats": ["US ZIP", "CA postal"],
            },
            "notes": "Mock serviceability check for testing. Replace with real carrier/lane rules."
        }
    }
