"""
Claude Agent - Base class for party members
Each agent is a Claude instance with a unique personality
"""

import os
import anthropic
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json


class ClaudeAgent:
    """
    A Claude instance with a specific personality/role

    Each party member is an independent Claude conversation with:
    - Unique personality loaded from markdown file
    - Role-specific permissions
    - Conversation history
    - Token/cost tracking
    """

    def __init__(
        self,
        role_name: str,
        personality_file: str,
        model: str = "claude-sonnet-3.5",
        permissions: Optional[Dict[str, Any]] = None,
        simulation_mode: bool = False
    ):
        self.role_name = role_name
        self.model = model
        self.permissions = permissions or self._default_permissions()
        self.simulation_mode = simulation_mode

        # Load personality prompt
        self.personality = self._load_personality(personality_file)

        # Conversation state
        self.conversation_history: List[Dict[str, Any]] = []
        self.tools_used: List[Dict[str, Any]] = []

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        self.total_cost = 0.0

        # Claude client (skip in simulation mode)
        self.client = None
        if not simulation_mode:
            from ..config import ANTHROPIC_API_KEY
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set. Create .env file or set environment variable.")
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def _load_personality(self, personality_file: str) -> str:
        """Load personality prompt from markdown file"""
        # Look in personalities/ directory
        personality_path = Path(__file__).parent.parent.parent / "personalities" / personality_file

        if not personality_path.exists():
            raise FileNotFoundError(f"Personality file not found: {personality_path}")

        return personality_path.read_text()

    def _default_permissions(self) -> Dict[str, Any]:
        """Default permissions for an agent"""
        return {
            "can_read_files": True,
            "can_write_files": False,
            "can_execute_shell": False,
            "shell_allowlist": [],
            "file_scope": None,
            "allowed_tools": []
        }

    def check_permission(self, tool_name: str, **kwargs) -> bool:
        """Check if agent has permission to use a tool"""
        # Read permission
        if tool_name in ["read_file", "search_codebase"]:
            return self.permissions.get("can_read_files", True)

        # Write permission
        if tool_name in ["write_file", "edit_file", "delete_file"]:
            if not self.permissions.get("can_write_files", False):
                return False

            # Check file scope
            file_path = kwargs.get("path", "")
            file_scope = self.permissions.get("file_scope")
            if file_scope and not file_path.startswith(file_scope):
                return False

        # Shell execution
        if tool_name == "run_command":
            if not self.permissions.get("can_execute_shell", False):
                return False

            command = kwargs.get("command", "")
            shell_allowlist = self.permissions.get("shell_allowlist", [])
            if shell_allowlist:
                cmd_base = command.split()[0] if command else ""
                if cmd_base not in shell_allowlist:
                    return False

        # Tool allowlist
        allowed_tools = self.permissions.get("allowed_tools", [])
        if allowed_tools and tool_name not in allowed_tools:
            return False

        return True

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools for this agent

        Tools are filtered by permissions
        """
        all_tools = [
            {
                "name": "write_file",
                "description": "⚔️ Code Strike - Write or modify a code file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"},
                        "reason": {"type": "string", "description": "Why this change is needed"}
                    },
                    "required": ["path", "content", "reason"]
                }
            },
            {
                "name": "read_file",
                "description": "📖 Read Scroll - Read a code file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_code",
                "description": "🔍 Scrying Search - Search for code patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Search pattern/keyword"},
                        "file_pattern": {"type": "string", "description": "File pattern (e.g., '*.rs')"}
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "run_command",
                "description": "🎯 Execute Skill - Run a shell command",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"},
                        "purpose": {"type": "string", "description": "Why you're running this"}
                    },
                    "required": ["command", "purpose"]
                }
            },
            {
                "name": "run_tests",
                "description": "🧪 Alchemical Test - Run the test suite",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "test_path": {"type": "string", "description": "Specific test path (optional)"}
                    }
                }
            },
            {
                "name": "search_memory",
                "description": "📚 Memory Recall - Search Ergo's memory/vault",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "What to search for"},
                        "scope": {"type": "string", "description": "Memory scope (project, session, etc.)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_plan",
                "description": "🗺️ Chart the Path - Create a task plan",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string", "description": "What needs to be accomplished"},
                        "steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of steps to accomplish the goal"
                        }
                    },
                    "required": ["goal", "steps"]
                }
            }
        ]

        # Filter by permissions
        allowed_tools = []
        for tool in all_tools:
            # Basic permission check
            if self.check_permission(tool["name"]):
                allowed_tools.append(tool)

        return allowed_tools

    async def send_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        use_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Send a message to this agent and get response

        Returns:
            {
                "response": str,
                "tool_calls": List[Dict],
                "tokens": {"input": int, "output": int, "cached": int},
                "cost": float
            }
        """
        # Build messages
        messages = self.conversation_history.copy()

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages.append({
                "role": "user",
                "content": f"[Context]\n{context_str}\n\n[Task]\n{message}"
            })
        else:
            messages.append({"role": "user", "content": message})

        # Create system blocks with caching
        system_blocks = [
            {
                "type": "text",
                "text": self.personality,
                "cache_control": {"type": "ephemeral"}  # Cache personality
            }
        ]

        # Call Claude
        try:
            response = self.client.messages.create(
                model=self._get_model_id(),
                max_tokens=4096,
                system=system_blocks,
                messages=messages,
                tools=self.get_tools() if use_tools else None
            )

            # Track tokens
            usage = response.usage
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens
            self.total_cached_tokens += getattr(usage, 'cache_read_input_tokens', 0)

            # Calculate cost
            cost = self._calculate_cost(
                usage.input_tokens,
                usage.output_tokens,
                getattr(usage, 'cache_read_input_tokens', 0)
            )
            self.total_cost += cost

            # Process response
            result = {
                "response": "",
                "tool_calls": [],
                "tokens": {
                    "input": usage.input_tokens,
                    "output": usage.output_tokens,
                    "cached": getattr(usage, 'cache_read_input_tokens', 0)
                },
                "cost": cost
            }

            # Extract text and tool calls
            for block in response.content:
                if block.type == "text":
                    result["response"] += block.text
                elif block.type == "tool_use":
                    tool_call = {
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    }
                    result["tool_calls"].append(tool_call)
                    self.tools_used.append({
                        "timestamp": datetime.now().isoformat(),
                        "tool": block.name,
                        "input": block.input
                    })

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            return result

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "tokens": {"input": 0, "output": 0, "cached": 0},
                "cost": 0.0,
                "error": str(e)
            }

    def _get_model_id(self) -> str:
        """Map model names to Claude API IDs"""
        model_map = {
            "claude-opus": "claude-3-opus-20240229",
            "claude-opus-3": "claude-3-opus-20240229",
            "claude-sonnet": "claude-3-5-sonnet-20241022",
            "claude-sonnet-3.5": "claude-3-5-sonnet-20241022",
            "claude-haiku": "claude-3-5-haiku-20241022"
        }
        return model_map.get(self.model, self.model)

    def _calculate_cost(self, input_tokens: int, output_tokens: int, cached_tokens: int) -> float:
        """Calculate cost for this model call"""
        # Claude Sonnet 3.5 pricing (per million tokens)
        costs = {
            "claude-sonnet-3.5": {
                "input": 3.00,
                "output": 15.00,
                "cache_read": 0.30
            },
            "claude-opus-3": {
                "input": 15.00,
                "output": 75.00,
                "cache_read": 1.50
            }
        }

        model_costs = costs.get(self.model, costs["claude-sonnet-3.5"])

        uncached_input = input_tokens - cached_tokens

        cost = (
            (uncached_input * model_costs["input"] / 1_000_000) +
            (cached_tokens * model_costs["cache_read"] / 1_000_000) +
            (output_tokens * model_costs["output"] / 1_000_000)
        )

        return round(cost, 4)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as readable text"""
        lines = []
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                lines.append(f"{key}:\n{json.dumps(value, indent=2)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "role": self.role_name,
            "model": self.model,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cached_tokens": self.total_cached_tokens,
            "total_cost": self.total_cost,
            "tools_used": len(self.tools_used),
            "turns": len(self.conversation_history) // 2
        }

    def reset_conversation(self):
        """Reset conversation history (keep personality)"""
        self.conversation_history = []

    def compress_history(self, keep_recent: int = 5):
        """Compress old conversation history"""
        if len(self.conversation_history) <= keep_recent * 2:
            return

        # Keep recent messages
        recent = self.conversation_history[-keep_recent * 2:]

        # Summarize old messages
        old = self.conversation_history[:-keep_recent * 2]
        summary = self._summarize_conversation(old)

        # Rebuild history
        self.conversation_history = [
            {"role": "user", "content": f"[Previous conversation summary]\n{summary}"}
        ] + recent

    def _summarize_conversation(self, messages: List[Dict]) -> str:
        """Create a brief summary of old messages"""
        actions = []
        for msg in messages:
            if msg.get("role") == "assistant":
                content = str(msg.get("content", ""))
                if "write_file" in content.lower():
                    actions.append("Modified code files")
                if "run_tests" in content.lower():
                    actions.append("Ran tests")

        return f"Previous actions: {', '.join(set(actions)) if actions else 'Initial discussion'}"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        # Create a Rogue agent (code executor)
        rogue = ClaudeAgent(
            role_name="rogue",
            personality_file="rogue.md",
            model="claude-sonnet-3.5",
            permissions={
                "can_write_files": True,
                "can_execute_shell": True,
                "shell_allowlist": ["cargo", "git"]
            }
        )

        # Send a task
        result = await rogue.send_message(
            "We need to implement a simple authentication function in Rust. Create src/auth.rs with a basic JWT validation function."
        )

        print(f"Rogue says: {result['response']}")
        print(f"Tool calls: {len(result['tool_calls'])}")
        print(f"Cost: ${result['cost']:.4f}")
        print(f"\nStats: {rogue.get_stats()}")

    asyncio.run(test_agent())
