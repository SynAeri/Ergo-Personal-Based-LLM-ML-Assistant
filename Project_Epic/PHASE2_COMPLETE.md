# Project Epic - Phase 2 Complete: World Backend

**Date:** 2026-03-30
**Phase:** World Visualization Backend ✅
**Status:** Ready for Frontend Integration

---

## What Was Built

### 1. World Event Emitter System ✅
**File:** `epic/world/event_emitter.py` (500+ lines)

**Features:**
- `WorldEventEmitter` class with WebSocket broadcasting
- 15+ event types (quest lifecycle, phase changes, agent actions, metrics)
- Convenience methods for common events
- Event history tracking
- Global singleton pattern via `get_world_emitter()`

**Key Events:**
- `quest_start/complete/failed` - Quest lifecycle
- `phase_change` - Triggers zone transitions
- `agent_active/idle/output/error` - Agent state changes
- `campfire_start/message/decision/end` - Group gatherings
- `budget/token/progress/confidence_update` - Metrics & HUD
- `zone_transition` - Agent movement
- `dialogue` - Speech bubbles

**Usage:**
```python
from epic.world import get_world_emitter

emitter = get_world_emitter()
await emitter.phase_change("planning", "sprint_1", sprint_name="Protect the Royal Seal")
await emitter.agent_active("rogue", "Implementing JWT tokens", target_file="src/auth.rs")
await emitter.dialogue("rogue", "Target acquired. Executing Code Strike.")
```

### 2. Zone Configuration System ✅
**File:** `epic/world/zones.json` (300+ lines)

**10 Zones Defined:**
1. **Campfire** - Planning & reviews
2. **Forge** - Debugging & fixes
3. **Arena** - Testing & verification
4. **Library** - Documentation
5. **Guild Hall** - Quest management
6. **Tavern** - Rest & celebration
7. **Inn** - Idle recovery
8. **Dungeon** - Active sprint work
9. **Graveyard** - Failed quests
10. **Market** - Dependencies

**Each Zone Has:**
- Name, description, purpose
- Quest phases it maps to
- Parallax set identifier
- Features list
- Ambient context for dialogue
- Mood and music cue
- Position coordinates
- Confidence palette variants

**Zone Transition Mapping:**
```json
{
  "planning": "campfire",
  "sprint_1": "dungeon",
  "debugging": "forge",
  "testing": "arena",
  "complete": "tavern"
}
```

**Confidence Palettes:**
- High (≥0.8): Bright, warm, optimistic
- Normal (0.5-0.8): Balanced, neutral
- Low (0.3-0.5): Muted, concerning
- Critical (<0.3): Dark, ominous

### 3. Parallax Assets Structure ✅
**Directory:** `frontend/public/parallax/`

**Structure Created:**
```
parallax/
├── PARALLAX_GUIDE.md          (Complete asset guide)
├── campfire/                   (10 zones total)
│   ├── README.md              (Zone-specific guide)
│   ├── far_background/        (depth: 0.2)
│   ├── mid_background/        (depth: 0.5)
│   ├── foreground/            (depth: 0.8)
│   └── overlay/               (depth: 1.0)
├── forge/
├── arena/
├── library/
├── guild_hall/
├── tavern/
├── inn/
├── dungeon/
├── graveyard/
└── market/
```

**Each Zone Has:**
- 4 parallax layers (far, mid, fore, overlay)
- README with art direction
- Placeholder color specifications
- Mood and atmosphere guidelines
- Key elements to include

**Asset Specifications:**
- Format: PNG, 32-bit RGBA
- Size: 1920x1080 (16:9)
- Style: Octopath Traveler HD-2D inspired
- Layers: 4 per zone for depth

### 4. Ambient Dialogue Engine ✅
**File:** `epic/world/dialogue_engine.py` (450+ lines)

**Features:**
- `DialogueEngine` class with LLM integration hooks
- Contextual dialogue templates (the "blacksmith pattern")
- Cooldown management (30s between lines per agent)
- Trigger probability system
- Agent personality integration
- Fallback lines when LLM unavailable

