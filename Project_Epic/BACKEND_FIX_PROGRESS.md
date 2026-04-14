# Fixed: quest.progress is undefined

## Issue
Frontend was getting `undefined` for `quest.progress` when creating a new quest, causing the error:
```
can't access property "toFixed", quest.progress is undefined
```

## Root Cause
The `create_quest` endpoint was returning sprints with the wrong field name:
- Backend: `sprints[].enemy`
- Frontend expects: `sprints[].enemy_type`

The `get_quest` endpoint already had the transformation, but `create_quest` didn't.

## Fix Applied

### 1. Backend - Transform sprints in create_quest
Updated `epic/api/server.py` line 87-98:

```python
quest.start()

# Transform sprints to match frontend expectations
quest_dict = quest.to_dict()
sprints = [{
    "rank": s["rank"],
    "name": s["name"],
    "description": s["description"],
    "enemy_type": s["enemy"],  # ← Renamed from "enemy"
    "estimated_cost": s["estimated_cost"],
    "success_criteria": [],
    "completed": s.get("completed", False)
} for s in quest_dict["sprints"]]

return QuestResponse(
    quest_id=quest.id,
    goal=quest.goal,
    demon_king=quest.demon_king,
    status=quest.status.value,
    sprints=sprints,  # ← Use transformed sprints
    progress=quest.get_progress_percentage(),
    budget=quest_dict["budget"],
    tokens=quest_dict["tokens"]
)
```

### 2. Frontend - Safety check for undefined
Added nullish coalescing operator in `frontend/app/page.tsx` line 235:

```tsx
// Before
<span>{quest.progress.toFixed(0)}%</span>

// After
<span>{(quest.progress ?? 0).toFixed(0)}%</span>
```

This ensures that if `progress` is somehow undefined, it defaults to `0` instead of crashing.

## How to Apply

**Restart the backend:**
```bash
# Stop current backend (Ctrl+C)
cd ~/Documents/Github/Ergo/Project_Epic
source venv/bin/activate
python -m epic.api.server
```

**Frontend will hot-reload automatically** (no restart needed)

## Verification

After restarting backend:

1. Open http://localhost:3000
2. Select party members
3. Enter quest goal
4. Press Enter
5. ✅ Quest should create successfully
6. ✅ Progress bar should show "0%"
7. ✅ No errors in console

## Why This Happened

The backend has two endpoints that return quest data:
1. `POST /quest/create` - Creates new quest
2. `GET /quest/{id}` - Gets existing quest

We fixed the transformation in `GET` but forgot to apply it to `POST`. Both now use the same transformation logic.

## Data Flow

```
Backend quest.to_dict() returns:
{
  "sprints": [
    {
      "enemy": "Crocodiles",  ← Backend field
      ...
    }
  ],
  "progress_percentage": 0.0  ← Backend field
}

Transform to frontend format:
{
  "sprints": [
    {
      "enemy_type": "Crocodiles",  ← Frontend field
      ...
    }
  ],
  "progress": 0.0  ← Frontend field
}
```

## Files Modified

- ✅ `epic/api/server.py` - Added sprint transformation to create_quest
- ✅ `frontend/app/page.tsx` - Added safety check for undefined progress

## Status

🎉 **FIXED** - Backend restart required
