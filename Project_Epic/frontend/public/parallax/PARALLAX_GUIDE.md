# Parallax Assets Guide

**Purpose:** This directory contains parallax layer images for each zone in the Living World.

---

## Directory Structure

```
parallax/
├── campfire/              # The Campfire - Planning & Review
│   ├── far_background/    # Layer 1: Sky, distant scenery (depth: 0.2)
│   ├── mid_background/    # Layer 2: Trees, structures (depth: 0.5)
│   ├── foreground/        # Layer 3: Fire, logs, close objects (depth: 0.8)
│   └── overlay/           # Layer 4: Particles, effects (depth: 1.0)
│
├── forge/                 # The Forge - Debugging & Fixing
│   ├── far_background/    # Mountains, dark sky
│   ├── mid_background/    # Forge building exterior
│   ├── foreground/        # Anvil, bellows, tools
│   └── overlay/           # Sparks, heat shimmer
│
├── arena/                 # The Proving Grounds - Testing
│   ├── far_background/    # Arena walls, sky
│   ├── mid_background/    # Banners, seating
│   ├── foreground/        # Training dummies, scoreboard
│   └── overlay/           # Dust, combat effects
│
├── library/               # The Grand Archive - Documentation
│   ├── far_background/    # Library interior, windows
│   ├── mid_background/    # Bookshelves, architecture
│   ├── foreground/        # Desk, candles, books
│   └── overlay/           # Candlelight glow, papers
│
├── guild_hall/            # The Guild Hall - Quest Management
│   ├── far_background/    # Hall interior, windows
│   ├── mid_background/    # Quest board, furniture
│   ├── foreground/        # Table, chairs, scrolls
│   └── overlay/           # Quest markers, UI elements
│
├── tavern/                # The Rusty Compile - Rest & Celebration
│   ├── far_background/    # Tavern interior
│   ├── mid_background/    # Bar, tables, fireplace
│   ├── foreground/        # Mugs, decorations
│   └── overlay/           # Fireplace glow, celebration effects
│
├── inn/                   # The Stack Overflow Inn - Idle Rest
│   ├── far_background/    # Inn room, window view
│   ├── mid_background/    # Beds, furniture
│   ├── foreground/        # Chest, personal items
│   └── overlay/           # Moonlight, peaceful effects
│
├── dungeon/               # The Dungeon Gate - Active Sprints
│   ├── far_background/    # Dark cavern, portal glow
│   ├── mid_background/    # Stone gate, architecture
│   ├── foreground/        # Torches, danger signs
│   └── overlay/           # Portal effects, ominous particles
│
├── graveyard/             # The Deprecated Grounds - Failed Quests
│   ├── far_background/    # Dead trees, foggy sky
│   ├── mid_background/    # Tombstones, memorials
│   ├── foreground/        # Fog, grass, stones
│   └── overlay/           # Fog particles, somber effects
│
└── market/                # The Package Bazaar - Dependencies
    ├── far_background/    # Market backdrop
    ├── mid_background/    # Stalls, structures
    ├── foreground/        # Crates, packages, merchant
    └── overlay/           # Busy atmosphere, item highlights
```

---

## Image Specifications

### File Format
- **Format:** PNG with transparency
- **Bit depth:** 32-bit RGBA
- **Compression:** Optimize for web (use tools like TinyPNG)

### Dimensions
- **Width:** 1920px (full HD width)
- **Height:** 1080px (full HD height)
- **Aspect ratio:** 16:9

### Layer Guidelines

#### Far Background (depth: 0.2)
- Slowest movement
- Distant scenery: mountains, sky, far structures
- Low detail, atmospheric
- **Example:** `campfire/far_background/sky.png`

#### Mid Background (depth: 0.5)
- Moderate movement
- Middle-distance objects: trees, buildings, terrain
- Medium detail
- **Example:** `campfire/mid_background/forest.png`

#### Foreground (depth: 0.8)
- Fast movement
- Close objects: main zone features, furniture, props
- High detail
- **Example:** `campfire/foreground/logs_and_fire.png`

#### Overlay (depth: 1.0)
- Full movement (1:1 with camera)
- Effects: particles, UI elements, lighting
- Transparency-heavy
- **Example:** `campfire/overlay/fire_particles.png`

---

## Aesthetic Style

### Overall Look
- **Octopath Traveler HD-2D inspired**
- Pixel art feel with modern lighting
- Rich depth through layering
- Atmospheric and moody

### Color Palette (by confidence level)

#### High Confidence (≥ 0.8)
- Bright, warm colors
- Golden hour lighting
- Saturated greens and blues
- **Mood:** Optimistic, energetic

#### Normal (0.5 - 0.8)
- Balanced, neutral tones
- Overcast lighting
- Earthy colors
- **Mood:** Focused, steady

