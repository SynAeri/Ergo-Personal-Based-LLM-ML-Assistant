"use client";

import { useState } from 'react';

interface Sprint {
  rank: string;
  name: string;
  description: string;
  enemy_type: string;
  estimated_cost: number;
  success_criteria: string[];
}

interface SprintTasksPanelProps {
  currentSprint: Sprint | null;
  progress?: number;
}

export default function SprintTasksPanel({ currentSprint, progress = 0 }: SprintTasksPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!currentSprint) return null;

  return (
    <div className="fixed top-4 right-4 z-20 w-80">
      {/* Minimal View - Always shown */}
      <div className="bg-[#1c1b1b]/80 backdrop-blur-sm">
        <div className="px-3 py-1">
          <span className="text-[#e9c349] text-[10px] font-semibold tracking-widest opacity-60">OBJECTIVES</span>
        </div>
        <div className="px-3 py-2 space-y-1 max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-[#434843] scrollbar-track-transparent">
          <div className="text-[10px] text-[#c4c8c1] opacity-80">
            <span className="text-[#e9c349] font-bold mr-1">[{currentSprint.rank}]</span>
            {currentSprint.name}
          </div>
          {currentSprint.success_criteria.slice(0, 3).map((criterion, idx) => (
            <div key={idx} className="text-[10px] text-[#c4c8c1] opacity-70 flex items-start gap-1">
              <span>□</span>
              <span className="flex-1">{criterion}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
