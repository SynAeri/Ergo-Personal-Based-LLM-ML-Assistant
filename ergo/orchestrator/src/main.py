"""
Ergo Orchestrator - Main service
Handles model routing, memory updates, and context assembly
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.model_router import router, TaskType
from src.context_builder import ContextBuilder
from src.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Ergo Orchestrator", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
context_builder = ContextBuilder()
memory_manager = MemoryManager()


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    persona_mode: str = "standard"
    include_context: bool = True


class ChatResponse(BaseModel):
    response: str
    context_used: Optional[str] = None


class EventPayload(BaseModel):
    event_id: str
    timestamp: int
    source: str
    event_type: str
    project_id: Optional[str]
    privacy_tag: str
    payload: Dict[str, Any]
    confidence: float


class SummaryRequest(BaseModel):
    session_id: str
    duration_minutes: int


# API Endpoints


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ergo-orchestrator",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "anthropic_configured": router.anthropic_client is not None,
        "gemini_configured": router.gemini_configured,
        "openai_configured": router.openai_client is not None,
        "database_type": settings.database_type,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle a chat request with context assembly and model routing
    """
    try:
        # Build context if requested
        context = None
        if request.include_context:
            context = await context_builder.build_chat_context()

        # Generate response
        response = await router.generate_chat_response(
            user_message=request.message,
            context=context,
            persona_mode=request.persona_mode,
        )

        return ChatResponse(response=response, context_used=context)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/code-review")
async def code_review(
    code: str, language: str, file_path: Optional[str] = None
):
    """
    Perform code review using Opus
    """
    try:
        # Build context around the code
        context = f"File: {file_path or 'unknown'}"
        if file_path:
            # Could add git info, recent changes, etc.
            pass

        review = await router.generate_code_review(
            code=code, language=language, context=context
        )

        return {"review": review}

    except Exception as e:
        logger.error(f"Error in code-review endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events")
async def receive_event(event: EventPayload):
    """
    Receive an event from the daemon
    Process it for memory updates and intervention checks
    """
    try:
        logger.info(
            f"Received event: {event.source}.{event.event_type} [{event.event_id}]"
        )

        # Store in memory manager
        await memory_manager.process_event(event.dict())

        # Check for intervention triggers (if enabled)
        if settings.enable_interventions:
            # TODO: Implement intervention checking
            pass

        return {"status": "processed", "event_id": event.event_id}

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary")
async def generate_summary(request: SummaryRequest):
    """
    Generate a session summary
    """
    try:
        # Get events for the session
        events = await memory_manager.get_session_events(request.session_id)

        # Generate summary
        summary = await router.generate_session_summary(
            events=events, duration_minutes=request.duration_minutes
        )

        # Store the summary
        await memory_manager.store_summary(
            session_id=request.session_id, summary_text=summary
        )

        return {"summary": summary, "session_id": request.session_id}

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/context/recent")
async def get_recent_context(minutes: int = 30):
    """
    Get recent context (ephemeral memory window)
    """
    try:
        context = await context_builder.get_recent_context(minutes)
        return {"context": context, "window_minutes": minutes}

    except Exception as e:
        logger.error(f"Error getting recent context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{memory_type}/{key}")
async def get_memory(memory_type: str, key: str):
    """
    Retrieve a specific memory by type and key
    """
    try:
        value = await memory_manager.get_memory(memory_type, key)
        if value is None:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"memory_type": memory_type, "key": key, "value": value}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/{memory_type}/{key}")
async def store_memory(
    memory_type: str, key: str, value: str, project_id: Optional[str] = None
):
    """
    Store a long-term memory fact
    """
    try:
        await memory_manager.store_memory(memory_type, key, value, project_id)
        return {
            "status": "stored",
            "memory_type": memory_type,
            "key": key,
        }

    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interventions")
async def get_interventions():
    """
    Get pending interventions
    """
    try:
        interventions = await memory_manager.get_pending_interventions()
        return {"interventions": interventions}

    except Exception as e:
        logger.error(f"Error retrieving interventions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point"""
    logger.info("Starting Ergo Orchestrator")
    logger.info(f"Database: {settings.database_type}")
    logger.info(f"Listening on {settings.orchestrator_host}:{settings.orchestrator_port}")

    uvicorn.run(
        "orchestrator.src.main:app",
        host=settings.orchestrator_host,
        port=settings.orchestrator_port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
