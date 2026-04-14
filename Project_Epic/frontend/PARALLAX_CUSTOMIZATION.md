# Parallax Forest Customization Guide

## Layer Size & Appearance Modifiers

The `ParallaxForest` component now supports per-layer customization!

## Basic Usage (Current Default)

```tsx
<ParallaxForest>
  {/* Your content */}
</ParallaxForest>
```

## Customizing Individual Layers

### Scale Modifier

Change the size of specific layers:

```tsx
<ParallaxForest
  layer1={{ scale: 1.5 }}    // Make foreground 150% size
  layer2={{ scale: 1.2 }}    // Make mid-foreground 120% size
  layer3={{ scale: 0.8 }}    // Make mid-background 80% size
  layer4={{ scale: 1.0 }}    // Keep background at 100% (default)
>
  {/* Your content */}
</ParallaxForest>
```

### Opacity Modifier

Adjust transparency of layers:

```tsx
<ParallaxForest
  layer1={{ opacity: 1.0 }}   // Fully opaque (default for layer 1)
  layer2={{ opacity: 0.85 }}  // 85% opacity (default)
  layer3={{ opacity: 0.7 }}   // 70% opacity (default)
  layer4={{ opacity: 0.6 }}   // 60% opacity (default)
>
  {/* Your content */}
</ParallaxForest>
```

### Object Fit

Control how images fill their container:

```tsx
<ParallaxForest
  layer1={{ objectFit: 'cover' }}    // Fill and crop (default)
  layer2={{ objectFit: 'contain' }}  // Fit without cropping
  layer3={{ objectFit: 'fill' }}     // Stretch to fill
  layer4={{ objectFit: 'none' }}     // Original size
>
  {/* Your content */}
</ParallaxForest>
```

### Combined Configuration

```tsx
<ParallaxForest
  layer1={{
    scale: 1.3,
    opacity: 0.95,
    objectFit: 'cover'
  }}
  layer2={{
    scale: 1.1,
    opacity: 0.8,
    objectFit: 'cover'
  }}
  layer3={{
    scale: 0.9,
    opacity: 0.6,
    objectFit: 'contain'
  }}
  layer4={{
    scale: 0.8,
    opacity: 0.5,
    objectFit: 'cover'
  }}
>
  {/* Your content */}
</ParallaxForest>
```

## Global Parallax Settings

### Max Offset

Control how far layers move:

```tsx
<ParallaxForest
  maxOffset={100}  // Layers move up to 100px (default: 50)
>
  {/* Your content */}
</ParallaxForest>
```

### Parallax Speed

Speed up or slow down all layer movement:

```tsx
<ParallaxForest
  parallaxSpeed={2.0}   // 2x faster movement
  // parallaxSpeed={0.5}  // Half speed
  // parallaxSpeed={0}    // No parallax (static)
>
  {/* Your content */}
</ParallaxForest>
```

## Complete Example

```tsx
<ParallaxForest
  // Layer configurations (furthest to closest)
  layer4={{
    scale: 0.8,        // Smaller background
    opacity: 0.4,      // More transparent
    objectFit: 'cover'
  }}
  layer3={{
    scale: 0.9,
    opacity: 0.6,
    objectFit: 'cover'
  }}
  layer2={{
    scale: 1.2,        // Slightly larger
    opacity: 0.85,
    objectFit: 'cover'
  }}
  layer1={{
    scale: 1.5,        // Much larger foreground
    opacity: 1.0,      // Fully opaque
    objectFit: 'cover'
  }}
  // Global settings
  maxOffset={75}       // More movement
  parallaxSpeed={1.5}  // Faster parallax
>
  {/* Your quest interface */}
</ParallaxForest>
```

## Layer Reference

- **Layer 4** (furthest): `parallax-forest-4.png` - Background, slowest movement (0.3x)
- **Layer 3**: `parallax-forest-3.png` - Mid-background, slow movement (0.5x)
- **Layer 2**: `parallax-forest-2.png` - Mid-foreground, medium movement (0.8x)
- **Layer 1** (closest): `parallax-forest-1.png` - Foreground, fastest movement (1.2x)

## Tips

### Making Layers Appear Larger

```tsx
layer1={{ scale: 1.5 }}  // Layer appears 50% larger
```

### Making Layers Appear Smaller

```tsx
layer4={{ scale: 0.7 }}  // Layer appears 30% smaller
```

### Fading Distant Layers

```tsx
layer4={{ opacity: 0.3 }}  // Very faint background
layer3={{ opacity: 0.5 }}  // Faded mid-background
```

### Subtle Parallax

```tsx
<ParallaxForest
  maxOffset={25}        // Less movement
  parallaxSpeed={0.7}   // Slower
>
```

### Dramatic Parallax

```tsx
<ParallaxForest
  maxOffset={100}       // More movement
  parallaxSpeed={2.0}   // Faster
>
```

### Disable Parallax (Static Background)

```tsx
<ParallaxForest parallaxSpeed={0}>
  {/* Static forest background */}
</ParallaxForest>
```

## Common Scenarios

### Zoom In on Foreground

Make the closest trees much larger:

```tsx
<ParallaxForest
  layer1={{ scale: 2.0, opacity: 0.9 }}  // 2x size, slightly transparent
>
```

### Atmospheric Depth

Emphasize depth by fading distant layers:

```tsx
<ParallaxForest
  layer4={{ scale: 0.7, opacity: 0.3 }}
  layer3={{ scale: 0.85, opacity: 0.5 }}
  layer2={{ scale: 1.0, opacity: 0.8 }}
  layer1={{ scale: 1.2, opacity: 1.0 }}
>
```

### Tight Frame

Make all layers smaller to show more sky/edges:

```tsx
<ParallaxForest
  layer1={{ scale: 0.8 }}
  layer2={{ scale: 0.85 }}
  layer3={{ scale: 0.9 }}
  layer4={{ scale: 0.95 }}
>
```

## Where to Use It

Edit `frontend/app/page.tsx`:

```tsx
import ParallaxForest from '@/components/ParallaxForest';

export default function Home() {
  return (
    <ParallaxForest
      layer1={{ scale: 1.5 }}
      maxOffset={75}
    >
      {/* Your quest interface */}
    </ParallaxForest>
  );
}
```

## Interface Reference

```typescript
interface LayerConfig {
  scale?: number;      // Scale multiplier (1.0 = 100%)
  opacity?: number;    // 0-1 range (0 = transparent, 1 = opaque)
  objectFit?: 'cover' | 'contain' | 'fill' | 'none';
}

interface ParallaxForestProps {
  children?: React.ReactNode;
  layer4?: LayerConfig;       // Furthest layer
  layer3?: LayerConfig;
  layer2?: LayerConfig;
  layer1?: LayerConfig;       // Closest layer
  maxOffset?: number;         // Max pixel offset (default: 50)
  parallaxSpeed?: number;     // Speed multiplier (default: 1.0)
}
```

## Defaults

If you don't specify any configuration, these defaults are used:

```tsx
{
  layer4: { scale: 1.0, opacity: 0.6, objectFit: 'cover' },
  layer3: { scale: 1.0, opacity: 0.7, objectFit: 'cover' },
  layer2: { scale: 1.0, opacity: 0.85, objectFit: 'cover' },
  layer1: { scale: 1.0, opacity: 1.0, objectFit: 'cover' },
  maxOffset: 50,
  parallaxSpeed: 1.0
}
```