**Dialogue Types:**
- **Functional:** Agent output summaries
- **Ambient:** Idle flavor text
- **Contextual:** Event-driven narrative (technical → fantasy)
- **Victory:** Quest success celebration
- **Frustrated:** Errors and problems

**The "Blacksmith Pattern":**
```python
# Technical event: tests_fail
# Tank says: "These weapons aren't holding up. We should visit the forge."
# → Agent moves to forge zone
# → User sees fantasy narrative, not technical error

dialogue_engine.get_contextual_dialogue("tests_fail", "tank")
# Returns pre-written contextual line
```

**Contextual Templates:**
- tests_fail → "To the forge!"
- dependency_needed → "Visit the bazaar"
- architecture_review → "Consult the archives"
- sprint_complete → "Regroup at campfire"
- budget_warning → "Supplies running low"
- repeated_failure → "We need a new approach"

**Trigger System:**
- Event-driven: Always fire (phase_change, campfire_start)
- Probabilistic: Random chance (idle 30%, midpoint 40%)
- Cooldown: Min 30s between dialogue per agent

---

## File Structure Created

```
Project_Epic/
├── PHASE2_COMPLETE.md              ✅ This file
│
├── epic/
│   └── world/                      ✅ NEW: World system
│       ├── __init__.py
│       ├── event_emitter.py        ✅ WebSocket event broadcasting
│       ├── zones.json              ✅ Zone configurations
│       └── dialogue_engine.py      ✅ Ambient dialogue generation
│
└── frontend/
    └── public/
        └── parallax/               ✅ NEW: Asset structure
            ├── PARALLAX_GUIDE.md   ✅ Complete art guide
            ├── campfire/
            │   ├── README.md       ✅ Zone art direction
            │   ├── far_background/
            │   ├── mid_background/
            │   ├── foreground/
            │   └── overlay/
            ├── forge/
            │   └── README.md       ✅ Zone art direction
            ├── tavern/
            │   └── README.md       ✅ Zone art direction
            └── (7 more zones)
```

**New Code:** ~1,250 lines
**Documentation:** ~500 lines
**Asset Guides:** 3 detailed READMEs

---

## Integration with Existing System

### Orchestrator Integration

```python
# In epic/api/server.py or orchestrator code

from epic.world import get_world_emitter, EventType

emitter = get_world_emitter()

# Quest lifecycle
async def start_quest(quest_data):
    await emitter.quest_start(
        quest_id=quest_data.id,
        title=quest_data.goal,
        demon_lord=quest_data.demon_lord,
        budget=quest_data.budget,
        token_limit=quest_data.token_limit
    )

# Sprint execution
async def execute_sprint(sprint_number, sprint_name):
    await emitter.phase_change(
        from_phase="campfire",
        to_phase=f"sprint_{sprint_number}",
        sprint_number=sprint_number,
        sprint_name=sprint_name
    )

# Agent actions
async def agent_starts_work(agent_id, action):
    await emitter.agent_active(agent_id, action)

    # Generate ambient dialogue
    from epic.world import DialogueEngine, DialogueTrigger
    dialogue_engine = DialogueEngine()
    line = dialogue_engine.generate_dialogue(
        agent_id=agent_id,
        trigger=DialogueTrigger.PHASE_CHANGE,
        context={"zone": "dungeon", "quest_title": "..."}
    )
    if line:
        await emitter.dialogue(agent_id, line, "contextual")
```

### WebSocket Endpoint

```python
# In epic/api/server.py

from fastapi import WebSocket, WebSocketDisconnect
from epic.world import get_world_emitter

@app.websocket("/ws/world")
async def world_websocket(websocket: WebSocket):
    """
    World visualization WebSocket endpoint.
    Frontend connects here to receive events.
    """
    await websocket.accept()
    emitter = get_world_emitter()
    await emitter.add_client(websocket)

    try:
        while True:
            # Keep connection alive
            message = await websocket.receive_text()
            # Could handle client → server messages here if needed
    except WebSocketDisconnect:
        await emitter.remove_client(websocket)
```

