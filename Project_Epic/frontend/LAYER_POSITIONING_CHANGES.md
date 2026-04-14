# Parallax Forest Layer Positioning Changes

## What Was Changed

### 1. Layer 2 Positioning
- **Before**: Layer 2 covered the entire screen (`inset-0`)
- **After**: Layer 2 starts at 25% from the top and extends downward
- **Why**: Positions the middle layer closer to the center of the screen for better visual composition

```tsx
// Layer 2 now positioned in middle
<div
  style={{
    top: '25%',     // Start 25% from top (middle-ish)
    left: '0',
    right: '0',
    height: '100%', // Full height to allow parallax movement
  }}
>
```

### 2. Black Fade Under Layer 2
- **Added**: Gradient fade from black to transparent
- **Position**: Bottom half of screen, sits at same z-index as layer 2
- **Purpose**: Hides trailing assets from layers 1, 3, and 4 when they move

```tsx
<div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black via-black/80 to-transparent" />
```

### 3. Layer 1 Opacity (Sun Ray Effect)
- **Before**: `opacity: 1.0` (fully opaque)
- **After**: `opacity: 0.85` (15% transparent)
- **Why**: Creates sun ray effect by letting background layers show through slightly
- **Benefit**: When layer 1 moves, the trailing edge reveals the lighter background layers, creating a natural light leak effect

## Visual Effect

```
Sky/Light (Layer 4)
      ↓
  [Layer 3]
      ↓
[Layer 2 - positioned at 25% from top]
      ↓
[Black Fade - covers bottom 50%]
      ↓
[Layer 1 - 85% opacity for sun rays]
      ↓
   Your UI
```

### When You Move Mouse:
1. **Layer 1 moves** and becomes slightly transparent
2. **Background layers shine through** (sun ray effect)
3. **Black fade prevents** trailing assets from being visible at bottom
4. **Layer 2 stays centered** in middle region of screen

## Customizing Further

### Adjust Layer 2 Position
```tsx
// Higher up (10% from top)
top: '10%'

// Lower down (40% from top)
top: '40%'

// Centered vertically
top: '50%'
transform: 'translateY(-50%)'
```

### Adjust Black Fade

**Make fade stronger:**
```tsx
className="h-1/2 bg-gradient-to-t from-black via-black/90 to-transparent"
```

**Make fade extend higher:**
```tsx
className="h-2/3 bg-gradient-to-t from-black via-black/70 to-transparent"
```

**Make fade shorter:**
```tsx
className="h-1/3 bg-gradient-to-t from-black via-black/80 to-transparent"
```

### Adjust Sun Ray Effect

**More transparent (stronger sun rays):**
```tsx
layer1={{ opacity: 0.7 }}  // 30% transparent
```

**Less transparent (subtle sun rays):**
```tsx
layer1={{ opacity: 0.95 }}  // 5% transparent
```

**No transparency (no sun ray effect):**
```tsx
layer1={{ opacity: 1.0 }}  // Fully opaque
```

## In Component Usage

```tsx
<ParallaxForest
  layer1={{ opacity: 0.85 }}  // Sun ray effect (default now)
  // To override:
  // layer1={{ opacity: 0.7 }}  // Stronger effect
  // layer1={{ opacity: 1.0 }}  // Disable effect
>
  {/* Your content */}
</ParallaxForest>
```

## File Modified

- `frontend/components/ParallaxForest.tsx`

## Changes Summary

1. ✅ Layer 2 positioned at 25% from top (middle region)
2. ✅ Black gradient fade added under layer 2 (bottom 50%)
3. ✅ Layer 1 now 85% opacity by default (sun ray effect)
4. ✅ Trailing assets hidden by black fade
5. ✅ Light leaks through layer 1 when moving

## Hot Reload

The frontend will automatically reload when you save changes. No restart needed! 🔥
