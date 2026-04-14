"""
Epic Quest System - FastAPI Server
Octopath Traveler-style quest interface
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from pathlib import Path

from ..core.quest import Quest, QuestStatus
from ..core.party import Party
from ..coordination.campfire import Campfire, CampfireAgenda

app = FastAPI(title="Project Epic - Quest System", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active quests (in-memory for now)
active_quests: Dict[str, Dict[str, Any]] = {}

# WebSocket connections
websocket_connections: Dict[str, List[WebSocket]] = {}


class QuestCreate(BaseModel):
    goal: str
    quest_type: Optional[str] = None
    budget: float = 10.0
    max_tokens: int = 100_000
    party_members: List[str] = ["planner", "mage", "rogue", "tank"]


class QuestResponse(BaseModel):
    quest_id: str
    goal: str
    demon_king: str
    status: str
    sprints: List[Dict]
    progress: float
    budget: Dict
    tokens: Dict


@app.get("/")
async def root():
    """Serve the main Octopath-style interface"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Project Epic Quest System", "status": "active"}


@app.post("/quest/create", response_model=QuestResponse)
async def create_quest(quest_data: QuestCreate):
    """Create a new quest"""
    # Create quest
    quest = Quest(
        goal=quest_data.goal,
        quest_type=quest_data.quest_type,
        budget=quest_data.budget,
        max_tokens=quest_data.max_tokens
    )

    # Assemble party
    party = Party.assemble(roles=quest_data.party_members)

    # Store quest and party
    active_quests[quest.id] = {
        "quest": quest,
        "party": party,
        "campfire": Campfire(quest.goal, quest.budget, quest.max_tokens)
    }

    quest.start()

    # Transform sprints to match frontend expectations
    quest_dict = quest.to_dict()
    sprints = [{
        "rank": s["rank"],
        "name": s["name"],
        "description": s["description"],
        "enemy_type": s["enemy"],
        "estimated_cost": s["estimated_cost"],
        "success_criteria": [],
        "completed": s.get("completed", False)
    } for s in quest_dict["sprints"]]

    return QuestResponse(
        quest_id=quest.id,
        goal=quest.goal,
        demon_king=quest.demon_king,
        status=quest.status.value,
        sprints=sprints,
        progress=quest.get_progress_percentage(),
        budget=quest_dict["budget"],
        tokens=quest_dict["tokens"]
    )


@app.get("/quest/{quest_id}")
async def get_quest(quest_id: str):
    """Get quest status"""
    if quest_id not in active_quests:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest = active_quests[quest_id]["quest"]
    quest_dict = quest.to_dict()

    # Transform to match frontend expectations
    sprints = [{
        "rank": s["rank"],
        "name": s["name"],
        "description": s["description"],
        "enemy_type": s["enemy"],
        "estimated_cost": s["estimated_cost"],
        "success_criteria": [],
        "completed": s.get("completed", False)
    } for s in quest_dict["sprints"]]

    return {
        "quest_id": quest_dict["id"],
        "goal": quest_dict["goal"],
        "demon_king": quest_dict["demon_king"],
        "status": quest_dict["status"],
        "progress": quest_dict["progress_percentage"],
        "budget": quest_dict["budget"],
        "tokens": quest_dict["tokens"],
        "sprints": sprints
    }


@app.get("/quest/{quest_id}/party")
async def get_party_status(quest_id: str):
    """Get party member status"""
    if quest_id not in active_quests:
        raise HTTPException(status_code=404, detail="Quest not found")

    party = active_quests[quest_id]["party"]
    return party.get_party_stats()


