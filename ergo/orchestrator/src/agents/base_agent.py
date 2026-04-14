"""
Base Agent for Ergo Work Mode
Abstract base class for all role-based agents
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import sqlite3


class BaseAgent(ABC):
    """Base class for all Ergo agents with permission checking and tool execution"""

    def __init__(
        self,
        role_name: str,
        db_path: str = "~/ergo/runtime/missions.db",
        config_path: str = "~/ergo/config/permissions.toml"
    ):
        self.role_name = role_name
        self.db_path = Path(db_path).expanduser()
        self.config_path = Path(config_path).expanduser()

        # Load permissions for this role
        self.permissions = self._load_permissions()

        # Load role definition from database
        self.role_definition = self._load_role_definition()

        # Tool call history
        self.tool_calls = []

    def _load_permissions(self) -> Dict[str, Any]:
        """Load permission configuration for this role"""
        # For now, return default permissions
        # TODO: Parse TOML file when available
        return {
            "can_read_files": True,
            "can_write_files": False,
            "can_execute_shell": False,
            "shell_allowlist": [],
            "file_scope": None,
            "memory_scopes": ["working"],
            "allowed_tools": []
        }

    def _load_role_definition(self) -> Dict[str, Any]:
        """Load role definition from database"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM role_definitions WHERE role_name = ?",
            (self.role_name,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Role definition not found: {self.role_name}")

        return dict(row)

    def check_permission(self, tool_name: str, **kwargs) -> bool:
        """Check if agent has permission to use a tool with given parameters"""

        # File write check
        if tool_name in ["write_file", "edit_file", "delete_file"]:
            if not self.permissions.get("can_write_files", False):
                return False

            # Check file scope if specified
            file_path = kwargs.get("path", "")
            file_scope = self.permissions.get("file_scope")
            if file_scope and not file_path.startswith(file_scope):
                return False

        # Shell execution check
        if tool_name == "execute_shell":
            if not self.permissions.get("can_execute_shell", False):
                return False

            # Check shell allowlist
            command = kwargs.get("command", "")
            shell_allowlist = self.permissions.get("shell_allowlist", [])

            if shell_allowlist:
                cmd_base = command.split()[0] if command else ""
                if cmd_base not in shell_allowlist:
                    return False

        # Memory access check
        if tool_name == "read_memory":
            memory_type = kwargs.get("memory_type", "")
            allowed_scopes = self.permissions.get("memory_scopes", [])
            if memory_type not in allowed_scopes:
                return False

        return True

    def log_tool_call(self, tool_name: str, params: Dict, result: Any, success: bool):
        """Log a tool call for auditing"""
        self.tool_calls.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params,
            "success": success,
            "result_summary": str(result)[:200]  # Truncate long results
        })

    def get_tool_call_history(self) -> List[Dict]:
        """Get history of tool calls made by this agent"""
        return self.tool_calls

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent role"""
        pass

    @abstractmethod
    def process_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a mission step and return results

        Args:
            step: Mission step dictionary with objective, input_context, etc.
            context: Additional context (memories, files, etc.)

        Returns:
            Dictionary with output_summary, cost_estimate, tool_calls, success
        """
        pass

    def format_output(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Format agent output consistently"""
        return {
            "role": self.role_name,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "tool_calls": self.tool_calls
        }

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for a model call"""
        # Cost per million tokens
        costs = {
            "claude-opus": {"input": 15.00, "output": 75.00},
            "claude-sonnet": {"input": 3.00, "output": 15.00},
            "claude-haiku": {"input": 0.25, "output": 1.25},
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00}
        }

        if model not in costs:
            # Default to mid-range cost
            return (input_tokens * 3.00 + output_tokens * 15.00) / 1_000_000

        cost_config = costs[model]
        return (
            input_tokens * cost_config["input"] / 1_000_000 +
            output_tokens * cost_config["output"] / 1_000_000
        )

    def call_model(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Call an AI model with the given messages

        Args:
            messages: List of message dictionaries with role and content
            model: Model identifier (uses role's preferred model if not specified)
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with response, tokens, cost
        """
        # Use preferred model if not specified
        if not model:
            preferred_models = self.role_definition.get('preferred_models', '').split(',')
            model = preferred_models[0] if preferred_models else "claude-sonnet"

        # Add system prompt
        system_prompt = self.get_system_prompt()

        # Determine which API to use based on model
        if model.startswith("claude"):
            return self._call_anthropic(messages, model, system_prompt, max_tokens)
        elif model.startswith("gemini"):
            return self._call_google(messages, model, system_prompt, max_tokens)
        elif model.startswith("gpt"):
            return self._call_openai(messages, model, system_prompt, max_tokens)
        else:
            raise ValueError(f"Unknown model: {model}")

    def _call_anthropic(
        self,
        messages: List[Dict],
        model: str,
        system_prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Anthropic API"""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        client = anthropic.Anthropic(api_key=api_key)

        # Map model names
        model_map = {
            "claude-opus": "claude-3-opus-20240229",
            "claude-sonnet": "claude-3-5-sonnet-20241022",
            "claude-haiku": "claude-3-5-haiku-20241022"
        }

        response = client.messages.create(
            model=model_map.get(model, model),
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = self.estimate_cost(input_tokens, output_tokens, model)

        return {
            "response": response.content[0].text,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "success": True
        }

    def _call_google(
        self,
        messages: List[Dict],
        model: str,
        system_prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Google AI API"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Map model names
        model_map = {
            "gemini-2.5-flash": "gemini-2.0-flash-exp",
            "gemini-2.5-pro": "gemini-2.0-pro-exp"
        }

        client = genai.GenerativeModel(
            model_name=model_map.get(model, model),
            system_instruction=system_prompt
        )

        # Convert messages to Gemini format
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })

        chat = client.start_chat(history=history)
        response = chat.send_message(
            messages[-1]["content"],
            generation_config=genai.GenerationConfig(max_output_tokens=max_tokens)
        )

        # Estimate tokens (Gemini doesn't provide exact counts easily)
        input_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)
        output_tokens = len(response.text.split()) * 1.3
        cost = self.estimate_cost(int(input_tokens), int(output_tokens), model)

        return {
            "response": response.text,
            "model": model,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "cost": cost,
            "success": True
        }

    def _call_openai(
        self,
        messages: List[Dict],
        model: str,
        system_prompt: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        client = OpenAI(api_key=api_key)

        # Add system message
        messages_with_system = [{"role": "system", "content": system_prompt}] + messages

        response = client.chat.completions.create(
            model=model,
            messages=messages_with_system,
            max_tokens=max_tokens
        )

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self.estimate_cost(input_tokens, output_tokens, model)

        return {
            "response": response.choices[0].message.content,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "success": True
        }
