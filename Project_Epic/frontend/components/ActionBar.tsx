"use client";

import { useState } from 'react';

interface ActionBarProps {
  selectedPartyMember: string | null;
  onActionSelect: (action: string) => void;
  disabled?: boolean;
}

const ACTIONS = [
  { id: 'attack', label: 'Attack', icon: '⚔️', color: 'from-red-700 to-red-500' },
  { id: 'defend', label: 'Defend', icon: '🛡️', color: 'from-blue-700 to-blue-500' },
  { id: 'item', label: 'Item', icon: '📦', color: 'from-green-700 to-green-500' },
  { id: 'escape', label: 'Escape', icon: '🏃', color: 'from-gray-700 to-gray-500' },
];

export default function ActionBar({ selectedPartyMember, onActionSelect, disabled = false }: ActionBarProps) {
  const [hoveredAction, setHoveredAction] = useState<string | null>(null);

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-30">
      <div className="bg-[#1c1b1b]/95 backdrop-blur-sm border-2 border-[#434843] shadow-[0_0_40px_rgba(0,0,0,0.9)] p-4">
        {/* Selected Member Indicator */}
        {selectedPartyMember ? (
          <div className="text-center mb-3 text-[#e9c349] text-sm font-semibold tracking-wider">
            {selectedPartyMember.toUpperCase()}'S TURN
          </div>
        ) : (
          <div className="text-center mb-3 text-[#8e928c] text-sm tracking-wider">
            SELECT A PARTY MEMBER
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          {ACTIONS.map((action) => (
            <button
              key={action.id}
              onClick={() => !disabled && selectedPartyMember && onActionSelect(action.id)}
              onMouseEnter={() => setHoveredAction(action.id)}
              onMouseLeave={() => setHoveredAction(null)}
              disabled={disabled || !selectedPartyMember}
              className={`
                relative flex flex-col items-center justify-center
                w-28 h-24 border-2 transition-all duration-200
                ${disabled || !selectedPartyMember
                  ? 'border-[#353534] bg-[#2d3436]/50 opacity-50 cursor-not-allowed'
                  : hoveredAction === action.id
                  ? 'border-[#e9c349] bg-gradient-to-b ' + action.color + '/20 shadow-[0_0_20px_rgba(233,195,73,0.3)] -translate-y-1'
                  : 'border-[#434843] bg-[#2d3436]/80 hover:border-[#e9c349]/50'
                }
              `}
            >
              {/* Icon */}
              <div className={`
                text-4xl mb-1 transition-all duration-200
                ${hoveredAction === action.id ? 'scale-125' : 'scale-100'}
              `}>
                {action.icon}
              </div>

              {/* Label */}
              <div className={`
                text-xs font-semibold tracking-wider transition-colors
                ${disabled || !selectedPartyMember
                  ? 'text-[#8e928c]'
                  : hoveredAction === action.id
                  ? 'text-[#e9c349]'
                  : 'text-[#c4c8c1]'
                }
              `}>
                {action.label}
              </div>

              {/* Glow effect on hover */}
              {hoveredAction === action.id && !disabled && selectedPartyMember && (
                <div className="absolute inset-0 bg-gradient-to-b from-[#e9c349]/10 to-transparent pointer-events-none animate-pulse" />
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
