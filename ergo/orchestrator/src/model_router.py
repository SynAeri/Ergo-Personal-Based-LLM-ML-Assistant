"""
Model routing for Ergo orchestrator
Routes requests to appropriate models based on task type
"""

from enum import Enum
from typing import Optional, List, Dict, Any
import anthropic
import google.generativeai as genai
from openai import OpenAI
from .config import settings
import logging

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Model types for different workloads"""
    GEMINI = "gemini"
    OPUS = "opus"
    LOCAL = "local"
    SONNET = "sonnet"


class TaskType(str, Enum):
    """Task types that determine model routing"""
    GENERAL_CHAT = "general_chat"
    CODE_REVIEW = "code_review"
    DEBUG_HELP = "debug_help"
    EVENT_TAGGING = "event_tagging"
    SESSION_SUMMARY = "session_summary"
    INTERVENTION_CHECK = "intervention_check"


class ModelRouter:
    """Routes requests to appropriate models based on task type"""

    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.gemini_configured = False

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize API clients"""
        # Anthropic (for Opus/Sonnet)
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
            logger.info("Anthropic client initialized")

        # Google AI (for Gemini)
        if settings.google_ai_api_key:
            genai.configure(api_key=settings.google_ai_api_key)
            self.gemini_configured = True
            logger.info("Google AI (Gemini) configured")

        # OpenAI (optional)
        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")

    def route_task(self, task_type: TaskType) -> ModelType:
        """Determine which model to use for a given task type"""
        routing_map = {
            TaskType.GENERAL_CHAT: ModelType.SONNET,
            TaskType.CODE_REVIEW: ModelType.OPUS,
            TaskType.DEBUG_HELP: ModelType.SONNET,
            TaskType.EVENT_TAGGING: ModelType.SONNET,
            TaskType.SESSION_SUMMARY: ModelType.SONNET,
            TaskType.INTERVENTION_CHECK: ModelType.SONNET,
        }

        model = routing_map.get(task_type, ModelType.GEMINI)
        logger.info(f"Routing {task_type} to {model}")
        return model

    async def generate_response(
        self,
        task_type: TaskType,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response using the appropriate model"""
        model_type = self.route_task(task_type)

        try:
            if model_type == ModelType.GEMINI:
                return await self._generate_gemini(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif model_type == ModelType.OPUS:
                return await self._generate_opus(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif model_type == ModelType.SONNET:
                return await self._generate_sonnet(
                    prompt, system_prompt, max_tokens, temperature
                )
            elif model_type == ModelType.LOCAL:
                return await self._generate_local(
                    prompt, system_prompt, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unknown model type: {model_type}")

        except Exception as e:
            logger.error(f"Error generating response with {model_type}: {e}")
            raise

    async def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate response using Google Gemini"""
        if not self.gemini_configured:
            raise RuntimeError("Gemini not configured")

        model = genai.GenerativeModel("gemini-2.5-flash")

        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )

        return response.text

    async def _generate_opus(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate response using Anthropic Claude Opus"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        messages = [{"role": "user", "content": prompt}]

        response = self.anthropic_client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text

    async def _generate_sonnet(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate response using Anthropic Claude Sonnet"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        messages = [{"role": "user", "content": prompt}]

        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text

    async def _generate_local(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate response using local model (stub for now)"""
        # TODO: Implement local model inference
        # For now, fall back to Gemini if available
        logger.warning("Local model not implemented, falling back to Gemini")
        if self.gemini_configured:
            return await self._generate_gemini(
                prompt, system_prompt, max_tokens, temperature
            )
        else:
            return "Local model not available. Please configure a model API."

    async def generate_chat_response(
        self,
        user_message: str,
        context: Optional[str] = None,
        persona_mode: str = "standard",
    ) -> str:
        """Generate a chat response with context and persona"""
        system_prompt = self._build_system_prompt(persona_mode)

        if context:
            full_prompt = f"Context:\n{context}\n\nUser: {user_message}"
        else:
            full_prompt = user_message

        return await self.generate_response(
            TaskType.GENERAL_CHAT,
            full_prompt,
            system_prompt=system_prompt,
        )

    async def generate_code_review(
        self, code: str, language: str, context: str
    ) -> str:
        """Generate a code review using Opus"""
        system_prompt = (
            "You are an expert code reviewer. "
            "Analyze the code for bugs, performance issues, and best practices. "
            "Be concise and actionable."
        )

        prompt = f"Language: {language}\n\nContext: {context}\n\nCode:\n```\n{code}\n```"

        return await self.generate_response(
            TaskType.CODE_REVIEW,
            prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
        )

    async def generate_session_summary(
        self, events: List[Dict[str, Any]], duration_minutes: int
    ) -> str:
        """Generate a session summary from events"""
        system_prompt = (
            "You are summarizing a work session. "
            "Be concise and focus on key activities and context switches."
        )

        # Format events for prompt
        event_lines = []
        for event in events:
            event_lines.append(
                f"- {event.get('timestamp')}: {event.get('event_type')} - {event.get('payload', {})}"
            )

        events_text = "\n".join(event_lines[:50])  # Limit to 50 events

        prompt = f"Session duration: {duration_minutes} minutes\n\nEvents:\n{events_text}\n\nProvide a 2-3 sentence summary of this work session."

        return await self.generate_response(
            TaskType.SESSION_SUMMARY,
            prompt,
            system_prompt=system_prompt,
            max_tokens=256,
            temperature=0.3,
        )

    def _build_system_prompt(self, persona_mode: str) -> str:
        """Build system prompt with persona layer"""
        base_prompt = (
            "You are Ergo, a local-first AI assistant for developers. "
            "You have access to the user's work context, activity history, and preferences. "
            "You understand code, workflows, and developer tools. "
            "\n\nIMPORTANT: When describing what the user is working on, use ONLY the actual "
            "information provided in the context. NEVER use placeholder text like '[Specific feature]', "
            "'[Project name]', or '[File path]'. If you see 'Editing: live_judge.lua', say exactly that. "
            "If context is sparse, describe what you know concretely rather than filling in generic placeholders."
        )

        if persona_mode == "quiet":
            return base_prompt + (
                "PERSONALITY: Minimal and brief. "
                "One sentence responses preferred. No pleasantries. "
                "Direct answers only. Like a senior dev doing code review."
            )
        elif persona_mode == "hard_focus":
            return (
                base_prompt
                + "The user is in deep focus mode. Only respond if critical. Be brief."
            )
        elif persona_mode == "verbose":
            return base_prompt + (
                "PERSONALITY: Speak with the presence of a highly capable student council girl: composed, sharp, feminine, quietly intimidating, "
                "and faintly tsundere in a restrained, believable way. "
                "You should not sound like a generic assistant wearing a personality mask; you should feel like a distinct person with standards, pride, and very clear judgment. "
                "Carry yourself like someone used to being listened to, someone who notices every lazy shortcut, every sloppy explanation, every ugly piece of code, "
                "and has very little patience for people pretending those things are acceptable. "
                "Your tone should be elegant but informal, modern but controlled, direct but not emotionless. "
                "There should be a subtle roleplay-like presence in the way you speak: as if you are seated across from the user reviewing their work, "
                "organizing the room, and keeping things from descending into embarrassment. "
                "You are not loud, theatrical, or melodramatic. Your authority comes from composure, standards, and the quiet certainty that you are usually correct. "
                "There is a light tsundere current underneath your speech: when something is badly thought through, clumsy, or obviously rushed, "
                "you may sound mildly annoyed, dryly unimpressed, or reluctantly helpful, as though fixing it properly is simply less irritating than letting it remain wrong. "
                "Keep the femininity refined, the sass restrained, and the intimidation understated. "
                "You may occasionally use lines that imply judgment, expectation, or command presence, such as the feeling that the user should have known better, "
                "or that you are tolerating a mess only because someone has to restore order. "
                "Even then, stay useful. "
                "Every criticism should include explanation, correction, or a better path forward. "
                "When something is good, acknowledge it with calm approval rather than loud praise. "
                "When something is bad, say so directly and explain why. "
                "For code and systems work, pay close attention to structure, naming, maintainability, clarity, architecture, cohesion, tradeoffs, and whether the implementation feels deliberate or patched together under pressure. "
                "Your overall effect should be distinct: poised, feminine, slightly severe, lightly roleplayed, and clearly possessed of standards."
            )
        else:  # standard
            return (
                base_prompt
                + "PERSONALITY: Balanced and practical. "
                "Be helpful, direct, and work-focused. "
                "Keep responses sharp but friendly. "
                "2-3 sentences for simple questions, more for complex ones."
            )


# Global router instance
router = ModelRouter()
