# Project Epic - Frontend

Next.js + TypeScript frontend for Project Epic with HD-2D parallax forest background and mouse-based camera movement.

## Features

- ✨ **Mouse-Based Parallax** - Move your mouse to look around the parallax forest layers
- 🎨 **HD-2D Aesthetic** - Octopath Traveler-inspired visual style
- ⚔️ **Quest Creation** - Select up to 4 party members and create epic quests
- 📊 **Real-Time Progress** - WebSocket updates for sprint execution
- 🏕️ **Campfire System** - Business alignment checkpoints

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser
http://localhost:3000
```

## Requirements

- Node.js 18+
- Backend server running at `http://localhost:8766`

## Backend Connection

The frontend connects to the FastAPI backend at `http://localhost:8766`. Make sure the backend is running:

```bash
# In Project_Epic root directory
cd ..
source venv/bin/activate
python -m epic.api.server
```

## Components

### ParallaxForest
The main parallax background component with 4 forest layers that move based on mouse position:
- Layer 4 (furthest): slowest movement
- Layer 3 (mid-back): medium-slow
- Layer 2 (mid-front): medium-fast
- Layer 1 (closest): fastest movement

### Main Page
Quest creation and management interface with:
- Party member selection (up to 4)
- Quest goal input
- Sprint visualization
- Execute sprint / Campfire buttons
- Real-time progress tracking

## API Endpoints Used

- `POST /quest/create` - Create new quest
- `GET /quest/{quest_id}` - Get quest status
- `POST /quest/{quest_id}/sprint/execute` - Execute current sprint
- `POST /quest/{quest_id}/campfire` - Trigger campfire gathering
- `WS /ws/quest/{quest_id}` - WebSocket for real-time updates

## Assets

Parallax forest images are located in `public/assets/`:
- `parallax-forest-1.png` (foreground)
- `parallax-forest-2.png`
- `parallax-forest-3.png`
- `parallax-forest-4.png` (background)

## Development

```bash
# Run development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Customization

### Change API URL
Edit `frontend/app/page.tsx`:
```typescript
const API_BASE = 'http://your-backend-url:port';
```

### Adjust Parallax Speed
Edit `frontend/components/ParallaxForest.tsx`:
```typescript
const maxOffset = 50; // Increase for more movement
```

### Modify Theme Colors
Colors follow the HD-2D palette defined in the template:
- Primary: `#e9c349` (gold)
- Background: `#131313` (dark)
- Surface: `#1c1b1b` (card background)
- Text: `#e5e2e1` (light gray)

## Tech Stack

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **WebSockets** - Real-time updates
- **Newsreader** - Display font
- **Inter** - Body font
