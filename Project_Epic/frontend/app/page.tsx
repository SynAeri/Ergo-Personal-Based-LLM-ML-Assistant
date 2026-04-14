"use client";

import { useState, useEffect } from 'react';
import ParallaxForest from '@/components/ParallaxForest';
import PartySlotSelector from '@/components/PartySlotSelector';
import SprintDisplay from '@/components/SprintDisplay';
import SprintTasksPanel from '@/components/SprintTasksPanel';
import ChatLog from '@/components/ChatLog';

interface Sprint {
  rank: string;
  name: string;
  description: string;
  enemy_type: string;
  estimated_cost: number;
  success_criteria: string[];
}

interface Quest {
  quest_id: string;
  goal: string;
  demon_king: string;
  status: string;
  sprints: Sprint[];
  progress: number;
  budget: { used: number; total: number };
  tokens: { used: number; total: number };
}

export default function Home() {
  const [selectedParty, setSelectedParty] = useState<(string | null)[]>([null, null, null, null]);
  const [goal, setGoal] = useState('');
  const [quest, setQuest] = useState<Quest | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [partyAnimations, setPartyAnimations] = useState<Record<string, 'idle' | 'run' | 'attack'>>({});
  const [currentSprintIndex, setCurrentSprintIndex] = useState(0);
  const [selectedPartyMember, setSelectedPartyMember] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [partyStats, setPartyStats] = useState<Record<string, { hp: number; maxHp: number; mp: number; maxMp: number }>>({});
  const [battlePhase, setBattlePhase] = useState<'idle' | 'running' | 'fighting'>('idle');
  const [autoProgress, setAutoProgress] = useState(0);
  const [activeActions, setActiveActions] = useState<Record<string, string>>({});
  const [phaseSummary, setPhaseSummary] = useState<{attacks: number; defends: number; items: number}>({attacks: 0, defends: 0, items: 0});

  const API_BASE = 'http://localhost:8766';

  // Get non-null party members for API call
  const getActivePartyMembers = () => {
    return selectedParty.filter((id): id is string => id !== null);
  };

  // Add chat message
  const addChatMessage = (agent: string, action: string, message: string, type: 'action' | 'combat' | 'movement' | 'system' = 'action') => {
    const newMessage = {
      id: `${Date.now()}-${Math.random()}`,
      timestamp: Date.now(),
      agent,
      action,
      message,
      type,
    };
    setChatMessages(prev => [...prev, newMessage]);
  };

  // Handle action selection (now takes memberId and action)
  const handleActionSelect = (memberId: string, action: string) => {
    // Simulate action with chat messages
    switch (action) {
      case 'attack':
        addChatMessage(memberId, 'attack', `used ${getRandomCommand()}`, 'combat');
        setPartyAnimations(prev => ({ ...prev, [memberId]: 'attack' }));
        setTimeout(() => {
          setPartyAnimations(prev => ({ ...prev, [memberId]: 'idle' }));
        }, 1500);
        break;
      case 'defend':
        addChatMessage(memberId, 'defend', 'takes a defensive stance', 'action');
        break;
      case 'item':
        addChatMessage(memberId, 'item', 'searches for tools', 'action');
        break;
      case 'escape':
        addChatMessage(memberId, 'escape', 'attempts to retreat', 'movement');
        setPartyAnimations(prev => ({ ...prev, [memberId]: 'run' }));
        setTimeout(() => {
          setPartyAnimations(prev => ({ ...prev, [memberId]: 'idle' }));
        }, 2000);
        break;
    }
  };

  // Get random command for simulating agent actions
  const getRandomCommand = () => {
    const commands = [
      'ls -la',
      'grep -r "function"',
      'npm install',
      'git status',
      'python test.py',
      'cargo build',
      'vim config.json',
      'cd src/',
      'cat README.md',
      'pytest tests/',
      'write src/auth.rs',
      'edit config.json',
      'run tests',
      'check logs',
    ];
    return commands[Math.floor(Math.random() * commands.length)];
  };

  // Get random action for automated battle
  const getRandomAction = () => {
    const actions = ['attack', 'defend', 'item'];
    const weights = [0.5, 0.3, 0.2]; // 50% attack, 30% defend, 20% item
    const random = Math.random();
    let sum = 0;

    for (let i = 0; i < weights.length; i++) {
      sum += weights[i];
      if (random <= sum) return actions[i];
    }
    return 'attack';
  };

  // Automated battle system
  useEffect(() => {
    if (!quest || battlePhase === 'idle') return;

    let battleInterval: NodeJS.Timeout;
    let progressInterval: NodeJS.Timeout;

    if (battlePhase === 'running') {
      // Running phase - all characters run
      const activeMembers = getActivePartyMembers();
      const runAnims: Record<string, 'idle' | 'run' | 'attack'> = {};
      activeMembers.forEach(member => {
        runAnims[member] = 'run';
      });
      setPartyAnimations(runAnims);

      // Add running messages
      activeMembers.forEach((member, idx) => {
        setTimeout(() => {
          addChatMessage(member, 'movement', 'advancing to battle position', 'movement');
        }, idx * 500);
      });

      // After 3 seconds, switch to fighting
      setTimeout(() => {
        setBattlePhase('fighting');
        addChatMessage('system', 'combat', 'Engaging enemy!', 'combat');
      }, 3000);
    } else if (battlePhase === 'fighting') {
      // Fighting phase - automated combat
      const activeMembers = getActivePartyMembers();
      let turnIndex = 0;

      battleInterval = setInterval(() => {
        const member = activeMembers[turnIndex % activeMembers.length];
        const action = getRandomAction();

        // Highlight active action
        setActiveActions(prev => ({ ...prev, [member]: action }));

        // Execute action
        switch (action) {
          case 'attack':
            addChatMessage(member, 'attack', `used ${getRandomCommand()}`, 'combat');
            setPartyAnimations(prev => ({ ...prev, [member]: 'attack' }));
            setPhaseSummary(prev => ({ ...prev, attacks: prev.attacks + 1 }));
            setTimeout(() => {
              setPartyAnimations(prev => ({ ...prev, [member]: 'idle' }));
              setActiveActions(prev => ({ ...prev, [member]: '' }));
            }, 1200);
            // Reduce MP
            setPartyStats(prev => ({
              ...prev,
              [member]: {
                ...prev[member],
                mp: Math.max(0, prev[member].mp - 2)
              }
            }));
            break;

          case 'defend':
            addChatMessage(member, 'defend', 'takes defensive stance', 'action');
            setPhaseSummary(prev => ({ ...prev, defends: prev.defends + 1 }));
            setTimeout(() => {
              setPartyAnimations(prev => ({ ...prev, [member]: 'idle' }));
              setActiveActions(prev => ({ ...prev, [member]: '' }));
            }, 800);
            break;

          case 'item':
            addChatMessage(member, 'item', 'searches for tools', 'action');
            setPhaseSummary(prev => ({ ...prev, items: prev.items + 1 }));
            setTimeout(() => {
              setActiveActions(prev => ({ ...prev, [member]: '' }));
            }, 800);
            // Restore some MP
            setPartyStats(prev => ({
              ...prev,
              [member]: {
                ...prev[member],
                mp: Math.min(prev[member].maxMp, prev[member].mp + 3)
              }
            }));
            break;
        }

        turnIndex++;
      }, 2000); // Action every 2 seconds

      // Progress increment
      progressInterval = setInterval(() => {
        setAutoProgress(prev => {
          const newProgress = Math.min(100, prev + 1);
          if (newProgress >= 100) {
            // Sprint complete - add summary
            addChatMessage('system', 'system', 'Sprint complete! Enemy defeated!', 'system');
            addChatMessage(
              'system',
              'summary',
              `Phase Summary: ${phaseSummary.attacks} attacks, ${phaseSummary.defends} defends, ${phaseSummary.items} items used`,
              'system'
            );
            setBattlePhase('idle');
            setActiveActions({});

            // Reset to running for next sprint
            setTimeout(() => {
              if (quest.status !== 'COMPLETED') {
                setAutoProgress(0);
                setPhaseSummary({attacks: 0, defends: 0, items: 0});
                setBattlePhase('running');
              }
            }, 3000);
          }
          return newProgress;
        });
      }, 300); // Progress every 300ms (100 ticks = 30 seconds)
    }

    return () => {
      if (battleInterval) clearInterval(battleInterval);
      if (progressInterval) clearInterval(progressInterval);
    };
  }, [battlePhase, quest]);

  // Start battle when quest is created
  useEffect(() => {
    if (quest && battlePhase === 'idle') {
      setBattlePhase('running');
    }
  }, [quest]);

  // Create a new quest
  const createQuest = async () => {
    if (!goal.trim()) {
      setError('Please enter a quest goal');
      return;
    }

    const activeMembers = getActivePartyMembers();
    if (activeMembers.length === 0) {
      setError('Please select at least one party member');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/quest/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          party_members: activeMembers,
          budget: 10.0,
          max_tokens: 100000,
        }),
      });

      if (!response.ok) throw new Error('Failed to create quest');

      const data = await response.json();
      setQuest(data);

      // Initialize party stats
      const initialStats: Record<string, { hp: number; maxHp: number; mp: number; maxMp: number }> = {};
      activeMembers.forEach(member => {
        initialStats[member] = { hp: 100, maxHp: 100, mp: 50, maxMp: 50 };
      });
      setPartyStats(initialStats);

      // Add system message
      addChatMessage('system', 'system', 'Quest initiated! Party assembled.', 'system');

      // Connect WebSocket for real-time updates
      const websocket = new WebSocket(`ws://localhost:8766/ws/quest/${data.quest_id}`);
      websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'sprint_complete' || message.type === 'campfire') {
          // Refresh quest data
          fetchQuestStatus(data.quest_id);
        }
      };
      setWs(websocket);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create quest');
    } finally {
      setLoading(false);
    }
  };

  // Fetch quest status
  const fetchQuestStatus = async (questId: string) => {
    try {
      const response = await fetch(`${API_BASE}/quest/${questId}`);
      if (!response.ok) throw new Error('Failed to fetch quest');
      const data = await response.json();
      setQuest(data);
    } catch (err) {
      console.error('Error fetching quest:', err);
    }
  };

  // Execute current sprint
  const executeSprint = async () => {
    if (!quest) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/quest/${quest.quest_id}/sprint/execute`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to execute sprint');

      const data = await response.json();

      // Refresh quest status
      await fetchQuestStatus(quest.quest_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute sprint');
    } finally {
      setLoading(false);
    }
  };

  // Trigger campfire
  const triggerCampfire = async () => {
    if (!quest) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/quest/${quest.quest_id}/campfire`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to trigger campfire');

      await fetchQuestStatus(quest.quest_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger campfire');
    } finally {
      setLoading(false);
    }
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws) ws.close();
    };
  }, [ws]);

  return (
    <ParallaxForest
      layer1={{ scale: 1}} 
      layer2={{ scale: 1}}
      layer3={{ scale: 1 }}
      layer4={{ scale: 1 }}
      maxOffset={75}
    >
      <div className="min-h-screen flex flex-col p-8">
        <div className="max-w-7xl w-full mx-auto">
          {/* Minimal Header */}
          <header className="text-center mb-12 mt-8">
            <h1 className="font-['Newsreader'] text-4xl tracking-[0.3em] text-[#e9c349] uppercase">
              Project Epic
            </h1>
          </header>

          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-100 px-6 py-4 mb-6 max-w-2xl mx-auto">
              {error}
            </div>
          )}

          {/* Quest Input - Always visible */}
          <div className="max-w-2xl mx-auto mb-12">
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Enter your quest..."
              className="w-full bg-transparent border-b-2 border-[#434843] text-[#e5e2e1] py-3 text-2xl text-center
                focus:outline-none focus:border-[#e9c349] transition-colors placeholder:text-[#434843]
                font-['Newsreader'] tracking-wide drop-shadow-[0_2px_8px_rgba(0,0,0,0.9)]"
              style={{ textShadow: '0 2px 8px rgba(0,0,0,0.9)' }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !loading && !quest) {
                  createQuest();
                }
              }}
              disabled={loading || !!quest}
            />
            {loading && (
              <div className="text-center text-[#e9c349] mt-4 animate-pulse">
                ⏳ Assembling quest...
              </div>
            )}
          </div>

          {/* Party Selection - Always visible */}
          <div className="max-w-6xl mx-auto mb-12">
            <h2 className="text-xl text-[#e9c349]/80 mb-16 text-center tracking-[0.3em] uppercase font-light drop-shadow-[0_2px_8px_rgba(0,0,0,0.9)]">
              {quest ? 'Your Party' : 'Select Your Party'}
            </h2>
            <PartySlotSelector
              selectedParty={selectedParty}
              onPartyChange={quest ? undefined : setSelectedParty}
              locked={!!quest}
              partyStats={partyStats}
              onMemberSelect={quest ? setSelectedPartyMember : undefined}
              selectedMemberId={selectedPartyMember}
              onActionSelect={quest ? handleActionSelect : undefined}
              activeActions={activeActions}
              partyAnimations={partyAnimations}
            />
          </div>

          {/* Sprint Display - Top Left (only when quest active) */}
          {quest && (
            <SprintDisplay
              sprints={quest.sprints}
              currentSprintIndex={currentSprintIndex}
            />
          )}

          {/* Sprint Tasks Panel - Top Right (only when quest active) */}
          {quest && quest.sprints[currentSprintIndex] && (
            <SprintTasksPanel
              currentSprint={quest.sprints[currentSprintIndex]}
              progress={autoProgress}
            />
          )}

          {/* Chat Log - Bottom Left (only when quest active) */}
          {quest && (
            <ChatLog messages={chatMessages} />
          )}

          {/* Progress Bar - Horizontal center (only when quest active) */}
          {quest && (
            <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-20 w-96">
              <div className="bg-[#1c1b1b]/80 backdrop-blur-sm px-4 py-2">
                <div className="flex items-center gap-3">
                  {/* Progress Bar */}
                  <div className="flex-1">
                    <div className="h-3 bg-[#353534] border border-[#434843] relative">
                      <div
                        className="h-full bg-gradient-to-r from-[#735c00] to-[#e9c349] transition-all duration-300"
                        style={{ width: `${autoProgress}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-[#8e928c] mt-1 text-center opacity-60">
                      {autoProgress.toFixed(0)}% COMPLETE • {battlePhase.toUpperCase()}
                    </div>
                  </div>

                  {/* Phase Indicator */}
                  <div className="w-10 h-10 flex items-center justify-center text-xl">
                    {battlePhase === 'running' && <span className="animate-pulse">🏃</span>}
                    {battlePhase === 'fighting' && <span className="animate-pulse">⚔️</span>}
                    {battlePhase === 'idle' && <span>✓</span>}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </ParallaxForest>
  );
}
