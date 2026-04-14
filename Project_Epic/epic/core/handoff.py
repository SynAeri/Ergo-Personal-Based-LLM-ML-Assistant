"""
Swarm-style Agent Handoff System

Inspired by OpenAI Swarm (github.com/openai/swarm)
Enables agents to hand off work to other agents mid-conversation.

Pattern:
    Planner completes planning → returns HandoffResult(next_agent="mage")
    → System switches active agent to Mage
    → Mage receives context and continues work
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class HandoffReason(Enum):
    """Why an agent is handing off work"""
    TASK_COMPLETE = "task_complete"      # Agent finished their part
    NEEDS_EXPERTISE = "needs_expertise"  # Requires another agent's skills
    BLOCKED = "blocked"                   # Can't proceed, needs help
    CAMPFIRE = "campfire"                 # Triggering group sync
    ERROR = "error"                       # Something went wrong


@dataclass
class HandoffResult:
    """
    Result of an agent action that may trigger handoff to another agent.

    Similar to OpenAI Swarm's Result class, but adapted for our party system.

    Attributes:
        value: The result message/output from the agent
        next_agent: Agent ID to hand off to (None = no handoff)
        context_updates: New/updated context variables to pass forward
        reason: Why the handoff is happening
        metadata: Additional data (files changed, tests run, etc.)
    """
    value: str
    next_agent: Optional[str] = None
    context_updates: Dict[str, Any] = None
    reason: HandoffReason = HandoffReason.TASK_COMPLETE
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.context_updates is None:
            self.context_updates = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HandoffContext:
    """
    Shared context passed through handoffs.

    This is the "context_variables" from Swarm, but structured for our quest system.
    """
    quest_id: str
    sprint_name: str
    current_phase: str
    goal: str
    files_modified: List[str]
    tests_status: Dict[str, str]
    budget_remaining: float
    tokens_used: int
    agent_outputs: List[Dict[str, Any]]  # History of what each agent did

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for passing to agents"""
        return {
            "quest_id": self.quest_id,
            "sprint_name": self.sprint_name,
            "current_phase": self.current_phase,
            "goal": self.goal,
            "files_modified": self.files_modified,
            "tests_status": self.tests_status,
            "budget_remaining": self.budget_remaining,
            "tokens_used": self.tokens_used,
            "agent_outputs": self.agent_outputs,
        }

    def update(self, updates: Dict[str, Any]) -> "HandoffContext":
        """Create new context with updates"""
        current = self.to_dict()
        current.update(updates)
        return HandoffContext(**current)


class HandoffCoordinator:
    """
    Coordinates agent handoffs during quest execution.

    Similar to Swarm's run() loop, but designed for our party system where:
    - Planner → Mage → Rogue → Tank is a common chain
    - Agents can trigger campfires (gather all agents)
    - Budget/token limits enforced
    - Full handoff history tracked for observability
    """

    def __init__(self, party, max_handoffs: int = 20):
        """
        Args:
            party: Party instance with all agent references
            max_handoffs: Safety limit to prevent infinite loops
        """
        self.party = party
        self.max_handoffs = max_handoffs
        self.handoff_history: List[Dict[str, Any]] = []

    def execute_with_handoff(
        self,
        starting_agent_id: str,
        task: str,
        context: HandoffContext,
    ) -> HandoffResult:
        """
        Execute a task starting with one agent, following handoffs.

        This is the core Swarm pattern:
        1. Agent executes task
        2. If result includes next_agent, hand off
        3. New agent receives updated context
        4. Repeat until no handoff or max_handoffs reached

        Args:
            starting_agent_id: Which agent starts (usually "planner")
            task: The task description
            context: Shared context

        Returns:
            Final HandoffResult after all handoffs complete
        """
        current_agent_id = starting_agent_id
        current_task = task
        current_context = context
        handoff_count = 0

        while handoff_count < self.max_handoffs:
            # Get agent
            agent = self.party.get_agent(current_agent_id)
            if not agent:
                raise ValueError(f"Agent {current_agent_id} not found in party")

            # Record handoff
            self.handoff_history.append({
                "agent_id": current_agent_id,
                "task": current_task,
                "handoff_count": handoff_count,
            })

            # Execute agent action
            result = agent.invoke(
                task=current_task,
                context=current_context.to_dict(),
            )

            # Convert agent output to HandoffResult if needed
            if not isinstance(result, HandoffResult):
                result = HandoffResult(value=str(result))

            # Update context
            current_context = current_context.update(result.context_updates)
            current_context.agent_outputs.append({
                "agent_id": current_agent_id,
                "output": result.value,
                "metadata": result.metadata,
            })

            # Check for handoff
            if not result.next_agent:
                # No more handoffs, task complete
                return result

            # Hand off to next agent
            current_agent_id = result.next_agent
            current_task = result.value  # Next agent works on this output
            handoff_count += 1

        # Hit max handoffs - return with warning
        return HandoffResult(
            value=f"Max handoffs ({self.max_handoffs}) reached. Last output: {result.value}",
            next_agent=None,
            metadata={"warning": "max_handoffs_reached", "handoff_history": self.handoff_history}
        )

    def get_handoff_chain(self) -> List[str]:
        """Get the sequence of agents that executed"""
        return [h["agent_id"] for h in self.handoff_history]

    def visualize_handoff_chain(self) -> str:
        """Pretty-print the handoff chain"""
        if not self.handoff_history:
            return "No handoffs yet"

        chain = " → ".join(self.get_handoff_chain())
        return f"Handoff chain: {chain}"


