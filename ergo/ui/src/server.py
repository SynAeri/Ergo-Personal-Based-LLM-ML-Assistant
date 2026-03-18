"""
Ergo UI Server
Simple web interface for chat, activity view, and interventions
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ergo UI", version="0.1.0")

# Templates directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Orchestrator API base URL
ORCHESTRATOR_URL = "http://127.0.0.1:8765"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main UI page"""
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Ergo"}
    )


@app.get("/api/health")
async def health():
    """Health check that also checks orchestrator"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{ORCHESTRATOR_URL}/health", timeout=2.0)
            orchestrator_status = resp.json()
    except Exception as e:
        orchestrator_status = {"error": str(e)}

    return {
        "ui": "healthy",
        "orchestrator": orchestrator_status,
    }


@app.post("/api/chat")
async def chat(request: Request):
    """Proxy chat requests to orchestrator"""
    try:
        body = await request.json()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/chat",
                json=body,
                timeout=30.0,
            )
            return resp.json()

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )


@app.get("/api/context/recent")
async def get_recent_context(minutes: int = 30):
    """Get recent context from orchestrator"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{ORCHESTRATOR_URL}/context/recent",
                params={"minutes": minutes},
                timeout=5.0,
            )
            return resp.json()

    except Exception as e:
        logger.error(f"Context error: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )


@app.get("/api/interventions")
async def get_interventions():
    """Get pending interventions"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{ORCHESTRATOR_URL}/interventions",
                timeout=5.0,
            )
            return resp.json()

    except Exception as e:
        logger.error(f"Interventions error: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Ergo UI on http://127.0.0.1:3000")
    uvicorn.run(app, host="127.0.0.1", port=3000)
