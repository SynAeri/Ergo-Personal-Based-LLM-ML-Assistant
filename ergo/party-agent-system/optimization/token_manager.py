"""
Token Manager - Optimize token usage across party agents
Implements caching, compression, and smart context management
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class TokenUsage:
    """Track token usage for a single interaction"""
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    timestamp: datetime
    agent_role: str
    cost: float


class TokenManager:
    """
    Manages token optimization across the party system

    Strategies:
    1. Prompt Caching - Cache personality prompts
    2. Context Compression - Summarize old conversations
    3. Smart Routing - Only send relevant context to each agent
    4. Incremental Updates - Send diffs, not full files
    """

    def __init__(self, max_context_tokens: int = 100_000):
        self.max_context_tokens = max_context_tokens
        self.usage_history: List[TokenUsage] = []

        # Token costs per model (per million tokens)
        self.model_costs = {
            "claude-sonnet-3.5": {
                "input": 3.00,
                "output": 15.00,
                "cache_write": 3.75,  # 25% premium for cache writes
                "cache_read": 0.30    # 90% discount on cache reads
            },
            "claude-opus-3": {
                "input": 15.00,
                "output": 75.00,
                "cache_write": 18.75,
                "cache_read": 1.50
            },
            "gemini-2.0-flash": {
                "input": 0.075,
                "output": 0.30,
                "cache_write": 0.075,
                "cache_read": 0.075  # Gemini doesn't have prompt caching
            }
        }

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        model: str = "claude-sonnet-3.5"
    ) -> float:
        """Calculate cost for a model call with caching"""
        if model not in self.model_costs:
            model = "claude-sonnet-3.5"  # Default

        costs = self.model_costs[model]

        # Uncached input tokens
        uncached_input = input_tokens - cached_tokens

        cost = (
            (uncached_input * costs["input"] / 1_000_000) +
            (cached_tokens * costs["cache_read"] / 1_000_000) +
            (output_tokens * costs["output"] / 1_000_000)
        )

        return round(cost, 4)

    def track_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        agent_role: str,
        model: str = "claude-sonnet-3.5"
    ):
        """Record token usage for analytics"""
        cost = self.calculate_cost(input_tokens, output_tokens, cached_tokens, model)

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            timestamp=datetime.now(),
            agent_role=agent_role,
            cost=cost
        )

        self.usage_history.append(usage)

    def get_total_tokens_used(self) -> int:
        """Get total tokens used across all agents"""
        return sum(
            u.input_tokens + u.output_tokens
            for u in self.usage_history
        )

    def get_total_cost(self) -> float:
        """Get total cost across all agents"""
        return sum(u.cost for u in self.usage_history)

    def get_tokens_saved_by_caching(self) -> int:
        """Calculate tokens saved via prompt caching"""
        return sum(u.cached_tokens for u in self.usage_history)

    def get_cost_saved_by_caching(self) -> float:
        """Calculate cost saved via prompt caching"""
        # If we hadn't cached, we'd pay full input price
        saved = 0.0
        for usage in self.usage_history:
            if usage.cached_tokens > 0:
                # Cost we would have paid
                full_cost = usage.cached_tokens * 3.00 / 1_000_000
                # Cost we actually paid
                cached_cost = usage.cached_tokens * 0.30 / 1_000_000
                saved += (full_cost - cached_cost)

        return round(saved, 4)

    def compress_conversation_history(
        self,
        messages: List[Dict[str, str]],
        target_tokens: int = 10_000,
        keep_recent: int = 5
    ) -> List[Dict[str, str]]:
        """
        Compress old conversation history

        Strategy:
        - Keep recent N messages at full fidelity
        - Summarize older messages into key points
        - Always keep system prompt
        """
        if len(messages) <= keep_recent + 1:  # +1 for system prompt
            return messages

        # Separate system, old, and recent messages
        system_msg = messages[0] if messages[0].get("role") == "system" else None
        start_idx = 1 if system_msg else 0

        recent_messages = messages[-keep_recent:]
        old_messages = messages[start_idx:-keep_recent]

        # Summarize old messages
        summary = self._create_conversation_summary(old_messages)

        # Reconstruct: [system] + [summary] + [recent messages]
        compressed = []
        if system_msg:
            compressed.append(system_msg)

        if summary:
            compressed.append({
                "role": "user",
                "content": f"[Conversation Summary - Previous Context]\n{summary}"
            })

        compressed.extend(recent_messages)

        return compressed

    def _create_conversation_summary(self, messages: List[Dict[str, str]]) -> str:
        """Create a summary of conversation messages"""
        if not messages:
            return ""

        # Extract key points
        key_actions = []
        decisions = []

        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")

            # Extract tool uses
            if "write_file" in content.lower():
                key_actions.append("Modified code files")
            if "run_tests" in content.lower():
                key_actions.append("Ran tests")
            if "search" in content.lower():
                key_actions.append("Searched codebase/memory")

            # Extract decisions (user confirmations)
            if role == "user" and any(word in content.lower() for word in ["yes", "approved", "proceed"]):
                decisions.append("User approved proceeding")

        summary_parts = []
        if key_actions:
            summary_parts.append(f"Actions taken: {', '.join(set(key_actions))}")
        if decisions:
            summary_parts.append(f"Decisions: {', '.join(decisions)}")

        return "\n".join(summary_parts) if summary_parts else "Previous discussion context"

    def optimize_context_for_agent(
        self,
        agent_role: str,
        full_context: Dict[str, Any],
        quest_phase: str
    ) -> Dict[str, Any]:
        """
        Send only relevant context to each agent

        Token savings strategy:
        - Planner needs high-level context, not implementation details
        - Rogue needs implementation details, not architectural rationale
        - Tank needs test context, not planning discussions
        """
        optimized = {
            "quest_goal": full_context.get("quest_goal"),
            "current_phase": quest_phase
        }

        # Role-specific context filtering
        if agent_role == "planner":
            optimized["relevant_info"] = [
                full_context.get("quest_goal"),
                full_context.get("project_structure"),
                full_context.get("constraints")
            ]

        elif agent_role == "mage":
            optimized["relevant_info"] = [
                full_context.get("architecture_decisions"),
                full_context.get("technical_constraints"),
                full_context.get("patterns_used")
            ]

        elif agent_role == "rogue":
            optimized["relevant_info"] = [
                full_context.get("implementation_plan"),
                full_context.get("code_files"),
                full_context.get("dependencies")
            ]

        elif agent_role == "tank":
            optimized["relevant_info"] = [
                full_context.get("test_requirements"),
                full_context.get("code_changes"),
                full_context.get("previous_test_results")
            ]

        elif agent_role == "support":
            optimized["relevant_info"] = [
                full_context.get("memory_query"),
                full_context.get("search_scope")
            ]

        elif agent_role == "healer":
            optimized["relevant_info"] = [
                full_context.get("quest_summary"),
                full_context.get("lessons_learned"),
                full_context.get("decisions_made")
            ]

        return optimized

    def create_cacheable_blocks(
        self,
        personality_prompt: str,
        codebase_context: str
    ) -> List[Dict[str, Any]]:
        """
        Create cache-enabled content blocks for Claude

        Cache strategy:
        - Personality prompts (static, rarely change)
        - Codebase structure (changes infrequently)
        - Recent conversation (changes every turn - DON'T cache)
        """
        blocks = [
            {
                "type": "text",
                "text": personality_prompt,
                "cache_control": {"type": "ephemeral"}  # Cache personality
            },
            {
                "type": "text",
                "text": f"## Codebase Context\n\n{codebase_context}",
                "cache_control": {"type": "ephemeral"}  # Cache codebase
            }
        ]

        return blocks

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Rough estimation: 1 token ≈ 4 characters for English
        More accurate would use tiktoken, but this is fast
        """
        return len(text) // 4

    def should_compress_context(self, messages: List[Dict[str, str]]) -> bool:
        """Determine if context should be compressed"""
        total_tokens = sum(
            self.estimate_tokens(msg.get("content", ""))
            for msg in messages
        )

        return total_tokens > (self.max_context_tokens * 0.7)  # 70% threshold

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get detailed optimization statistics"""
        if not self.usage_history:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "tokens_saved": 0,
                "cost_saved": 0.0,
                "cache_hit_rate": 0.0
            }

        total_input = sum(u.input_tokens for u in self.usage_history)
        total_cached = sum(u.cached_tokens for u in self.usage_history)
        cache_hit_rate = (total_cached / total_input * 100) if total_input > 0 else 0.0

        return {
            "total_tokens": self.get_total_tokens_used(),
            "total_cost": self.get_total_cost(),
            "tokens_saved": self.get_tokens_saved_by_caching(),
            "cost_saved": self.get_cost_saved_by_caching(),
            "cache_hit_rate": round(cache_hit_rate, 1),
            "agent_breakdown": self._get_agent_breakdown()
        }

    def _get_agent_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Break down usage by agent role"""
        breakdown = {}

        for usage in self.usage_history:
            role = usage.agent_role
            if role not in breakdown:
                breakdown[role] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "calls": 0
                }

            breakdown[role]["total_tokens"] += usage.input_tokens + usage.output_tokens
            breakdown[role]["total_cost"] += usage.cost
            breakdown[role]["calls"] += 1

        return breakdown

    def export_stats(self, filepath: str):
        """Export optimization stats to JSON"""
        stats = self.get_optimization_stats()
        stats["timestamp"] = datetime.now().isoformat()
        stats["usage_history"] = [
            {
                "agent": u.agent_role,
                "input_tokens": u.input_tokens,
                "output_tokens": u.output_tokens,
                "cached_tokens": u.cached_tokens,
                "cost": u.cost,
                "timestamp": u.timestamp.isoformat()
            }
            for u in self.usage_history
        ]

        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)


