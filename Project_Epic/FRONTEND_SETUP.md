# Project Epic - New Frontend Setup Complete! 🎮

## What Was Created

A **Next.js + TypeScript** frontend with:
- ✨ Mouse-based parallax forest background (4 layers)
- 🎨 HD-2D Octopath Traveler aesthetic
- ⚔️ Full quest creation and management UI
- 📊 Real-time WebSocket updates
- 🏕️ Sprint execution and campfire system

## Quick Start

### 1. Start Backend
```bash
cd ~/Documents/Github/Ergo/Project_Epic
source venv/bin/activate
python -m epic.api.server
```

Backend runs at: **http://localhost:8766**

### 2. Start Frontend
```bash
cd ~/Documents/Github/Ergo/Project_Epic/frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Open Browser
Go to **http://localhost:3000** and you'll see:
- Parallax forest background that moves with your mouse
- Party selection interface (choose up to 4 members)
- Quest goal input
- Beautiful HD-2D styled quest board

## What Was Fixed

### ❌ Old Issues:
1. Execute button didn't work properly
2. Progress bar showed NaN%
3. No proper frontend separation
4. No mouse-based parallax
5. CORS errors

### ✅ Now Fixed:
1. ✅ Execute sprint button fully functional
2. ✅ Progress bar correctly calculates percentage
3. ✅ Separate Next.js frontend with TypeScript
4. ✅ Mouse-based parallax with 4 forest layers
5. ✅ CORS enabled for localhost:3000
6. ✅ WebSocket real-time updates
7. ✅ Proper error handling and loading states

## Features

### Parallax Forest Background
- **4 Layers**: Layer 1 (foreground) → Layer 4 (background)
- **Mouse Control**: Move mouse to look around the scene
- **Depth Effect**: Closer layers move faster, creating depth illusion
- **HD-2D Style**: Pixelated images with modern effects

### Quest Creation
1. **Select Party** (up to 4):
   - 🗺️ Planner - Strategic planning
   - 🧙 Mage - Architecture
   - 🗡️ Rogue - Code execution
   - 🛡️ Tank - Testing
   - 📚 Support - Documentation
   - ✨ Healer - Refactoring

2. **Enter Quest Goal**: e.g., "Build a banking app"

3. **Begin Quest**: Creates 6 difficulty-scaled sprints

### Quest Management
- **Progress Tracking**: Real-time progress bar
- **Sprint Visualization**: See all 6 sprints (D→C→B→A→S→SSS)
- **Execute Sprint**: Run current sprint
- **Campfire**: Business checkpoint after sprints
- **Budget & Token Tracking**: Monitor resource usage

## Architecture

```
Project_Epic/
├── epic/                    # Backend (Python/FastAPI)
│   ├── api/
│   │   └── server.py       # FastAPI server with CORS
│   ├── core/
│   │   ├── quest.py
│   │   ├── party.py
│   │   └── claude_agent.py
│   └── ...
└── frontend/                # Frontend (Next.js/TypeScript)
    ├── app/
    │   ├── page.tsx        # Main quest interface
    │   └── layout.tsx      # App layout with fonts
    ├── components/
    │   └── ParallaxForest.tsx  # Mouse-based parallax
    └── public/
        └── assets/          # Parallax forest images
            ├── parallax-forest-1.png
            ├── parallax-forest-2.png
            ├── parallax-forest-3.png
            └── parallax-forest-4.png
```

## API Integration

Frontend connects to backend via:
- **REST API**: Quest creation, sprint execution, campfire
- **WebSockets**: Real-time updates during quest execution

### Endpoints Used:
- `POST /quest/create` - Create new quest
- `GET /quest/{id}` - Get quest status
- `POST /quest/{id}/sprint/execute` - Execute sprint
- `POST /quest/{id}/campfire` - Trigger campfire
- `WS /ws/quest/{id}` - Real-time updates

## Backend Changes

### Updated `epic/api/server.py`:
```python
# Added CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Updated `epic/core/claude_agent.py`:
```python
# Added simulation_mode parameter
def __init__(self, ..., simulation_mode: bool = False):
    if not simulation_mode:
        # Only create API client if not in simulation
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
```

### Updated `epic/core/party.py`:
```python
# Added simulation_mode parameter
def assemble(cls, roles: Optional[List[str]] = None, simulation_mode: bool = False):
    return cls(roles, simulation_mode)
```

## Testing

### Without AI (Simulation Mode):
```bash
cd ~/Documents/Github/Ergo/Project_Epic
python test_standalone.py
```

### With Frontend:
1. Start backend: `python -m epic.api.server`
2. Start frontend: `cd frontend && npm run dev`
3. Open: http://localhost:3000
4. Create a quest and execute sprints

## Customization

### Adjust Parallax Speed
Edit `frontend/components/ParallaxForest.tsx`:
```typescript
const maxOffset = 50; // Increase for more movement
```

### Change Depth Factors
```typescript
getParallaxStyle(0.3)  // Layer 4 (slowest)
getParallaxStyle(0.5)  // Layer 3
getParallaxStyle(0.8)  // Layer 2
getParallaxStyle(1.2)  // Layer 1 (fastest)
```

### Modify Colors
Edit `frontend/app/page.tsx` and change Tailwind classes:
- Gold: `text-[#e9c349]` or `bg-[#e9c349]`
- Dark: `bg-[#131313]`
- Surface: `bg-[#1c1b1b]`
- Borders: `border-[#434843]`

## What You Can Do Now

1. **Create Quests**: Select party and enter goal
2. **Execute Sprints**: Click "Execute Sprint" to run current sprint
3. **View Progress**: See real-time progress bar and budget tracking
4. **Campfire**: Trigger business checkpoints
5. **Multiple Quests**: Create new quests anytime
6. **Mouse Parallax**: Move mouse to explore the forest scene

## Next Steps

### For Real AI Execution:
1. Add API key to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. Update `epic/core/party.py` to remove `simulation_mode=True`

3. Execute sprints will actually call Claude agents!

### Future Enhancements:
- [ ] Add sprite animations for party members
- [ ] Implement quest history / save system
- [ ] Add sound effects and music
- [ ] Create sprite selection for party members
- [ ] Add campfire dialogue visualization
- [ ] Implement quest log with detailed history

## Troubleshooting

### "Failed to fetch" Error:
- Make sure backend is running at localhost:8766
- Check CORS is enabled in server.py

### Images Not Loading:
- Verify images are in `frontend/public/assets/`
- Check Next.js is serving from correct port (3000)

### Progress Shows NaN%:
- This should be fixed now with proper Quest data structure
- Backend returns `progress` as float (0-100)

### WebSocket Errors:
- Backend must be running
- Check WebSocket URL matches backend port

## Summary

You now have a fully functional Next.js frontend with:
- ✅ Mouse-based parallax forest (your custom assets!)
- ✅ HD-2D Octopath Traveler aesthetic
- ✅ Full quest management UI
- ✅ Working execute sprint button
- ✅ Proper progress tracking
- ✅ Real-time WebSocket updates
- ✅ TypeScript for type safety
- ✅ Responsive design

**Time to embark on your epic quests!** ⚔️
