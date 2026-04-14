"use client";

import { useState, useEffect } from 'react';
import AnimatedSprite from './AnimatedSprite';

interface PartyMember {
  id: string;
  name: string;
  icon: string;
  hp: number;
  maxHp: number;
  mp: number;
  maxMp: number;
  animation: 'idle' | 'run' | 'attack';
}

interface PartyDisplayProps {
  partyMembers: PartyMember[];
  onCommandSelect?: (memberId: string, command: string) => void;
}

const ROLE_NAMES: Record<string, string> = {
  'planner': 'Planner',
  'mage': 'Mage',
  'rogue': 'Rogue',
  'tank': 'Tank',
  'support': 'Support',
  'healer': 'Healer',
};

export default function PartyDisplay({ partyMembers, onCommandSelect }: PartyDisplayProps) {
  const [selectedMember, setSelectedMember] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

  // Track mouse position for parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      const x = clientX / innerWidth;
      const y = clientY / innerHeight;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const getFrameCount = (roleId: string, animation: string) => {
    if (animation === 'run') {
      // Mage-based: 5 frames sprint, Knight-based: 8 frames run
      return (roleId === 'mage' || roleId === 'support' || roleId === 'healer') ? 5 : 8;
    }
    if (animation === 'attack') {
      // Mage-based: 19 frames, Knight-based: 12 frames
      return (roleId === 'mage' || roleId === 'support' || roleId === 'healer') ? 19 : 12;
    }
    // Idle: Mage-based 9 frames, Knight-based 6 frames
    return (roleId === 'mage' || roleId === 'support' || roleId === 'healer') ? 9 : 6;
  };

  // Calculate parallax for each member (more movement for variety)
  const getMemberParallax = (index: number) => {
    const depths = [0.3, 0.5, 0.4, 0.6];
    const maxOffset = 15;
    const depth = depths[index] || 0.4;

    const xOffset = (mousePos.x - 0.5) * maxOffset * depth;
    const yOffset = (mousePos.y - 0.5) * maxOffset * depth;

    return {
      transform: `translate(${xOffset}px, ${yOffset}px)`,
      transition: 'transform 0.1s ease-out',
    };
  };

  const commands = ['Attack', 'Defend', 'Items', 'Escape'];

  return (
    <div className="fixed top-4 left-4 z-20 flex gap-6">
      {partyMembers.map((member, index) => (
        <div
          key={member.id}
          className="relative"
          style={getMemberParallax(index)}
        >
          {/* Selection border */}
          {selectedMember === member.id && (
            <div className="absolute inset-0 border-2 border-[#e9c349] animate-pulse pointer-events-none z-10" />
          )}

          {/* Character Container */}
          <div
            className="relative bg-[#1c1b1b]/80 backdrop-blur-sm border border-[#434843] p-3 cursor-pointer
              hover:border-[#e9c349]/50 transition-all"
            onClick={() => setSelectedMember(member.id)}
          >
            {/* Sprite */}
            <div className="w-24 h-24 flex items-center justify-center mb-2">
              <AnimatedSprite
                roleId={member.id}
                frameCount={getFrameCount(member.id, member.animation)}
                width={96}
                height={96}
                animation={member.animation}
              />
            </div>

            {/* Name */}
            <div className="text-[#e9c349] text-xs font-semibold text-center mb-2 tracking-wider drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)]">
              {ROLE_NAMES[member.id] || member.name}
            </div>

            {/* HP Bar */}
            <div className="mb-1">
              <div className="flex justify-between text-[10px] text-[#c4c8c1] mb-1">
                <span>HP</span>
                <span>{member.hp}/{member.maxHp}</span>
              </div>
              <div className="h-2 bg-[#353534] border border-[#434843]">
                <div
                  className="h-full bg-gradient-to-r from-red-700 to-red-500 transition-all duration-500"
                  style={{ width: `${(member.hp / member.maxHp) * 100}%` }}
                />
              </div>
            </div>

            {/* MP Bar */}
            <div>
              <div className="flex justify-between text-[10px] text-[#c4c8c1] mb-1">
                <span>MP</span>
                <span>{member.mp}/{member.maxMp}</span>
              </div>
              <div className="h-2 bg-[#353534] border border-[#434843]">
                <div
                  className="h-full bg-gradient-to-r from-blue-700 to-blue-500 transition-all duration-500"
                  style={{ width: `${(member.mp / member.maxMp) * 100}%` }}
                />
              </div>
            </div>

            {/* Circular shadow */}
            <div className="absolute bottom-1 left-1/2 -translate-x-1/2 w-16 h-3 rounded-full bg-black/40 blur-sm pointer-events-none" />
          </div>

          {/* RPG Command Menu */}
          {selectedMember === member.id && (
            <div className="absolute top-0 left-full ml-2 bg-[#1c1b1b] border-2 border-[#e9c349] shadow-[0_0_20px_rgba(233,195,73,0.4)] z-50">
              {commands.map((command) => (
                <button
                  key={command}
                  onClick={(e) => {
                    e.stopPropagation();
                    onCommandSelect?.(member.id, command.toLowerCase());
                    setSelectedMember(null);
                  }}
                  className="w-32 px-4 py-2 text-left text-[#e5e2e1] border-b border-[#434843] last:border-b-0
                    hover:bg-[#e9c349] hover:text-[#131313] transition-colors text-sm font-semibold tracking-wide"
                >
                  {command}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
