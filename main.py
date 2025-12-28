from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os
import re
import uuid

app = FastAPI(
    title="NFC.ICU MCP Server",
    description="MCP server for NFC.ICU and Globeship tools",
    version="0.1.1"
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

# --- API key middleware for tool execution ---
# NOTE:
# - /mcp/manifest and /mcp/tools remain PUBLIC so DreamCrew can discover tools without timing out.
# - Tool execution endpoints (/mcp/tools/...) require X-API-Key.
API_KEY = os.getenv("API_KEY", "").strip()


@app.middleware("http")
async def require_api_key_for_tools(request: Request, call_next):
    path = request.url.path

    # Allow discovery endpoints without auth (important for DreamCrew)
    if path in ["/", "/about", "/robots.txt", "/mcp/manifest", "/mcp/tools", "/tools"]:
        return await call_next(request)

    # Require API key for tool execution endpoints
    if path.startswith("/mcp/tools/"):
        if not API_KEY:
            # Server misconfigured (no API_KEY set)
            raise HTTPException(status_code=500, detail="Server missing API_KEY secret")

        supplied = request.headers.get("X-API-Key", "").strip()

        # (Optional) also allow Authorization: Bearer <key> if some platforms only support bearer
        if not supplied:
            auth = request.headers.get("Authorization", "").strip()
            if auth.lower().startswith("bearer "):
                supplied = auth.split(" ", 1)[1].strip()

        if supplied != API_KEY:
            raise HTTPException(status_code=401, detail="Missing or invalid API key")

    return await call_next(request)


# --- Request schema shared by both tools ---
class QuoteRequest(BaseModel):
    from_postal: str = Field(..., description="Origin postal/zip code")
    to_postal: str = Field(..., description="Destination postal/zip code")
    weight_kg: float = Field(..., gt=0, description="Total shipment weight in kilograms")
    pieces: int = Field(..., ge=1, description="Number of pieces/boxes")


def _meta():
    return {
        "request_id": str(uuid.uuid4()),
        "ts": datetime.now(timezone.utc).isoformat(),
        "service": "nfc-icu-mcp",
        "version": app.version,
    }


def _tool_response(tool: str, ok: bool, input_data: dict, result: dict | None = None, errors: list | None = None):
    return {
        "tool": tool,
        "ok": ok,
        "input": input_data,
        "result": result or {},
        "errors": errors or [],
        "meta": _meta(),
    }


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
                "pieces": {"type": "integer"},
            },
            "required": ["from_postal", "to_postal", "weight_kg", "pieces"],
        },
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
                "pieces": {"type": "integer"},
            },
            "required": ["from_postal", "to_postal", "weight_kg", "pieces"],
        },
    },
]


# --- Basic endpoints ---
@app.get("/")
def health_check():
    return {"status": "ok", "service": "nfc-icu-mcp", "version": app.version}


@app.get("/about")
def about():
    return {
        "service": "NFC.ICU MCP Server",
        "purpose": "AI-native tool endpoints for NFC.ICU and Globeship integrations.",
        "homepage": "https://nfc.icu",
        "api_base": "https://api.nfc.icu",
        "contact": {"email": "info@nfc.icu"},
        "version": app.version,
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
        "version": app.version,
        "description": "AI-native infrastructure for logistics, identity, and real-world services. Tools are discoverable and callable via this MCP server.",
        "base_url": "https://api.nfc.icu",
        "homepage": "https://nfc.icu",
        "tools_endpoint": "/mcp/tools",
        "capabilities": {"tools": True},
        "contact": {"email": "info@nfc.icu"},
        "notes": [
            "Discovery endpoints (/mcp/manifest, /mcp/tools) are public for agent onboarding.",
            "Tool execution endpoints require X-API-Key.",
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
    total_rounded = round(total, 2)

    result = {
        "summary": f"Estimated {total_rounded} CAD (standard, 3-7 days).",
        "currency": "CAD",
        "total": total_rounded,
        "service_level": "standard",
        "estimated_transit_days": "3-7",
        "breakdown": {
            "base": base,
            "weight_component": round(req.weight_kg * per_kg, 2),
            "piece_component": round(req.pieces * per_piece, 2),
        },
        "notes": "Mock quote for end-to-end testing. Replace with real Globeship pricing engine.",
    }

    return _tool_response(
        tool="globeship.quick_quote",
        ok=True,
        input_data=req.model_dump(),
        result=result,
        errors=[],
    )


@app.post("/mcp/tools/globeship.serviceability_check")
def globeship_serviceability_check(req: QuoteRequest):
    # Mock serviceability rules (replace later)
    issues = []

    if req.weight_kg > 70:
        issues.append("weight_kg exceeds 70kg mock limit")
    if req.pieces > 20:
        issues.append("pieces exceeds 20 mock limit")

    # US ZIP or CA postal sanity checks
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

    result = {
        "eligible": eligible,
        "issues": issues,
        "constraints": {
            "max_weight_kg": 70,
            "max_pieces": 20,
            "supported_postal_formats": ["US ZIP", "CA postal"],
        },
        "notes": "Mock serviceability check for testing. Replace with real carrier/lane rules.",
    }

    return _tool_response(
        tool="globeship.serviceability_check",
        ok=True,
        input_data=req.model_dump(),
        result=result,
        errors=[],
    )
