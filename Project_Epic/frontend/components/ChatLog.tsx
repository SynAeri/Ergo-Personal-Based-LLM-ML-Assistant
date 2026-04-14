"use client";

import { useEffect, useRef, useState } from 'react';

interface ChatMessage {
  id: string;
  timestamp: number;
  agent: string;
  action: string;
  message: string;
  type: 'action' | 'combat' | 'movement' | 'system';
}

interface ChatLogProps {
  messages: ChatMessage[];
  maxMessages?: number;
}

const AGENT_COLORS: Record<string, string> = {
  planner: '#8b7355',
  mage: '#9b59b6',
  rogue: '#e74c3c',
  tank: '#95a5a6',
  support: '#3498db',
  healer: '#2ecc71',
  system: '#e9c349',
};

const ACTION_ICONS: Record<string, string> = {
  action: '⚙️',
  combat: '⚔️',
  movement: '🚶',
  system: '📢',
};

export default function ChatLog({ messages, maxMessages = 50 }: ChatLogProps) {
  const logRef = useRef<HTMLDivElement>(null);
  const [isAutoScroll, setIsAutoScroll] = useState(true);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (isAutoScroll && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages, isAutoScroll]);

  // Check if user has scrolled up
  const handleScroll = () => {
    if (logRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
      setIsAutoScroll(isAtBottom);
    }
  };

  // Keep only recent messages
  const recentMessages = messages.slice(-maxMessages);

  return (
    <div className="fixed bottom-4 left-4 z-20 w-80">
      <div className="bg-[#1c1b1b]/80 backdrop-blur-sm">
        {/* Minimal header - just text, no borders */}
        <div className="px-3 py-1 flex items-center justify-between">
          <span className="text-[#e9c349] text-[10px] font-semibold tracking-widest opacity-60">BATTLE</span>
          {!isAutoScroll && (
            <button
              onClick={() => {
                setIsAutoScroll(true);
                if (logRef.current) {
                  logRef.current.scrollTop = logRef.current.scrollHeight;
                }
              }}
              className="text-[#e9c349] text-[10px] hover:text-[#e9c349]/80 transition-colors opacity-60"
            >
              ↓
            </button>
          )}
        </div>

        {/* Log Messages - very compact */}
        <div
          ref={logRef}
          onScroll={handleScroll}
          className="h-32 overflow-y-auto px-3 py-1 space-y-1 scrollbar-thin scrollbar-thumb-[#434843] scrollbar-track-transparent"
        >
          {recentMessages.length === 0 ? (
            <div className="text-[#8e928c] text-[10px] opacity-50">
              ...
            </div>
          ) : (
            recentMessages.map((msg) => (
              <div
                key={msg.id}
                className="text-[10px] leading-relaxed"
              >
                {/* Icon + Agent Name + Message in one line */}
                <span className="mr-1 opacity-60">{ACTION_ICONS[msg.type] || '•'}</span>
                <span
                  className="font-semibold mr-1"
                  style={{ color: AGENT_COLORS[msg.agent] || '#c4c8c1' }}
                >
                  {msg.agent.toUpperCase()}
                </span>
                <span className="text-[#c4c8c1] opacity-80">{msg.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