# Common handoff patterns for convenience

def handoff_to(agent_id: str, message: str, reason: HandoffReason = HandoffReason.TASK_COMPLETE, **context_updates) -> HandoffResult:
    """
    Convenience function for agents to hand off work.

    Usage in agent:
        return handoff_to("mage", "I've planned the approach. Mage, please design the architecture.",
                         files_to_review=["src/auth.rs"])
    """
    return HandoffResult(
        value=message,
        next_agent=agent_id,
        context_updates=context_updates,
        reason=reason,
    )


def complete_task(message: str, **metadata) -> HandoffResult:
    """
    Convenience function for agents to complete without handoff.

    Usage in agent:
        return complete_task("Authentication implemented successfully",
                           files_changed=["src/auth.rs"])
    """
    return HandoffResult(
        value=message,
        next_agent=None,
        metadata=metadata,
    )


def trigger_campfire(message: str, **context_updates) -> HandoffResult:
    """
    Convenience function to trigger a campfire sync.

    Usage in agent:
        return trigger_campfire("Tests are failing. We need to regroup.",
                               test_failures=["auth/token_test.rs"])
    """
    return HandoffResult(
        value=message,
        next_agent="campfire",  # Special agent ID
        context_updates=context_updates,
        reason=HandoffReason.CAMPFIRE,
    )


# Example usage patterns:

"""
# In Planner agent:
def invoke(self, task, context):
    plan = self.create_plan(task)
    return handoff_to("mage", f"I've created a plan: {plan}. Please review the architecture.",
                     plan=plan)

# In Mage agent:
def invoke(self, task, context):
    architecture = self.design_architecture(context["plan"])
    return handoff_to("rogue", f"Architecture designed: {architecture}. Implement it.",
                     architecture=architecture)

# In Rogue agent:
def invoke(self, task, context):
    self.write_code(context["architecture"])
    return handoff_to("tank", "Code written. Please test it.",
                     files_changed=["src/auth.rs"])

# In Tank agent:
def invoke(self, task, context):
    test_result = self.run_tests()
    if test_result.failed:
        return trigger_campfire("Tests failing. Need to discuss approach.")
    return complete_task("All tests passing!", tests_passed=test_result.count)


# In orchestrator:
coordinator = HandoffCoordinator(party)
result = coordinator.execute_with_handoff(
    starting_agent_id="planner",
    task="Implement JWT authentication",
    context=HandoffContext(
        quest_id="quest_123",
        sprint_name="Protect the Royal Seal",
        current_phase="sprint_1",
        goal="Implement JWT authentication",
        files_modified=[],
        tests_status={},
        budget_remaining=10.0,
        tokens_used=0,
        agent_outputs=[],
    )
)

print(coordinator.visualize_handoff_chain())
# Output: Handoff chain: planner → mage → rogue → tank
"""
