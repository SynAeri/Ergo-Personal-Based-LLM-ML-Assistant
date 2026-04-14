"use client";

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';

interface LayerConfig {
  scale?: number;      // Scale multiplier (1.0 = 100%, 1.5 = 150%, etc.)
  opacity?: number;    // 0-1 range
  objectFit?: 'cover' | 'contain' | 'fill' | 'none';
}

interface ParallaxForestProps {
  children?: React.ReactNode;
  // Layer-specific configurations (furthest to closest)
  layer4?: LayerConfig;
  layer3?: LayerConfig;
  layer2?: LayerConfig;
  layer1?: LayerConfig;
  // Global parallax settings
  maxOffset?: number;       // Maximum pixel offset for parallax (default: 50)
  parallaxSpeed?: number;   // Global speed multiplier (default: 1.0)
}

export default function ParallaxForest({
  children,
  layer4 = {},
  layer3 = {},
  layer2 = {},
  layer1 = {},
  maxOffset = 50,
  parallaxSpeed = 1.0
}: ParallaxForestProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

  // Default layer configs
  const defaultLayer4 = { scale: 1.0, opacity: 0.6, objectFit: 'cover' as const, ...layer4 };
  const defaultLayer3 = { scale: 1.0, opacity: 0.7, objectFit: 'cover' as const, ...layer3 };
  const defaultLayer2 = { scale: 1.0, opacity: 0.85, objectFit: 'cover' as const, ...layer2 };
  const defaultLayer1 = { scale: 1.0, opacity: 0.6, objectFit: 'cover' as const, ...layer1 }; // Slightly transparent for sun ray effect

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;

      // Normalize mouse position to 0-1 range
      const x = clientX / innerWidth;
      const y = clientY / innerHeight;

      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Calculate parallax offset based on mouse position
  const getParallaxStyle = (depth: number, layerScale: number) => {
    const xOffset = (mousePos.x - 0.5) * maxOffset * depth * parallaxSpeed;
    const yOffset = (mousePos.y - 0.5) * maxOffset * depth * parallaxSpeed;

    return {
      transform: `translate(${xOffset}px, ${yOffset}px) scale(${layerScale})`,
      transition: 'transform 0.1s ease-out',
    };
  };

  return (
    <div ref={containerRef} className="fixed inset-0 z-0 bg-[#0e0e0e] overflow-hidden">
      {/* Layer 4: Furthest back (slowest movement) */}
      <div
        className="absolute inset-0 pointer-events-none z-[1]"
        style={{ ...getParallaxStyle(0.3, defaultLayer4.scale), opacity: defaultLayer4.opacity, top: '-25%' }}
      >
        <Image
          src="/assets/parallax-forest-4.png"
          alt="Forest Background Layer 4"
          fill
          className={`object-${defaultLayer4.objectFit}`}
          style={{
            imageRendering: 'pixelated',
            imageRendering: '-moz-crisp-edges',
            imageRendering: 'crisp-edges',
          }}
          unoptimized
          priority
        />
      </div>

      {/* Layer 3: Mid-background */}
      <div
        className="absolute inset-0 pointer-events-none z-[2]"
        style={{ ...getParallaxStyle(0.5, defaultLayer3.scale), opacity: defaultLayer3.opacity, top: '-20%' }}
      >
        <Image
          src="/assets/parallax-forest-3.png"
          alt="Forest Background Layer 3"
          fill
          className={`object-${defaultLayer3.objectFit}`}
          style={{
            imageRendering: 'pixelated',
            imageRendering: '-moz-crisp-edges',
            imageRendering: 'crisp-edges',
          }}
          unoptimized
        />
      </div>

      {/* Layer 2: Mid-foreground - Positioned in middle of screen */}
      <div
        className="absolute pointer-events-none z-[3]"
        style={{
          top: '-25%',  // Start 25% from top
          left: '0',
          right: '0',
          height: '100%',  // Full height to allow movement
          ...getParallaxStyle(0.8, defaultLayer2.scale),
          opacity: defaultLayer2.opacity
        }}
      >
        <Image
          src="/assets/parallax-forest-2.png"
          alt="Forest Background Layer 2"
          fill
          className={`object-${defaultLayer2.objectFit}`}
          style={{
            imageRendering: 'pixelated',
            imageRendering: '-moz-crisp-edges',
            imageRendering: 'crisp-edges',
          }}
          unoptimized
        />
      </div>

      {/* Black fade under layer 2 to hide trailing assets */}
      <div className="absolute inset-0 z-[3] pointer-events-none">
        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black via-black/80 to-transparent" />
      </div>

      {/* Layer 1: Closest (fastest movement) - Semi-transparent for sun ray effect */}
      <div
        className="absolute inset-0 pointer-events-none z-[4]"
        style={{
          ...getParallaxStyle(1.2, defaultLayer1.scale),
          opacity: defaultLayer1.opacity,
          top: '-15%'
        }}
      >
        <Image
          src="/assets/parallax-forest-1.png"
          alt="Forest Foreground Layer 1"
          fill
          className={`object-${defaultLayer1.objectFit}`}
          style={{
            imageRendering: 'pixelated',
            imageRendering: '-moz-crisp-edges',
            imageRendering: 'crisp-edges',
            filter: 'brightness(1.15) blur(0.5px)',
          }}
          unoptimized
        />
      </div>

      {/* Sun ray bloom effect */}
      <div
        className="absolute inset-0 pointer-events-none z-[4]"
        style={{
          ...getParallaxStyle(1.2, defaultLayer1.scale),
          opacity: 0.4,
          top: '-15%',
          mixBlendMode: 'screen',
        }}
      >
        <Image
          src="/assets/parallax-forest-1.png"
          alt="Sun Ray Bloom"
          fill
          className={`object-${defaultLayer1.objectFit}`}
          style={{
            imageRendering: 'pixelated',
            imageRendering: '-moz-crisp-edges',
            imageRendering: 'crisp-edges',
            filter: 'brightness(1.5) blur(8px)',
          }}
          unoptimized
        />
      </div>

      {/* Atmospheric Overlays */}
      <div className="absolute inset-0 z-[5] bg-gradient-to-t from-[#131313] via-transparent to-[#131313]/40 pointer-events-none" />
      <div className="absolute inset-0 z-[5] bg-gradient-to-r from-[#131313]/60 via-transparent to-[#131313]/60 pointer-events-none" />

      {/* Grain overlay */}
      <div
        className="absolute inset-0 z-[6] pointer-events-none opacity-15 mix-blend-overlay"
        style={{
          backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuBSxLYw7lox1gDTW-RWALnkjN6rU0sKutUQ2vVV3pf_AMp61D8EF4g6fnL7FLgYzbLYpFf-1KH1_Ea9CeSB64xaAROhMCMrOTFI6T5PC2dst0EudaxLy3KNzVitROorADNMKoxo9_-QpmCYvfSqX2HGFgsQ3voaW97U9Hd7DgdC1Z9lmuPYQgc5H8g873IntlKLGk1AwkObZ3b1P1npGy_DBBGa9D9Jzq7o4tHrf0hULoj7U3pypJ71uycY-doTEv_BNM2ldBwF6CPp)'
        }}
      />

      {/* Content overlay */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
