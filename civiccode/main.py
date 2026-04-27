"""FastAPI runtime foundation for CivicCode."""

from __future__ import annotations

from fastapi import FastAPI

from civiccode import __version__
from civiccore import __version__ as CIVICCORE_VERSION

app = FastAPI(
    title="CivicCode",
    version=__version__,
    summary="Runtime foundation for CivicCode municipal code access workflows.",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Describe the current shipped runtime boundary."""
    return {
        "name": "CivicCode",
        "status": "runtime foundation",
        "message": (
            "CivicCode runtime foundation is online. Municipal code source registry, "
            "section/version storage, search, citations, Q&A, summaries, staff workbench, "
            "CivicClerk handoff, and public lookup workflows are not implemented yet."
        ),
        "code_answer_behavior": "not_available",
        "api_base": "/api/v1/civiccode",
        "future_public_path": "/civiccode",
        "next_step": "Milestone 2: canonical schema and migrations",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Provide a simple operational health check for IT staff."""
    return {
        "status": "ok",
        "service": "civiccode",
        "version": __version__,
        "civiccore": CIVICCORE_VERSION,
    }
