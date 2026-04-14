# Animated Sprite Slot Selection

## What Changed

### Previous Design:
- Contained boxes with emoji icons
- Static display
- Bordered container around slots
- Simple hover effects

### New Design:
- **Animated idle sprites** (knight & mage)
- **Floating on background** (no container)
- **Circular shadows** beneath each slot
- **More separated** horizontal layout (gap-20)
- **Hover lift effect** - slots rise when hovered
- **Empty slots** show glowing circular + symbol

## Features

### 1. Animated Sprites
Each selected role shows an animated idle sprite:

**Knight-based roles** (6 frames):
- Tank (🛡️) → Knight idle animation
- Rogue (🗡️) → Knight idle animation
- Planner (🗺️) → Knight idle animation

**Mage-based roles** (9 frames):
- Mage (🧙) → Mage idle animation
- Support (📚) → Mage idle animation
- Healer (✨) → Mage idle animation

Frame delay: 150ms between frames

### 2. Circular Shadows
- Each slot has a circular shadow beneath it
- `w-20 h-6` elliptical shadow
- `bg-black/40 blur-sm` for soft shadow effect
- Positioned at bottom center of slot

### 3. Floating Effect
- No container box around slots
- Transparent background
- Floats directly on parallax forest
- Hover: Slot lifts up 8px (`translate-y-[-8px]`)
- Smooth transitions

### 4. Empty Slot Design
- **Circular border** instead of square
- **Glowing + symbol** on hover
- Pulses and scales on hover
- Gold glow effect when hovered
- Larger + symbol (text-7xl)

### 5. Separation
- Increased gap from `gap-6` to `gap-20`
- More breathing room between slots
- Better visual hierarchy

## Sprite Assets Used

### Knight Idle:
```
/app/assets/knight/Sprites/Idle/
  - Idle1.png
  - Idle2.png
  - Idle3.png
  - Idle4.png
  - Idle5.png
  - Idle6.png
```

### Mage Idle:
```
/app/assets/mage/Sprites/Idle/
  - Idle1.png
  - Idle2.png
  - Idle3.png
  - Idle4.png
  - Idle5.png
  - Idle6.png
  - Idle7.png
  - Idle8.png
  - Idle9.png
```

## Technical Implementation

### New Components:

**AnimatedSprite.tsx**
- Cycles through sprite frames
- Uses `useEffect` with `setInterval`
- Configurable frame count and delay
- Maps role IDs to sprite paths
- Pixelated image rendering

**PartySlotSelector.tsx** (updated)
- Removed container box
- Added circular shadows
- Implemented floating hover effect
- Integrated AnimatedSprite component
- Larger sprite display (160x160px)

### Animation Logic:

```tsx
useEffect(() => {
  const interval = setInterval(() => {
    setCurrentFrame((prev) => (prev % frameCount) + 1);
  }, frameDelay);

  return () => clearInterval(interval);
}, [frameCount, frameDelay]);
```

Cycles from frame 1 → frameCount → back to 1

### Hover Effects:

**Selected slot hover:**
```tsx
${isHovered ? 'translate-y-[-8px]' : 'translate-y-0'}
${isHovered ? 'drop-shadow-[0_0_15px_rgba(233,195,73,0.6)]' : ''}
```
- Lifts 8px upward
- Gold glow shadow appears

**Empty slot hover:**
```tsx
${isHovered
  ? 'border-[#e9c349] bg-[#e9c349]/10 shadow-[0_0_30px_rgba(233,195,73,0.4)]'
  : 'border-[#434843] bg-transparent'
}
```
- Border turns gold
- Background gets subtle gold tint
- Large outer glow

## Visual Hierarchy

```
┌────────────────────────────────────────────┐
│                                            │
│       Enter your quest... (input)          │
│       ─────────────────────────────        │
│                                            │
│       Select Your Party (text only)        │
│                                            │
│   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│   │ [🏃]  │  │  (+)  │  │ [🧙]  │  │  (+)  │
│   │  ◯    │  │  ◯    │  │  ◯    │  │  ◯    │
│   │ TANK  │  │SLOT 2 │  │ MAGE  │  │SLOT 4 │
│   └───────┘  └───────┘  └───────┘  └───────┘
│                                            │
│   (Shadows beneath each slot)              │
│                                            │
└────────────────────────────────────────────┘

Legend:
[🏃] = Animated knight sprite
[🧙] = Animated mage sprite
(+) = Glowing plus in circle
◯ = Circular shadow
```

## Styling Details

### Circular Shadow:
```tsx
<div className="absolute bottom-0 left-1/2 -translate-x-1/2
  w-20 h-6 rounded-full bg-black/40 blur-sm" />
```

### Empty Slot Circle:
```tsx
<div className="w-32 h-32 border-2 rounded-full
  flex items-center justify-center">
```

### Floating Container:
```tsx
<div className={`
  relative cursor-pointer transition-all duration-300
  ${isHovered ? 'translate-y-[-8px]' : 'translate-y-0'}
  ${isOpen ? 'scale-110' : 'scale-100'}
`}>
```

### Remove Button (now circular):
```tsx
<button className="absolute -top-2 -right-2
  w-6 h-6 rounded-full bg-red-900/80 border border-red-500">
  ✕
</button>
```

## Customization

### Change Animation Speed:
```tsx
// In AnimatedSprite.tsx
frameDelay = 150  // Default (faster)
frameDelay = 200  // Slower
frameDelay = 100  // Faster
```

### Change Sprite Size:
```tsx
// In PartySlotSelector.tsx
<AnimatedSprite
  width={160}   // Default
  height={160}
  // Or larger:
  width={200}
  height={200}
/>
```

### Change Slot Spacing:
```tsx
// In PartySlotSelector.tsx
<div className="flex justify-center gap-20">  // Default
<div className="flex justify-center gap-24">  // More space
<div className="flex justify-center gap-16">  // Less space
```

### Change Shadow Size:
```tsx
<div className="w-20 h-6">  // Default
<div className="w-24 h-8">  // Larger shadow
<div className="w-16 h-4">  // Smaller shadow
```

### Change Hover Lift:
```tsx
${isHovered ? 'translate-y-[-8px]' : 'translate-y-0'}
// More lift:
${isHovered ? 'translate-y-[-12px]' : 'translate-y-0'}
```

## Role to Sprite Mapping

```tsx
const spriteMap = {
  'tank': 'knight',     // 6 frames
  'mage': 'mage',       // 9 frames
  'planner': 'knight',  // 6 frames
  'rogue': 'knight',    // 6 frames
  'support': 'mage',    // 9 frames
  'healer': 'mage',     // 9 frames
};
```

## Files Modified/Created

- ✅ `frontend/components/AnimatedSprite.tsx` (NEW)
- ✅ `frontend/components/PartySlotSelector.tsx` (UPDATED)
- ✅ `frontend/app/page.tsx` (UPDATED)
- ✅ `frontend/app/globals.css` (UPDATED - pixelated class)

## Assets Required

Sprites automatically loaded from:
- `/app/assets/knight/Sprites/Idle/Idle[1-6].png`
- `/app/assets/mage/Sprites/Idle/Idle[1-9].png`

Both already exist in your assets folder! ✓

## Hot Reload

Frontend should auto-reload and show animated sprites! 🎮

## Next Steps (Optional)

- [ ] Add attack animations on selection
- [ ] Add sound effects for idle/selection
- [ ] Add more sprite variety (other character types)
- [ ] Animate transition when selecting/deselecting
- [ ] Add particle effects around selected characters
- [ ] Implement character "bounce" on idle
