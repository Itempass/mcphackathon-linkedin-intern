"""
Agent integration layer for handling tool calls and prompts.
This module bridges between the LLM and the MCP client.
"""

import os
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from .mcp_types import MCPMessage, ToolCall, ToolCallType
from .llm_client import get_llm_completion

class AgentToolCallHandler:
    """Handles tool calls from the agent."""

    def __init__(self):
        """Initialize the handler."""
        self.TOOL_CALL_PROMPT = self._load_prompt("tool_call_prompt.txt")
        self.process_thread_prompt = self._load_prompt("process_thread_prompt.txt")
        self.revise_draft_prompt = self._load_prompt("revise_draft_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt from a file."""
        prompt_dir = Path(__file__).parent / "prompts"
        with open(prompt_dir / filename) as f:
            return f.read()

    def _format_messages_for_llm(
        self,
        messages: List[MCPMessage],
        include_tool_prompt: bool = True
    ) -> List[Dict[str, str]]:
        """Format messages for the LLM."""
        llm_messages = []

        # Add appropriate system prompt
        if include_tool_prompt:
            llm_messages.append({
                "role": "system",
                "content": self.TOOL_CALL_PROMPT
            })
        else:
            llm_messages.append({
                "role": "system",
                "content": self.process_thread_prompt
            })

        # Add conversation messages
        for msg in messages:
            llm_messages.append({
                "role": "user" if msg.sender_name != "Agent" else "assistant",
                "content": msg.content  # Fixed: using content instead of msg_content
            })

        return llm_messages

    def _parse_tool_call(self, llm_response: str) -> Optional[ToolCall]:
        """Parse the LLM response into a tool call."""
        try:
            response_data = json.loads(llm_response)
            tool_name = response_data.get("tool")
            if not tool_name:
                return None

            try:
                tool_type = ToolCallType(tool_name)
            except ValueError:
                return None

            return ToolCall(
                tool_type=tool_type,
                **response_data.get("params", {})
            )
        except json.JSONDecodeError:
            return None

    async def get_next_tool_call(self, messages: List[MCPMessage]) -> ToolCall:
        """Get the next tool call from the agent."""
        llm_messages = self._format_messages_for_llm(messages)
        response = await get_llm_completion(llm_messages)
        tool_call = self._parse_tool_call(response)

        if not tool_call:
            raise ValueError("Failed to determine next tool call")

        return tool_call

    async def process_feedback(
        self,
        messages: List[MCPMessage],
        feedback: str
    ) -> ToolCall:
        """Process feedback and get the next tool call."""
        # Format messages with tool prompt
        llm_messages = self._format_messages_for_llm(messages, include_tool_prompt=True)

        # Add feedback message
        llm_messages.append({
            "role": "user",
            "content": f"FEEDBACK: {feedback}"
        })

        # Get next tool call
        response = await get_llm_completion(llm_messages)
        tool_call = self._parse_tool_call(response)

        if not tool_call:
            raise ValueError("Failed to determine next tool call after feedback")

        return tool_call 