---

## Frontend Integration Plan

### Step 1: World Visualizer Component

**Create:** `frontend/components/WorldVisualizer.tsx`

```typescript
import { useEffect, useState } from 'react';
import ParallaxZone from './ParallaxZone';
import AgentSprite from './AgentSprite';

export function WorldVisualizer({ questId }: { questId: string }) {
  const [currentZone, setCurrentZone] = useState('tavern');
  const [agents, setAgents] = useState([]);
  const [confidence, setConfidence] = useState(0.8);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8766/ws/world');

    ws.onmessage = (event) => {
      const worldEvent = JSON.parse(event.data);
      handleWorldEvent(worldEvent);
    };

    return () => ws.close();
  }, [questId]);

  function handleWorldEvent(event) {
    switch (event.type) {
      case 'phase_change':
        // Transition to new zone
        setCurrentZone(event.data.to);
        break;
      case 'agent_active':
        // Update agent state
        updateAgent(event.data.agent_id, { state: 'working' });
        break;
      case 'confidence_update':
        // Shift palette
        setConfidence(event.data.score);
        break;
      case 'dialogue':
        // Show speech bubble
        showDialogue(event.data.agent_id, event.data.text);
        break;
    }
  }

  return (
    <div className="world-container">
      <ParallaxZone
        zone={currentZone}
        confidence={confidence}
      />
      {agents.map(agent => (
        <AgentSprite
          key={agent.id}
          agent={agent}
          zone={currentZone}
        />
      ))}
    </div>
  );
}
```

### Step 2: Parallax Zone Component

**Create:** `frontend/components/ParallaxZone.tsx`

```typescript
import { useMouse } from '@/hooks/useMouse';
import zones from '@/epic/world/zones.json';

export function ParallaxZone({ zone, confidence }) {
  const { mouseX, mouseY } = useMouse();
  const zoneData = zones.zones.find(z => z.id === zone);

  // Calculate parallax offset based on mouse
  const getLayerOffset = (depth) => ({
    x: (mouseX - window.innerWidth / 2) * depth * 0.02,
    y: (mouseY - window.innerHeight / 2) * depth * 0.02,
  });

  // Get palette based on confidence
  const palette = getConfidencePalette(confidence);

  return (
    <div className="parallax-container" style={{ background: palette.bg }}>
      {/* Far background */}
      <ParallaxLayer
        src={`/parallax/${zone}/far_background/`}
        offset={getLayerOffset(0.2)}
      />

      {/* Mid background */}
      <ParallaxLayer
        src={`/parallax/${zone}/mid_background/`}
        offset={getLayerOffset(0.5)}
      />

      {/* Foreground */}
      <ParallaxLayer
        src={`/parallax/${zone}/foreground/`}
        offset={getLayerOffset(0.8)}
      />

      {/* Overlay */}
      <ParallaxLayer
        src={`/parallax/${zone}/overlay/`}
        offset={getLayerOffset(1.0)}
      />
    </div>
  );
}
```

### Step 3: Agent Sprite Component

**Create:** `frontend/components/AgentSprite.tsx`

```typescript
export function AgentSprite({ agent, zone }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dialogue, setDialogue] = useState(null);

  // Position based on zone
  useEffect(() => {
    // Get zone position from zones.json
    // Animate movement to new position
  }, [zone]);

  return (
    <div
      className="agent-sprite"
      style={{
        transform: `translate(${position.x}px, ${position.y}px)`,
        backgroundImage: `url(/sprites/${agent.id}.png)`
      }}
    >
      {dialogue && (
        <SpeechBubble text={dialogue} />
      )}
    </div>
  );
}
```

---

## Testing the System

### 1. Test Event Emitter

