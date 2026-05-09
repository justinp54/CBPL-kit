"""Railway deployment — FastAPI with static file serving and compute endpoint."""
from __future__ import annotations
import json, sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

from api.compute import _validate, _compute

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/compute")
async def compute(request: Request):
    try:
        body   = await request.json()
        inp    = _validate(body)
        result = _compute(inp)
    except Exception as e:
        result = {"success": False, "error": str(e)}
    return JSONResponse(content=result)

# Serve static files — must be after API routes
app.mount("/", StaticFiles(directory=str(_ROOT / "public"), html=True), name="static")
