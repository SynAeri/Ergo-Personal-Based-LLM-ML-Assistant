# New Slot-Based Party Selection UI

## What Changed

### Previous Design:
- Grid of 6 clickable cards with party roles
- Button-based selection (click to toggle)
- Separate "Begin Quest" button
- Cluttered screen with all information visible

### New Design:
- **4 Horizontal Slots** for party selection
- **Hover-activated glowing "+"** for empty slots
- **Minimal dropdown menus** with expandable role details
- **Quest input at top** - no button, press Enter to begin
- **Clean, minimal aesthetic** with reduced clutter

## Features

### 1. Horizontal Slot System
- 4 slots displayed horizontally
- Empty slots show a **glowing "+"** on hover
- Selected slots display role icon and name
- Small ✕ button to remove selected roles

### 2. Dropdown Role Selection
- Click empty slot to open dropdown
- List of available roles (not already selected)
- Click role to expand and see details:
  - **Skills**: List of Claude tools available to this role
  - **Personality**: Full personality prompt
  - **Description**: Role overview
- Click "SELECT" button to confirm choice

### 3. Minimal Quest Input
- Single text input at top of screen
- Centered, transparent background
- Border only at bottom
- **Press Enter** to create quest (no button!)
- Placeholder: "Enter your quest..."

### 4. Role Details in Dropdown

Each role now shows:

#### Planner 🗺️
- **Skills**: Create Plan, Search Memory, Read File, Search Code
- **Personality**: Scout and strategist, measured voice, never writes code
- **Role**: Creates plans and identifies paths forward

#### Mage 🧙
- **Skills**: Read File, Search Code, Create Plan, Write File
- **Personality**: Architect with wisdom, makes high-level decisions
- **Role**: Designs system architecture and patterns

#### Rogue 🗡️
- **Skills**: Write File, Edit File, Read File, Search Code, Run Command
- **Personality**: Action-oriented executor, combat metaphors
- **Role**: Implements code and executes features

#### Tank 🛡️
- **Skills**: Run Tests, Run Command, Read File, Search Code
- **Personality**: Protective guardian, questions and validates
- **Role**: Tests code and ensures quality

#### Support 📚
- **Skills**: Read File, Search Code, Search Memory, Write File
- **Personality**: Scholar and documentarian, clarity focused
- **Role**: Documents code and provides knowledge

#### Healer ✨
- **Skills**: Edit File, Read File, Search Code, Run Tests
- **Personality**: Calm optimizer, healing metaphors
- **Role**: Refactors and optimizes code

## User Flow

### Before Quest Creation:

1. **Enter quest goal** in minimal input at top
2. **Hover over empty slot** → + glows
3. **Click slot** → Dropdown opens with available roles
4. **Click role** → Details collapse to show
5. **Review skills and personality** → Understand role capabilities
6. **Click "SELECT [ROLE]"** → Role assigned to slot
7. **Repeat** for up to 4 slots
8. **Press Enter** in quest input → Quest created!

### After Selection:

- Slots show selected role icons and names
- Small ✕ button on each slot to remove
- Click slot again to change selection
- Enter key always available to start quest

## Technical Implementation

### Components:

1. **PartySlotSelector.tsx** (new)
   - Manages 4-slot horizontal layout
   - Handles dropdown state
   - Shows role details with expand/collapse
   - Integrates personality prompts and skills

2. **page.tsx** (updated)
   - Minimal quest input at top
   - No "Begin Quest" button (Enter key only)
   - Cleaner layout with more breathing room
   - Party state as array: `[null, null, null, null]`

### State Management:

```tsx
// Previous
const [selectedParty, setSelectedParty] = useState<string[]>([]);

// New
const [selectedParty, setSelectedParty] = useState<(string | null)[]>([null, null, null, null]);
```

### Key Features:

- **Dropdown closes automatically** after selection
- **Can't select same role twice** (filtered from dropdowns)
- **Visual feedback**: Hover effects, glowing +, shadows
- **Expandable details**: Click to expand, click again to select
- **Remove anytime**: Small ✕ button on filled slots

## Styling

### Empty Slot:
```tsx
- Border: #434843 (dark gray)
- Background: #131313/60 (very transparent)
- Hover: Border changes to #e9c349 (gold)
- + symbol: Glows and pulses on hover
```

### Filled Slot:
```tsx
- Border: #e9c349 (gold)
- Background: #1c1b1b/90 (semi-transparent)
- Icon: Large emoji (5xl)
- Name: Small gold text
- Remove: Small red ✕ in corner
```

### Dropdown:
```tsx
- Background: #1c1b1b (solid)
- Border: #434843
- Shadow: Large dark shadow for depth
- Width: 320px
- Max height: 384px (scrollable)
```

### Quest Input:
```tsx
- Background: Transparent
- Border: Bottom only, #434843
- Focus: Bottom border → #e9c349
- Text: 2xl, centered
- Font: Newsreader (fancy serif)
```

## Visual Hierarchy

```
┌──────────────────────────────────────┐
│        PROJECT EPIC (header)         │
├──────────────────────────────────────┤
│                                      │
│     Enter your quest... (input)      │
│     ___________________________      │
│                                      │
├──────────────────────────────────────┤
│                                      │
│      SELECT YOUR PARTY (heading)     │
│                                      │
│   ┌───┐  ┌───┐  ┌───┐  ┌───┐      │
│   │ + │  │ + │  │ + │  │ + │      │
│   └───┘  └───┘  └───┘  └───┘      │
│                                      │
│   Dropdown appears on click ↓        │
│   ┌─────────────────────┐           │
│   │ 🗺️ Planner          │           │
│   │ 🧙 Mage             │           │
│   │ 🗡️ Rogue            │           │
│   └─────────────────────┘           │
│                                      │
└──────────────────────────────────────┘
```

## Benefits

1. **Less Clutter**: Only shows details when needed
2. **Better UX**: Hover → Click → Expand → Select flow
3. **More Information**: Full personality prompts visible
4. **Cleaner Look**: Minimal, focused design
5. **Faster Input**: Press Enter to start (no button click)
6. **Mobile Friendly**: Dropdowns work well on touch devices
7. **Visual Feedback**: Glowing effects guide user interaction

## Customization

### Change Slot Size:
```tsx
// In PartySlotSelector.tsx
className="w-32 h-32"  // Default 128x128px
className="w-40 h-40"  // Larger 160x160px
```

### Change Dropdown Width:
```tsx
<div className="w-80">  // Default 320px
<div className="w-96">  // Larger 384px
```

### Adjust Glow Effect:
```tsx
className={isHovered
  ? 'text-[#e9c349] animate-pulse scale-110'  // Current
  : 'text-[#434843]'
}

// Stronger glow:
? 'text-[#e9c349] animate-pulse scale-125 drop-shadow-[0_0_10px_rgba(233,195,73,0.8)]'
```

### Change Slot Spacing:
```tsx
<div className="flex justify-center gap-6">  // Default 24px
<div className="flex justify-center gap-8">  // More space 32px
```

## Files Modified

- ✅ `frontend/components/PartySlotSelector.tsx` (NEW)
- ✅ `frontend/app/page.tsx` (UPDATED)

## Hot Reload

Changes are live! The frontend automatically reloads. 🔥

## Next Steps (Optional)

- [ ] Add animations when selecting roles
- [ ] Add sound effects on selection
- [ ] Add sprite images for each role
- [ ] Animate dropdown opening/closing
- [ ] Add tooltips for skills
- [ ] Persist party selection in localStorage