@app.post("/quest/{quest_id}/sprint/execute")
async def execute_sprint(quest_id: str):
    """Execute the current sprint"""
    if quest_id not in active_quests:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest_data = active_quests[quest_id]
    quest = quest_data["quest"]
    party = quest_data["party"]

    current_sprint = quest.get_current_sprint()
    if not current_sprint:
        raise HTTPException(status_code=400, detail="No more sprints")

    # Broadcast sprint start
    await broadcast_to_quest(quest_id, {
        "type": "sprint_start",
        "sprint": {
            "number": quest.current_sprint_index + 1,
            "rank": current_sprint.rank.value,
            "name": current_sprint.name,
            "enemy": current_sprint.enemy_type
        }
    })

    # Execute sprint (simplified for testing)
    # In real implementation, this would coordinate party members
    try:
        # Simulate sprint execution
        await asyncio.sleep(1)  # Simulate work

        # For testing, assume success
        sprint_cost = current_sprint.estimated_cost
        sprint_tokens = 10000

        quest.complete_sprint(
            success=True,
            cost=sprint_cost,
            tokens=sprint_tokens
        )

        # Broadcast sprint complete
        await broadcast_to_quest(quest_id, {
            "type": "sprint_complete",
            "success": True,
            "cost": sprint_cost,
            "tokens": sprint_tokens
        })

        return {
            "status": "success",
            "sprint_completed": quest.current_sprint_index,
            "progress": quest.get_progress_percentage()
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/quest/{quest_id}/campfire")
async def trigger_campfire(quest_id: str):
    """Trigger a campfire gathering"""
    if quest_id not in active_quests:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest_data = active_quests[quest_id]
    quest = quest_data["quest"]
    party = quest_data["party"]
    campfire = quest_data["campfire"]

    # Gather at campfire
    report = await party.gather_at_campfire(
        campfire=campfire,
        agenda=CampfireAgenda.SPRINT_REVIEW,
        sprint_number=quest.sprints_completed,
        sprint_success=True,  # Simplified
        budget_used=quest.budget_used,
        tokens_used=quest.tokens_used
    )

    # Broadcast campfire report
    await broadcast_to_quest(quest_id, {
        "type": "campfire",
        "report": {
            "on_track": report.on_track,
            "pivot_needed": report.pivot_needed,
            "overall_morale": report.overall_morale,
            "budget_remaining": report.budget_remaining,
            "strategy_changes": report.strategy_changes
        }
    })

    return {
        "on_track": report.on_track,
        "pivot_needed": report.pivot_needed,
        "morale": report.overall_morale,
        "full_report": campfire.format_report(report)
    }


@app.websocket("/ws/quest/{quest_id}")
async def websocket_quest_updates(websocket: WebSocket, quest_id: str):
    """WebSocket for real-time quest updates"""
    await websocket.accept()

    # Add to connections
    if quest_id not in websocket_connections:
        websocket_connections[quest_id] = []
    websocket_connections[quest_id].append(websocket)

    try:
        # Send initial state
        if quest_id in active_quests:
            quest = active_quests[quest_id]["quest"]
            await websocket.send_json({
                "type": "initial_state",
                "quest": quest.to_dict()
            })

        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Echo back (can add command handling here)
            await websocket.send_json({"type": "ack", "message": "received"})

    except WebSocketDisconnect:
        # Remove from connections
        if quest_id in websocket_connections:
            websocket_connections[quest_id].remove(websocket)


async def broadcast_to_quest(quest_id: str, message: Dict):
    """Broadcast message to all WebSocket connections for a quest"""
    if quest_id in websocket_connections:
        for websocket in websocket_connections[quest_id]:
            try:
                await websocket.send_json(message)
            except:
                pass  # Connection closed


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_quests": len(active_quests),
        "websocket_connections": sum(len(conns) for conns in websocket_connections.values())
    }


if __name__ == "__main__":
    import uvicorn
    from ..config import EPIC_HOST, EPIC_PORT, check_api_keys

    # Check API keys
    warnings = check_api_keys()
    if warnings:
        print("\n⚠️  API Key Warnings:")
        for warning in warnings:
            print(f"   {warning}")
        print("\n   For testing without AI, this is fine!")
        print("   Create .env file with keys for real execution.\n")

    uvicorn.run(app, host=EPIC_HOST, port=EPIC_PORT)
