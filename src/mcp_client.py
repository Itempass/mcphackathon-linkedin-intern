"""
MCP Client Wrapper for interacting with MCP servers.
Provides a high-level interface for making tool calls to MCP servers with proper
error handling and connection management.
"""

import os
from typing import Any, Dict, Optional, List, Union, AsyncGenerator, Tuple
import logging
from contextlib import asynccontextmanager
import uuid
import asyncio

try:
    from fastmcp import Client
    from fastmcp.exceptions import ClientError
except ImportError:
    # For testing purposes
    Client = object
    class ClientError(Exception):
        pass

from .types import MCPMessage, ToolCall, ToolCallType
from src.models.database_models import MessageType
from .agent_integration import AgentToolCallHandler

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass

class MCPConnectionError(MCPError):
    """Raised when there are connection issues with the MCP server."""
    pass

class MCPToolError(MCPError):
    """Raised when an MCP tool call fails."""
    pass

class MCPClientWrapper:
    """
    Wrapper around FastMCP client providing high-level interface for MCP tool calls.
    
    Handles:
    - Connection management through async context manager
    - Error handling and logging
    - Tool call response parsing
    - User and agent context management
    - Message type handling
    - Looping tool calls as shown in sequence diagrams
    """
    
    def __init__(self, base_url: str, user_id: str):
        """
        Initialize the MCP client wrapper.
        
        Args:
            base_url: Base URL of the MCP server (without /mcp suffix)
            user_id: ID of the user making the requests
        """
        if not base_url:
            raise ValueError("base_url is required")
        if not user_id:
            raise ValueError("user_id is required")
            
        self.base_url = base_url
        self.user_id = user_id
        self._client: Optional[Client] = None
        self._current_agent_id: Optional[str] = None
        self._message_cache: Dict[str, List[MCPMessage]] = {}
        self._agent_handler = AgentToolCallHandler()
        
    @property
    def client(self) -> Client:
        """Get the underlying FastMCP client, raising error if not initialized."""
        if self._client is None:
            raise MCPConnectionError("MCP client not initialized - use async context manager")
        return self._client

    @property
    def agent_id(self) -> Optional[str]:
        """Get current agent ID if set."""
        return self._current_agent_id

    def set_agent_context(self, agent_id: Optional[str] = None):
        """Set the current agent context."""
        self._current_agent_id = agent_id or str(uuid.uuid4())
        
    async def __aenter__(self) -> 'MCPClientWrapper':
        """Initialize connection when entering async context."""
        try:
            self._client = Client(f"{self.base_url}/mcp")
            await self._client.__aenter__()
            logger.debug("Successfully connected to MCP server at %s", self.base_url)
            return self
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}") from e
            
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up connection when exiting async context."""
        if self._client is not None:
            try:
                await self._client.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                logger.error("Error closing MCP connection: %s", e)
            finally:
                self._client = None
                self._current_agent_id = None
                self._message_cache.clear()

    def _cache_messages(self, thread_name: str, messages: List[MCPMessage]):
        """Cache messages for a thread to detect changes."""
        self._message_cache[thread_name] = messages.copy()

    def _has_new_messages(self, thread_name: str, current_messages: List[MCPMessage]) -> bool:
        """Check if there are new messages compared to cached messages."""
        if thread_name not in self._message_cache:
            return True
        cached = {msg.content for msg in self._message_cache[thread_name]}
        current = {msg.content for msg in current_messages}
        return len(current - cached) > 0

    async def process_agent_tool_calls(
        self,
        thread_name: str,
        messages: List[MCPMessage]
    ) -> AsyncGenerator[Tuple[ToolCallType, Any], None]:
        """
        Process tool calls from the agent in a loop as shown in sequence diagrams.
        
        Args:
            thread_name: Name of the thread being processed
            messages: List of messages to process
            
        Yields:
            Tuple of (tool_type, result) for each tool call
        """
        self._cache_messages(thread_name, messages)
        
        while True:
            # Get next tool call from agent
            tool_call = await self.get_next_tool_call(messages)
            
            if tool_call.tool_type == ToolCallType.END_WORK:
                break
                
            elif tool_call.tool_type == ToolCallType.SUGGEST_DRAFT:
                # Check for new messages before storing draft
                current_messages = await self.get_thread_messages(thread_name)
                if self._has_new_messages(thread_name, current_messages):
                    logger.info("New messages found, discarding draft")
                    continue
                    
                # Store draft and update cache
                draft_result = await self.store_draft(
                    thread_name=thread_name,
                    content=tool_call.kwargs["draft_content"]
                )
                self._cache_messages(thread_name, current_messages)
                yield tool_call.tool_type, draft_result
                
            elif tool_call.tool_type == ToolCallType.FIND_SIMILAR_MESSAGES:
                similar = await self.find_similar_messages(
                    message_content=tool_call.kwargs["message_content"],
                    thread_name=thread_name
                )
                yield tool_call.tool_type, similar
                
            elif tool_call.tool_type == ToolCallType.SEMANTIC_SEARCH:
                results = await self.semantic_search(
                    search_query=tool_call.kwargs["search_query"],
                    thread_name=thread_name
                )
                yield tool_call.tool_type, results

    async def get_next_tool_call(self, messages: List[MCPMessage]) -> ToolCall:
        """Get next tool call from agent based on messages."""
        return await self._agent_handler.get_next_tool_call(messages)

    async def process_feedback(self, messages: List[MCPMessage], feedback: str) -> ToolCall:
        """Process feedback and get next tool call."""
        return await self._agent_handler.process_feedback(messages, feedback)

    async def store_draft(self, thread_name: str, content: str) -> MCPMessage:
        """Store a draft message."""
        draft = MCPMessage(
            content=content,
            msg_type=MessageType.DRAFT,
            thread_name=thread_name,
            sender_name="Agent",
            user_id=self.user_id,
            agent_id=self.agent_id
        )
        # Call appropriate MCP tool to store draft
        await self.call_tool("store_draft", draft.to_dict())
        return draft

    async def get_thread_messages(self, thread_name: str) -> List[MCPMessage]:
        """Get all messages for a thread."""
        results = await self.call_tool(
            "get_thread_messages",
            {"thread_name": thread_name}
        )
        return [MCPMessage.from_dict(msg) for msg in results]
                
    async def call_tool(
        self,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        include_user_context: bool = True
    ) -> Any:
        """
        Make a tool call to the MCP server with error handling.
        
        Args:
            tool_name: Name of the MCP tool to call
            tool_args: Optional arguments for the tool call
            include_user_context: Whether to include user_id in tool args
            
        Returns:
            Parsed response from the tool call
            
        Raises:
            MCPToolError: If the tool call fails
            MCPConnectionError: If there are connection issues
        """
        try:
            args = dict(tool_args or {})
            
            # Include user context if requested
            if include_user_context:
                args["user_id"] = self.user_id
                
            # Include agent context if available
            if self._current_agent_id:
                args["agent_id"] = self._current_agent_id
            
            response = await self.client.call_tool(tool_name, args)
            
            if not response:
                raise MCPToolError(f"Empty response from tool {tool_name}")
                
            # FastMCP returns responses as a list where first item contains the text
            result = response[0].text if response else None
            
            try:
                # Tool responses are typically eval-able Python literals
                return eval(result) if result else None
            except Exception as e:
                logger.warning("Failed to parse tool response as Python literal: %s", e)
                return result
                
        except ClientError as e:
            raise MCPToolError(f"Tool {tool_name} failed: {e}") from e
        except Exception as e:
            raise MCPConnectionError(f"Connection error during tool call: {e}") from e

    async def find_similar_messages(
        self,
        message_content: str,
        thread_name: Optional[str] = None
    ) -> List[MCPMessage]:
        """Find similar messages using MCP search."""
        args = {
            "message_content": message_content
        }
        if thread_name:
            args["thread_name"] = thread_name
            
        results = await self.call_tool("find_similar_messages", args)
        return [MCPMessage.from_dict(msg) for msg in results]

    async def semantic_search(
        self,
        search_query: str,
        thread_name: Optional[str] = None
    ) -> List[MCPMessage]:
        """Perform semantic search using MCP."""
        args = {
            "search_query": search_query
        }
        if thread_name:
            args["thread_name"] = thread_name
            
        results = await self.call_tool("semantic_search", args)
        return [MCPMessage.from_dict(msg) for msg in results]
            
    @asynccontextmanager
    async def connection(self):
        """Context manager for handling MCP connections."""
        async with self:
            yield self 