# Example usage
if __name__ == "__main__":
    manager = TokenManager(max_context_tokens=100_000)

    # Simulate party quest
    print("🎮 Quest Started: Implement JWT Authentication")
    print()

    # Planner phase
    manager.track_usage(
        input_tokens=5000,
        output_tokens=1500,
        cached_tokens=3000,  # Personality prompt cached
        agent_role="planner"
    )
    print("🗺️  Planner completed task decomposition")

    # Mage phase
    manager.track_usage(
        input_tokens=6000,
        output_tokens=2000,
        cached_tokens=3500,
        agent_role="mage"
    )
    print("🧙 Mage completed architecture design")

    # Rogue phase
    manager.track_usage(
        input_tokens=8000,
        output_tokens=3000,
        cached_tokens=4000,
        agent_role="rogue"
    )
    print("⚔️  Rogue completed code implementation")

    # Tank phase
    manager.track_usage(
        input_tokens=4000,
        output_tokens=1000,
        cached_tokens=2500,
        agent_role="tank"
    )
    print("🛡️  Tank completed verification")

    print()
    print("📊 Quest Statistics:")
    stats = manager.get_optimization_stats()
    print(f"  Total Tokens: {stats['total_tokens']:,}")
    print(f"  Total Cost: ${stats['total_cost']:.2f}")
    print(f"  Tokens Saved (Caching): {stats['tokens_saved']:,}")
    print(f"  Cost Saved (Caching): ${stats['cost_saved']:.2f}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']}%")
    print()
    print("  Agent Breakdown:")
    for role, data in stats['agent_breakdown'].items():
        print(f"    {role.title()}: {data['total_tokens']:,} tokens, ${data['total_cost']:.2f}, {data['calls']} calls")