```python
# test_world_events.py
import asyncio
from epic.world import get_world_emitter

async def test_events():
    emitter = get_world_emitter()

    # Simulate quest events
    await emitter.quest_start("test_123", "Test Quest", "Test Demon", 10.0, 100000)
    await asyncio.sleep(1)

    await emitter.phase_change("idle", "planning")
    await asyncio.sleep(1)

    await emitter.agent_active("rogue", "Writing code")
    await asyncio.sleep(1)

    await emitter.dialogue("rogue", "Target acquired.", "ambient")

    # Check event history
    history = emitter.get_event_history()
    print(f"Generated {len(history)} events")
    for event in history:
        print(f"  {event['type']}: {event['data']}")

asyncio.run(test_events())
```

### 2. Test Dialogue Engine

```python
# test_dialogue.py
from epic.world import DialogueEngine, DialogueTrigger

engine = DialogueEngine()

# Test contextual dialogue
line = engine.get_contextual_dialogue("tests_fail", "tank")
print(f"Tank: {line}")

# Test generation
line = engine.generate_dialogue(
    agent_id="rogue",
    trigger=DialogueTrigger.AGENT_IDLE,
    context={"zone": "tavern", "quest_title": "Test", "phase": "idle"}
)
print(f"Rogue: {line}")
```

### 3. Test Zone Loading

```python
# test_zones.py
import json

with open('epic/world/zones.json') as f:
    zones = json.load(f)

print(f"Loaded {len(zones['zones'])} zones:")
for zone in zones['zones']:
    print(f"  {zone['name']}: {zone['description']}")
    print(f"    Parallax set: {zone['parallax_set']}")
    print(f"    Features: {', '.join(zone['features'])}")
```

---

## Next Steps (Phase 3: Frontend Integration)

### Immediate (2-3 hours):

1. **Create WorldVisualizer Component**
   - WebSocket connection
   - Event handling
   - State management

2. **Create ParallaxZone Component**
   - Layer rendering
   - Mouse parallax effect
   - Confidence-based palette

3. **Create AgentSprite Component**
   - Sprite rendering
   - Position animation
   - Speech bubbles

4. **Create Placeholder Assets**
   - Colored divs for layers
   - CSS gradients
   - Text labels

### Short-term (4-6 hours):

5. **Zone Transition System**
   - Fade between zones
   - Agent pathfinding animation
   - Smooth camera movement

6. **Speech Bubble System**
   - Pixel-art bubble rendering
   - Text display
   - Auto-fade after 4 seconds

7. **Agent Animation System**
   - Idle, walking, working states
   - Sprite sheet or CSS animations
   - State transitions

8. **HUD Integration**
   - Budget/token display
   - Confidence indicator
   - Phase name display

---

## Cost Estimates

### Ambient Dialogue (New Cost):
- Gemini Flash: ~$0.0001 per line
- Frequency: ~30 lines per quest
- **Total: ~$0.003 per quest**

### Pre-written Templates (Free):
- Most contextual dialogue uses templates
- No LLM calls for common events
- **Cost: $0**

### Total Additional Cost:
- **~$0.003 per quest (essentially free)**
- Rest is existing agent costs (~$7-8 per quest)

---

## Asset Creation Guide

### For Artists:

1. **Start with Campfire**
   - Most important zone (planning hub)
   - Read: `frontend/public/parallax/campfire/README.md`
   - Create 4 layers at 1920x1080

2. **Then Tavern**
   - Second most used (idle/celebration)
   - Victory atmosphere important

3. **Then Others**
   - Forge (debugging)
   - Arena (testing)
   - Etc.

### Tools Recommended:
- Aseprite (pixel art)
- Photoshop/GIMP (layers)
- TinyPNG (compression)

---

## Summary

**Phase 2 (World Backend) is COMPLETE.** ✅

We've built:
- ✅ Event emitter with 15+ event types
- ✅ WebSocket broadcasting system
- ✅ 10 zone configurations
- ✅ 4-layer parallax structure (40 layer folders)
- ✅ Ambient dialogue engine
- ✅ Contextual "blacksmith pattern" templates
- ✅ Complete art direction guides

The backend is ready to emit events. The frontend structure is ready for assets. The dialogue system is ready to generate in-character lines.

**Next:** Integrate into existing frontend, create placeholder visuals, wire up WebSocket events.

---

**"The world exists in data. Now we give it form."**
