"""FastAPI Application Main Entrypoint."""

import sys
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.absolute()))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator

from hiremind.infrastructure import logger
from hiremind.interfaces.api.middleware import RequestTimingMiddleware
from hiremind.interfaces.api.routers import candidates, health, jobs, ranking, reasoning

app = FastAPI(
    title="HireMind AI - Recruiter Platform",
    description="Intelligent candidate retrieval, ranking, and reasoning API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Middlewares
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Prometheus Instrumentation
Instrumentator().instrument(app).expose(app)

# 3. Include Routers
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(ranking.router)
app.include_router(candidates.router)
app.include_router(reasoning.router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting HireMind AI API...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down HireMind AI API...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("hiremind.interfaces.api.main:app", host="0.0.0.0", port=8000, reload=True)
