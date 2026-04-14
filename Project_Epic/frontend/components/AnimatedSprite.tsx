"use client";

import { useState, useEffect } from 'react';
import Image from 'next/image';

interface AnimatedSpriteProps {
  roleId: string;
  frameCount: number;
  frameDelay?: number; // milliseconds between frames
  width?: number;
  height?: number;
  animation?: 'idle' | 'run' | 'attack'; // Animation type
}

export default function AnimatedSprite({
  roleId,
  frameCount,
  frameDelay = 150,
  width = 128,
  height = 128,
  animation = 'idle'
}: AnimatedSpriteProps) {
  const [currentFrame, setCurrentFrame] = useState(1);

  useEffect(() => {
    setCurrentFrame(1); // Reset frame when animation changes
    const interval = setInterval(() => {
      setCurrentFrame((prev) => (prev % frameCount) + 1);
    }, frameDelay);

    return () => clearInterval(interval);
  }, [frameCount, frameDelay, animation]);

  // Map role IDs to sprite paths based on animation type
  const getSpritePath = () => {
    const isMageBased = roleId === 'mage' || roleId === 'support' || roleId === 'healer';
    const baseClass = isMageBased ? 'mage' : 'knight';

    // Animation path mapping
    const animationPaths: Record<string, string> = {
      'idle': `/assets/${baseClass}/Sprites/Idle/Idle${currentFrame}.png`,
      'run': isMageBased
        ? `/assets/mage/Sprites/Sprint/Sprinting/NoFX/Sprinting(NoFX)${currentFrame}.png`
        : `/assets/knight/Sprites/Run/Running/Running${currentFrame}.png`,
      'attack': isMageBased
        ? `/assets/mage/Sprites/Attacks/ComboAtk/Full/ComboAtk${currentFrame}.png`
        : `/assets/knight/Sprites/Attacks/LightAtk/LightAtk${currentFrame}.png`,
    };

    return animationPaths[animation];
  };

  return (
    <div className="relative flex items-center justify-center overflow-hidden" style={{ width, height }}>
      <Image
        src={getSpritePath()}
        alt={`${roleId} ${animation}`}
        width={width}
        height={height}
        className="pixelated object-contain"
        style={{
          imageRendering: 'pixelated',
          minWidth: width,
          minHeight: height,
        }}
        unoptimized
        priority
        onError={(e) => {
          console.error(`Failed to load sprite: ${getSpritePath()}`);
          // Fallback to frame 1 if current frame fails
          if (currentFrame > 1) {
            setCurrentFrame(1);
          }
        }}
      />
    </div>
  );
}
