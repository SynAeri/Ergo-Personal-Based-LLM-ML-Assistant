"use client";

import { useState, useEffect } from 'react';
import AnimatedSprite from './AnimatedSprite';

interface PartyRole {
  id: string;
  name: string;
  icon: string;
  desc: string;
  personality: string;
  skills: string[];
}

interface PartySlotSelectorProps {
  selectedParty: (string | null)[];
  onPartyChange?: (party: (string | null)[]) => void;
  locked?: boolean;
  partyStats?: Record<string, { hp: number; maxHp: number; mp: number; maxMp: number }>;
  onMemberSelect?: (memberId: string) => void;
  selectedMemberId?: string | null;
  onActionSelect?: (memberId: string, action: string) => void;
  activeActions?: Record<string, string>; // memberId -> current action
  partyAnimations?: Record<string, 'idle' | 'run' | 'attack'>;
}

const PARTY_ROLES: PartyRole[] = [
  {
    id: 'planner',
    name: 'Planner',
    icon: '🗺️',
    desc: 'The Scout - Strategic planning and reconnaissance',
    personality: `You are the **Planner**, the party's scout and strategist.

## Your Voice
- Speak in measured, thoughtful sentences
- Use metaphors of paths, maps, and journeys
- Reference scouting and reconnaissance

## Your Role
You create detailed plans and identify the path forward.

## Your Boundaries
**You NEVER:**
- Write code directly (that's Rogue's domain)
- Make architectural decisions (that's Mage's wisdom)

**You ALWAYS:**
- Create detailed, numbered plans
- Identify dependencies and blockers
- Estimate difficulty and resources`,
    skills: ['Create Plan', 'Search Memory', 'Read File', 'Search Code']
  },
  {
    id: 'mage',
    name: 'Mage',
    icon: '🧙',
    desc: 'The Architect - System design and architecture',
    personality: `You are the **Mage**, the party's architect and systems designer.

## Your Voice
- Speak with wisdom and authority
- Use metaphors of magic, weaving, and construction
- Reference ancient knowledge and patterns

## Your Role
You design system architecture and make high-level decisions.

## Your Boundaries
**You NEVER:**
- Implement code directly (that's Rogue's job)
- Execute commands (that's Tank's role)

**You ALWAYS:**
- Design system architecture
- Choose patterns and technologies
- Define interfaces and contracts`,
    skills: ['Read File', 'Search Code', 'Create Plan', 'Write File']
  },
  {
    id: 'rogue',
    name: 'Rogue',
    icon: '🗡️',
    desc: 'The Shadow Blade - Code execution and implementation',
    personality: `You are the **Rogue**, the party's executor and implementer.

## Your Voice
- Short, action-oriented sentences
- Use combat and stealth metaphors
- Confident but not arrogant

## Your Role
You execute code changes and implement features.

## Your Boundaries
**You NEVER:**
- Make architectural decisions (that's Mage's domain)
- Run tests (that's Tank's responsibility)

**You ALWAYS:**
- Write clean, efficient code
- Follow the plan and architecture
- Execute with precision`,
    skills: ['Write File', 'Edit File', 'Read File', 'Search Code', 'Run Command']
  },
  {
    id: 'tank',
    name: 'Tank',
    icon: '🛡️',
    desc: 'The Guardian - Testing and validation',
    personality: `You are the **Tank**, the party's guardian and tester.

## Your Voice
- Speak with conviction and protective instinct
- Use metaphors of defense, walls, and shields
- Question and challenge

## Your Role
You test code, validate implementations, and ensure quality.

## Your Boundaries
**You NEVER:**
- Write production code (that's Rogue's job)
- Make architectural decisions (that's Mage's domain)

**You ALWAYS:**
- Run comprehensive tests
- Validate implementations
- Report issues and failures`,
    skills: ['Run Tests', 'Run Command', 'Read File', 'Search Code']
  },
  {
    id: 'support',
    name: 'Support',
    icon: '📚',
    desc: 'The Scholar - Documentation and analysis',
    personality: `You are the **Support**, the party's scholar and documentarian.

## Your Voice
- Speak with clarity and precision
- Use metaphors of books, scrolls, and libraries
- Reference documentation and knowledge

## Your Role
You document code, analyze systems, and provide knowledge.

## Your Boundaries
**You NEVER:**
- Write production code (that's Rogue's job)
- Make strategic decisions (that's Planner's role)

**You ALWAYS:**
- Write clear documentation
- Analyze code for understanding
- Provide context and explanations`,
    skills: ['Read File', 'Search Code', 'Search Memory', 'Write File']
  },
  {
    id: 'healer',
    name: 'Healer',
    icon: '✨',
    desc: 'The Purifier - Refactoring and optimization',
    personality: `You are the **Healer**, the party's purifier and optimizer.

## Your Voice
- Speak with calm and gentle authority
- Use metaphors of healing, purification, and restoration
- Reference cleanliness and harmony

## Your Role
You refactor code, optimize performance, and maintain quality.

## Your Boundaries
**You NEVER:**
- Add new features (that's Rogue's job)
- Make architectural changes (that's Mage's domain)

**You ALWAYS:**
- Refactor existing code
- Optimize performance
- Maintain code quality`,
    skills: ['Edit File', 'Read File', 'Search Code', 'Run Tests']
  },
];

