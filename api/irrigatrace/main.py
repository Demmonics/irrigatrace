"""
Main FastAPI application entrypoint for IrrigaTrace.
Exposes all REST & SSE routes with CORS and OpenAPI docs.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.irrigatrace.api.routers import (
    health,
    plots,
    decisions,
    compare,
    audit,
    analytics,
    search,
    admin,
)

app = FastAPI(
    title="IrrigaTrace API",
    version="1.0.0",
    description="Object-oriented decision audit and replay system for AI irrigation advisory (KJS-AGR-01).",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(plots.router, prefix="/api")
app.include_router(decisions.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "IrrigaTrace API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/api/docs",
    }


def export_openapi_schema(output_path: str = "./openapi.json"):
    """Exports OpenAPI schema JSON to feed frontend TypeScript code generators."""
    schema = app.openapi()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"OpenAPI schema exported to {output_path}")


if __name__ == "__main__":
    export_openapi_schema()
