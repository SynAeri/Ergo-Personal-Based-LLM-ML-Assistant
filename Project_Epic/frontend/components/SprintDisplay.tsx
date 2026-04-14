"use client";

interface Sprint {
  rank: string;
  name: string;
  description: string;
  enemy_type: string;
  estimated_cost: number;
  success_criteria: string[];
}

interface SprintDisplayProps {
  sprints: Sprint[];
  currentSprintIndex?: number;
}

export default function SprintDisplay({ sprints, currentSprintIndex = 0 }: SprintDisplayProps) {
  return (
    <div className="fixed top-4 left-4 z-20 w-80">
      <div className="bg-[#1c1b1b]/80 backdrop-blur-sm">
        <div className="px-3 py-1">
          <span className="text-[#e9c349] text-[10px] font-semibold tracking-widest opacity-60">SPRINTS</span>
        </div>
        <div className="space-y-1 px-3 py-2 max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-[#434843] scrollbar-track-transparent">
          {sprints.map((sprint, idx) => {
            const isActive = idx === currentSprintIndex;
            const isCompleted = idx < currentSprintIndex;

            return (
              <div
                key={idx}
                className={`
                  text-[10px] transition-all
                  ${isActive ? 'text-[#e9c349] opacity-100' : isCompleted ? 'text-green-400 opacity-70' : 'text-[#8e928c] opacity-50'}
                `}
              >
                <div className="flex items-center gap-1">
                  {isCompleted && <span>✓</span>}
                  {isActive && <span className="animate-pulse">▶</span>}
                  <span className="font-bold">[{sprint.rank}]</span>
                  <span>{sprint.name}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