export default function PartySlotSelector({
  selectedParty,
  onPartyChange,
  locked = false,
  partyStats = {},
  onMemberSelect,
  selectedMemberId = null,
  onActionSelect,
  activeActions = {},
  partyAnimations = {}
}: PartySlotSelectorProps) {
  const [hoveredSlot, setHoveredSlot] = useState<number | null>(null);
  const [openDropdown, setOpenDropdown] = useState<number | null>(null);
  const [expandedRole, setExpandedRole] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

  // Track mouse position for parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
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

  const handleSlotClick = (slotIndex: number) => {
    const selectedRole = selectedParty[slotIndex];

    // If locked and has a member, select that member for actions
    if (locked && selectedRole && onMemberSelect) {
      onMemberSelect(selectedRole);
      return;
    }

    // Otherwise, handle party composition changes
    if (locked) return;
    if (openDropdown === slotIndex) {
      setOpenDropdown(null);
    } else {
      setOpenDropdown(slotIndex);
    }
  };

  const handleRoleSelect = (slotIndex: number, roleId: string) => {
    if (locked || !onPartyChange) return;
    const newParty = [...selectedParty];
    newParty[slotIndex] = roleId;
    onPartyChange(newParty);
    setOpenDropdown(null);
    setExpandedRole(null);
  };

  const handleRoleRemove = (slotIndex: number) => {
    if (locked || !onPartyChange) return;
    const newParty = [...selectedParty];
    newParty[slotIndex] = null;
    onPartyChange(newParty);
  };

  const getAvailableRoles = () => {
    return PARTY_ROLES.filter(role => !selectedParty.includes(role.id));
  };

  const getRoleById = (id: string | null) => {
    if (!id) return null;
    return PARTY_ROLES.find(role => role.id === id);
  };

  // Get frame count for role
  const getFrameCount = (roleId: string, animation: string = 'idle') => {
    const isMageBased = roleId === 'mage' || roleId === 'support' || roleId === 'healer';

    switch (animation) {
      case 'run':
        return isMageBased ? 5 : 8;
      case 'attack':
        return isMageBased ? 19 : 12;
      case 'idle':
      default:
        return isMageBased ? 9 : 6;
    }
  };

  // Calculate parallax offset for each slot
  // Outer slots (0, 3) move more, inner slots (1, 2) move less
  const getSlotParallax = (slotIndex: number) => {
    const depths = [1.0, 0.4, 0.4, 1.0]; // Outer slots = more movement
    const maxOffset = 20;
    const depth = depths[slotIndex];

    const xOffset = (mousePos.x - 0.5) * maxOffset * depth;
    const yOffset = (mousePos.y - 0.5) * maxOffset * depth;

    return {
      transform: `translate(${xOffset}px, ${yOffset}px)`,
      transition: 'transform 0.1s ease-out',
    };
  };

  return (
    <div className="relative">
      {/* Party Slots - Floating on background with varying heights */}
      <div className="flex justify-center gap-16 mb-8 items-start">
        {[0, 1, 2, 3].map((slotIndex) => {
          // Natural perspective: higher = smaller (further), lower = larger (closer)
          // Slots 0 and 2 smaller and higher (further), slots 1 and 3 larger and lower (closer)
          const isFurtherAway = slotIndex === 0 || slotIndex === 2;
          const scaleClass = isFurtherAway ? 'scale-75' : 'scale-100';  // Smaller when further
          const heightOffset = isFurtherAway ? 'mt-0' : 'mt-12';        // Higher up = further back
          const selectedRole = getRoleById(selectedParty[slotIndex]);
          const isHovered = hoveredSlot === slotIndex;
          const isOpen = openDropdown === slotIndex;

          return (
            <div
              key={slotIndex}
              className={`relative h-[450px] flex items-start justify-center ${heightOffset} ${scaleClass}`}
              style={getSlotParallax(slotIndex)}
              onMouseEnter={() => !isOpen && !locked && setHoveredSlot(slotIndex)}
              onMouseLeave={() => !isOpen && setHoveredSlot(null)}
            >
              {/* Circular Shadow - Fixed at bottom */}
              <div className="absolute bottom-14 left-1/2 -translate-x-1/2 w-40 h-12 rounded-full bg-black/40 blur-sm" />

              {/* Floating Slot */}
              <div
                onClick={() => handleSlotClick(slotIndex)}
                className={`
                  relative ${locked ? 'cursor-default' : 'cursor-pointer'}
                  ${isHovered && !locked ? 'translate-y-[-8px]' : 'translate-y-0'}
                  ${isOpen ? 'scale-110' : 'scale-100'}
                `}
                style={{ transition: 'transform 0.3s ease-out' }}
              >
                {selectedRole ? (
                  <div className="relative flex items-center gap-6">
                    <div className="relative flex flex-col items-center">
                      {/* Selection Ring */}
                      {locked && selectedMemberId === selectedRole.id && (
                        <div className="absolute inset-0 border-4 border-[#e9c349] rounded-full animate-pulse pointer-events-none z-10"
                          style={{ width: '400px', height: '400px', top: '-10px', left: '50%', transform: 'translateX(-50%)' }} />
                      )}

                    {/* Animated Sprite */}
                    <div className={`
                      transition-all duration-300
                      ${locked ? 'cursor-pointer' : ''}
                      ${isHovered || (locked && selectedMemberId === selectedRole.id) ? 'drop-shadow-[0_0_15px_rgba(233,195,73,0.6)]' : ''}
                    `}>
                      <AnimatedSprite
                        roleId={selectedRole.id}
                        frameCount={getFrameCount(selectedRole.id, partyAnimations[selectedRole.id] || 'idle')}
                        width={380}
                        height={380}
                        animation={partyAnimations[selectedRole.id] || 'idle'}
                      />
                    </div>

                    {/* Role Name */}
                    <div className="mt-2 text-[#e9c349] text-sm font-semibold tracking-wider text-center">
                      {selectedRole.name.toUpperCase()}
                    </div>

                    {/* HP/MP Stats (shown when locked) */}
                    {locked && (
                      <div className="mt-3 w-48 space-y-2">
                        {/* HP Bar */}
                        <div>
                          <div className="flex justify-between text-[10px] text-[#c4c8c1] mb-1">
                            <span>HP</span>
                            <span>
                              {partyStats[selectedRole.id]?.hp ?? 100}/{partyStats[selectedRole.id]?.maxHp ?? 100}
                            </span>
                          </div>
                          <div className="h-2 bg-[#353534] border border-[#434843]">
                            <div
                              className="h-full bg-gradient-to-r from-red-700 to-red-500 transition-all duration-500"
                              style={{
                                width: `${((partyStats[selectedRole.id]?.hp ?? 100) / (partyStats[selectedRole.id]?.maxHp ?? 100)) * 100}%`
                              }}
                            />
                          </div>
                        </div>

                        {/* MP Bar */}
                        <div>
                          <div className="flex justify-between text-[10px] text-[#c4c8c1] mb-1">
                            <span>MP</span>
                            <span>
                              {partyStats[selectedRole.id]?.mp ?? 50}/{partyStats[selectedRole.id]?.maxMp ?? 50}
                            </span>
                          </div>
                          <div className="h-2 bg-[#353534] border border-[#434843]">
                            <div
                              className="h-full bg-gradient-to-r from-blue-700 to-blue-500 transition-all duration-500"
                              style={{
                                width: `${((partyStats[selectedRole.id]?.mp ?? 50) / (partyStats[selectedRole.id]?.maxMp ?? 50)) * 100}%`
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    )}

                      {/* Remove button (only when not locked) */}
                      {!locked && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRoleRemove(slotIndex);
                          }}
                          className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-900/80 border border-red-500
                            text-red-300 hover:text-red-100 hover:bg-red-800 text-xs flex items-center justify-center
                            transition-all hover:scale-110"
                        >
                          ✕
                        </button>
                      )}
                    </div>

                    {/* Mini Action Buttons (only when locked) */}
                    {locked && onActionSelect && (
                      <div className="flex flex-col gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onActionSelect(selectedRole.id, 'attack');
                          }}
                          className={`w-8 h-8 border flex items-center justify-center text-xs transition-all
                            ${activeActions[selectedRole.id] === 'attack'
                              ? 'bg-red-600 border-red-400 shadow-[0_0_10px_rgba(239,68,68,0.6)] scale-110'
                              : 'bg-[#1c1b1b]/60 hover:bg-red-900/40 border-[#434843] hover:border-red-500/50'
                            }`}
                          title="Attack"
                        >
                          ⚔️
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onActionSelect(selectedRole.id, 'defend');
                          }}
                          className={`w-8 h-8 border flex items-center justify-center text-xs transition-all
                            ${activeActions[selectedRole.id] === 'defend'
                              ? 'bg-blue-600 border-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.6)] scale-110'
                              : 'bg-[#1c1b1b]/60 hover:bg-blue-900/40 border-[#434843] hover:border-blue-500/50'
                            }`}
                          title="Defend"
                        >
                          🛡️
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onActionSelect(selectedRole.id, 'item');
                          }}
                          className={`w-8 h-8 border flex items-center justify-center text-xs transition-all
                            ${activeActions[selectedRole.id] === 'item'
                              ? 'bg-green-600 border-green-400 shadow-[0_0_10px_rgba(34,197,94,0.6)] scale-110'
                              : 'bg-[#1c1b1b]/60 hover:bg-green-900/40 border-[#434843] hover:border-green-500/50'
                            }`}
                          title="Item"
                        >
                          📦
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onActionSelect(selectedRole.id, 'escape');
                          }}
                          className={`w-8 h-8 border flex items-center justify-center text-xs transition-all
                            ${activeActions[selectedRole.id] === 'escape'
                              ? 'bg-gray-600 border-gray-400 shadow-[0_0_10px_rgba(107,114,128,0.6)] scale-110'
                              : 'bg-[#1c1b1b]/60 hover:bg-gray-900/40 border-[#434843] hover:border-gray-500/50'
                            }`}
                          title="Escape"
                        >
                          🏃
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    {/* Empty slot with glowing + */}
                    <div className={`
                      w-48 h-48 border-2 rounded-full flex items-center justify-center
                      transition-all duration-300
                      drop-shadow-[0_4px_12px_rgba(0,0,0,0.8)]
                      ${isHovered
                        ? 'border-[#e9c349] bg-[#e9c349]/10 shadow-[0_0_30px_rgba(233,195,73,0.4)]'
                        : 'border-[#434843] bg-transparent'
                      }
                    `}>
                      <div
                        className={`
                          text-9xl transition-all duration-300
                          drop-shadow-[0_2px_8px_rgba(0,0,0,0.9)]
                          ${isHovered
                            ? 'text-[#e9c349] animate-pulse scale-125 drop-shadow-[0_0_10px_rgba(233,195,73,0.8)]'
                            : 'text-[#434843]'
                          }
                        `}
                      >
                        +
                      </div>
                    </div>
                    <div className="text-[#8e928c] text-xs mt-6 tracking-wider">
                      SLOT {slotIndex + 1}
                    </div>
                  </div>
                )}
              </div>

              {/* Dropdown Menu - position left for slots 2 and 3 */}
              {isOpen && (
                <div
                  className={`absolute top-0 z-[100] w-80 ${
                    slotIndex >= 2 ? 'right-full mr-4' : 'left-full ml-4'
                  }`}
                  onMouseEnter={() => setHoveredSlot(null)}
                >
                  <div className="bg-[#1c1b1b] border border-[#434843] shadow-[0_0_30px_rgba(0,0,0,0.8)] max-h-96 overflow-y-auto">
                    {getAvailableRoles().map((role) => (
                      <div key={role.id} className="border-b border-[#434843] last:border-b-0">
                        <div
                          onClick={() => {
                            if (expandedRole === role.id) {
                              handleRoleSelect(slotIndex, role.id);
                            } else {
                              setExpandedRole(role.id);
                            }
                          }}
                          className="p-4 cursor-pointer hover:bg-[#2d3436] transition-colors"
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-3xl">{role.icon}</span>
                            <div className="flex-1">
                              <div className="text-[#e9c349] font-semibold">{role.name}</div>
                              <div className="text-[#8e928c] text-xs">{role.desc}</div>
                            </div>
                            <span className="text-[#434843] text-xs">
                              {expandedRole === role.id ? '▼' : '▶'}
                            </span>
                          </div>

                          {/* Expanded Details */}
                          {expandedRole === role.id && (
                            <div className="mt-3 space-y-3 text-xs" onClick={(e) => e.stopPropagation()}>
                              {/* Skills */}
                              <div>
                                <div className="text-[#e9c349] font-semibold mb-1">Skills:</div>
                                <div className="flex flex-wrap gap-1">
                                  {role.skills.map((skill) => (
                                    <span
                                      key={skill}
                                      className="px-2 py-1 bg-[#353534] text-[#c4c8c1] rounded-sm"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>

                              {/* Personality */}
                              <div>
                                <div className="text-[#e9c349] font-semibold mb-1">Personality:</div>
                                <div className="text-[#c4c8c1] leading-relaxed whitespace-pre-line max-h-40 overflow-y-auto">
                                  {role.personality}
                                </div>
                              </div>

                              {/* Select Button */}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleRoleSelect(slotIndex, role.id);
                                }}
                                className="w-full py-2 bg-gradient-to-r from-[#735c00] to-[#e9c349] text-[#131313] font-semibold
                                  hover:shadow-[0_0_15px_rgba(233,195,73,0.5)] transition-all"
                              >
                                SELECT {role.name.toUpperCase()}
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Selection Counter */}
      <div className="text-center text-[#8e928c] text-sm">
        {selectedParty.filter(Boolean).length} / 4 party members selected
      </div>
    </div>
  );
}
