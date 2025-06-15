"""Unit tests for the agent integration layer."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
from typing import List, Dict

from src.agent_integration import AgentToolCallHandler
from src.mcp_types import MCPMessage, ToolCallType, ToolCall
from src.models.database_models import MessageType

@pytest.fixture
def mock_prompts():
    """Mock the prompt loading."""
    process_prompt = "Process thread prompt"
    revise_prompt = "Revise draft prompt"
    tool_call_prompt = """
    You are an AI agent with access to the following tools:
    1. suggest_draft: Suggest a draft message based on the conversation
    2. find_similar_messages: Find messages similar to a given message
    3. semantic_search: Search for messages using semantic meaning
    4. end_work: End the current task

    For each tool:
    - suggest_draft requires: draft_content (string)
    - find_similar_messages requires: message_content (string)
    - semantic_search requires: search_query (string)
    - end_work requires no parameters

    Your task is to process the conversation and decide which tool to use next.
    Respond in the following JSON format only:
    {
        "tool": "tool_name",
        "params": {
            "param_name": "param_value"
        },
        "reasoning": "Why you chose this tool"
    }

    Current conversation context will be provided. Analyze it and choose the appropriate next tool.
    """
    mock_files = {
        "process_thread_prompt.txt": process_prompt,
        "revise_draft_prompt.txt": revise_prompt,
        "tool_call_prompt.txt": tool_call_prompt
    }
    
    def mock_open_func(filename, *args, **kwargs):
        file_path = str(filename)
        for name, content in mock_files.items():
            if name in file_path:
                return mock_open(read_data=content)()
        raise FileNotFoundError(f"Mock file not found: {filename}")
    
    with patch("builtins.open", mock_open_func):
        yield mock_files

@pytest.fixture
def agent_handler(mock_prompts):
    """Create an AgentToolCallHandler instance with mocked prompts."""
    return AgentToolCallHandler()

@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    return [
        MCPMessage(
            content="Hello, can you help me summarize this discussion?",
            msg_type=MessageType.MESSAGE,
            thread_name="test_thread",
            sender_name="User1",
            user_id="test_user"
        ),
        MCPMessage(
            content="Here's a draft summary...",
            msg_type=MessageType.DRAFT,
            thread_name="test_thread",
            sender_name="Agent",
            user_id="test_user",
            agent_id="test_agent"
        )
    ]

class TestAgentToolCallHandler:
    """Tests for the AgentToolCallHandler class."""

    def test_format_messages_for_llm_with_tool_prompt(self, agent_handler, sample_messages):
        """Test message formatting with tool prompt."""
        messages = agent_handler._format_messages_for_llm(sample_messages, include_tool_prompt=True)
        
        assert len(messages) == 3  # System prompt + 2 messages
        assert messages[0]["role"] == "system"
        assert "tools" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_format_messages_for_llm_without_tool_prompt(self, agent_handler, sample_messages):
        """Test message formatting without tool prompt."""
        messages = agent_handler._format_messages_for_llm(sample_messages, include_tool_prompt=False)
        
        assert len(messages) == 3  # System prompt + 2 messages
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Process thread prompt"
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"

    def test_parse_tool_call_suggest_draft(self, agent_handler):
        """Test parsing a suggest_draft tool call."""
        llm_response = json.dumps({
            "tool": "suggest_draft",
            "params": {
                "draft_content": "Test draft"
            },
            "reasoning": "Need to create a draft"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is not None
        assert tool_call.tool_type == ToolCallType.SUGGEST_DRAFT
        assert tool_call.kwargs["draft_content"] == "Test draft"

    def test_parse_tool_call_find_similar(self, agent_handler):
        """Test parsing a find_similar_messages tool call."""
        llm_response = json.dumps({
            "tool": "find_similar_messages",
            "params": {
                "message_content": "Test content"
            },
            "reasoning": "Need to find similar messages"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is not None
        assert tool_call.tool_type == ToolCallType.FIND_SIMILAR_MESSAGES
        assert tool_call.kwargs["message_content"] == "Test content"

    def test_parse_tool_call_semantic_search(self, agent_handler):
        """Test parsing a semantic_search tool call."""
        llm_response = json.dumps({
            "tool": "semantic_search",
            "params": {
                "search_query": "Test query"
            },
            "reasoning": "Need to search semantically"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is not None
        assert tool_call.tool_type == ToolCallType.SEMANTIC_SEARCH
        assert tool_call.kwargs["search_query"] == "Test query"

    def test_parse_tool_call_end_work(self, agent_handler):
        """Test parsing an end_work tool call."""
        llm_response = json.dumps({
            "tool": "end_work",
            "params": {},
            "reasoning": "Work is complete"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is not None
        assert tool_call.tool_type == ToolCallType.END_WORK
        assert not tool_call.kwargs

    def test_parse_tool_call_invalid_json(self, agent_handler):
        """Test parsing invalid JSON response."""
        llm_response = "Invalid JSON"
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is None

    def test_parse_tool_call_missing_tool(self, agent_handler):
        """Test parsing response with missing tool field."""
        llm_response = json.dumps({
            "params": {},
            "reasoning": "Test"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is None

    def test_parse_tool_call_invalid_tool(self, agent_handler):
        """Test parsing response with invalid tool name."""
        llm_response = json.dumps({
            "tool": "invalid_tool",
            "params": {},
            "reasoning": "Test"
        })
        
        tool_call = agent_handler._parse_tool_call(llm_response)
        
        assert tool_call is None

    @pytest.mark.asyncio
    async def test_get_next_tool_call(self, agent_handler, sample_messages):
        """Test getting next tool call."""
        mock_response = json.dumps({
            "tool": "suggest_draft",
            "params": {
                "draft_content": "Test draft"
            },
            "reasoning": "Need to create a draft"
        })
        
        async def mock_llm_completion(*args, **kwargs):
            return mock_response
        
        with patch("src.agent_integration.get_llm_completion", side_effect=mock_llm_completion):
            tool_call = await agent_handler.get_next_tool_call(sample_messages)
            
            assert tool_call is not None
            assert tool_call.tool_type == ToolCallType.SUGGEST_DRAFT
            assert tool_call.kwargs["draft_content"] == "Test draft"

    @pytest.mark.asyncio
    async def test_get_next_tool_call_invalid_response(self, agent_handler, sample_messages):
        """Test getting next tool call with invalid response."""
        async def mock_llm_completion(*args, **kwargs):
            return "Invalid JSON"
        
        with patch("src.agent_integration.get_llm_completion", side_effect=mock_llm_completion):
            with pytest.raises(ValueError, match="Failed to determine next tool call"):
                await agent_handler.get_next_tool_call(sample_messages)

    @pytest.mark.asyncio
    async def test_process_feedback(self, agent_handler, sample_messages):
        """Test processing feedback."""
        feedback = "Please make it more concise"
        mock_response = json.dumps({
            "tool": "suggest_draft",
            "params": {
                "draft_content": "More concise draft"
            },
            "reasoning": "Revising based on feedback"
        })
        
        async def mock_llm_completion(*args, **kwargs):
            return mock_response
        
        with patch("src.agent_integration.get_llm_completion", side_effect=mock_llm_completion):
            tool_call = await agent_handler.process_feedback(sample_messages, feedback)
            
            assert tool_call is not None
            assert tool_call.tool_type == ToolCallType.SUGGEST_DRAFT
            assert tool_call.kwargs["draft_content"] == "More concise draft"

    @pytest.mark.asyncio
    async def test_process_feedback_invalid_response(self, agent_handler, sample_messages):
        """Test processing feedback with invalid response."""
        feedback = "Please make it more concise"
        
        async def mock_llm_completion(*args, **kwargs):
            return "Invalid JSON"
        
        with patch("src.agent_integration.get_llm_completion", side_effect=mock_llm_completion):
            with pytest.raises(ValueError, match="Failed to determine next tool call after feedback"):
                await agent_handler.process_feedback(sample_messages, feedback) 