#### Low (0.3 - 0.5)
- Muted, desaturated
- Foggy atmosphere
- Grey-greens, browns
- **Mood:** Concerning, tense

#### Critical (< 0.3)
- Dark, ominous
- Storm lighting
- Deep shadows, minimal light
- **Mood:** Crisis, danger

---

## Zone-Specific Art Direction

### Campfire
- Warm firelight glow
- Forest clearing
- Strategic planning atmosphere
- **Key elements:** Fire animation, logs, map, planning board

### Forge
- Hot, intense lighting
- Industrial medieval setting
- Sparks and heat effects
- **Key elements:** Anvil, bellows, glowing metal, tools

### Arena
- Bright, open space
- Competitive atmosphere
- Dynamic, active
- **Key elements:** Training dummies, scoreboard, banners

### Library
- Soft candlelight
- Scholarly, quiet
- Warm wood tones
- **Key elements:** Bookshelves, desk, candles, scrolls

### Guild Hall
- Organized, official
- Quest board focal point
- Professional atmosphere
- **Key elements:** Quest board, table, guild banner

### Tavern
- Cozy, lively
- Fireplace warmth
- Celebratory decorations
- **Key elements:** Bar, tables, fireplace, mugs

### Inn
- Peaceful, restful
- Moonlit ambiance
- Quiet and safe
- **Key elements:** Beds, window, chest

### Dungeon
- Dark, mysterious
- Portal glow (purple/blue)
- Ominous but exciting
- **Key elements:** Stone gate, torches, glowing portal

### Graveyard
- Somber, respectful
- Fog and mist
- Lessons learned
- **Key elements:** Tombstones, dead trees, fog

### Market
- Busy, colorful
- Package/crate theme
- Organized chaos
- **Key elements:** Stalls, crates, merchant, packages

---

## Implementation Notes

### File Naming Convention
```
{zone_name}/{layer_name}/{element_name}.png

Examples:
campfire/far_background/night_sky.png
campfire/mid_background/forest_trees.png
campfire/foreground/fire_and_logs.png
campfire/overlay/fire_particles.png
```

### Parallax Depth Values
- Far background: `0.2` (moves 20% of mouse/camera)
- Mid background: `0.5` (moves 50%)
- Foreground: `0.8` (moves 80%)
- Overlay: `1.0` (moves 100%)

### Animation Considerations
- Fire flicker (campfire, tavern, forge)
- Sparks (forge)
- Fog movement (graveyard, low confidence)
- Portal glow (dungeon)
- Candle flames (library)

These can be sprite sheets or separate animated layers.

---

## Placeholder Assets (Current)

For development, we're using:
- **Solid colors** for each layer
- **Text labels** indicating zone and layer
- **CSS gradients** for basic depth

### Placeholder Colors by Zone

**Campfire:**
- Far: `#1a1a2e` (night sky)
- Mid: `#16213e` (forest silhouette)
- Fore: `#533b4d` (warm glow)
- Over: `rgba(255, 140, 0, 0.3)` (fire glow)

**Forge:**
- Far: `#2a1a1a`
- Mid: `#3a2a2a`
- Fore: `#4a3a2a`
- Over: `rgba(255, 100, 0, 0.4)` (sparks)

**Arena:**
- Far: `#2a3a4a`
- Mid: `#3a4a5a`
- Fore: `#4a5a6a`
- Over: `rgba(255, 255, 255, 0.2)` (dust)

*(See zones.json for complete palette information)*

---

## Getting Started

### For Artists:

1. **Review** this guide and zones.json
2. **Pick a zone** to start with (campfire recommended)
3. **Sketch** the overall composition
4. **Create layers** at 1920x1080, 32-bit PNG
5. **Test** in frontend with parallax effect
6. **Iterate** based on depth and mood

### For Developers:

1. **Use placeholders** (already set up)
2. **Implement parallax** in frontend components
3. **Test layer movement** with mouse parallax
4. **Wire confidence system** to palette swapping
5. **Add agent sprites** that move between zones

---

## Reference Images

*(Add reference images here once collected)*

- Octopath Traveler screenshots
- Fantasy RPG environments
- Pixel art parallax examples
- Medieval/fantasy atmospheres

---

## Questions & Decisions

1. **Pixel density:** Pure pixel art vs. HD-2D hybrid?
2. **Animation frames:** Separate files or sprite sheets?
3. **Weather effects:** Rain/snow for low confidence?
4. **Time of day:** Should it change during quests?
5. **Character scale:** How big should agents be relative to environment?

---

**Last Updated:** 2026-03-30
**Status:** Directory structure created, awaiting assets
**Priority:** Campfire (highest), Tavern (second), then others

---

**"Each zone tells a story. Each layer adds depth. Together, they create a living world."**
