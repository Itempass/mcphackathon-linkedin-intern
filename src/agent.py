"""
AI-powered MCP Agent using FastMCP for dynamic tool discovery and LLM for intelligent decision-making.

This agent combines:
- FastMCP for dynamic MCP server connection and tool discovery
- LLM integration for intelligent tool selection and reasoning
- Simple conversation loop for multi-step problem solving
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
try:
    from fastmcp import Client
    from fastmcp.exceptions import ClientError
except ImportError:
    # For testing without FastMCP
    Client = object
    class ClientError(Exception):
        pass

# OpenRouter integration using modern OpenAI client
from openai import OpenAI


load_dotenv(override=True)
logger = logging.getLogger(__name__)

class GenericMCPAgent:
    """
    AI-powered MCP Agent that uses an LLM to intelligently decide which tools to call.
    
    Features:
    - Dynamic MCP tool discovery via FastMCP
    - LLM-driven decision making
    - Multi-step reasoning and tool execution
    - Automatic user context injection
    """
    
    def __init__(self, server_url: str, user_id: str, agent_id: str, openrouter_api_key: Optional[str] = None):
        """
        Initialize the AI-powered MCP agent.
        
        Args:
            server_url: MCP server URL
            user_id: User ID for context
            agent_id: Agent ID for tracking
            openrouter_api_key: OpenRouter API key (optional, uses env var if not provided)
        """
        self.server_url = server_url
        self.user_id = user_id
        self.agent_id = agent_id
        self.client: Optional[Client] = None
        self.tools: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize OpenRouter client
        api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if api_key:
            logger.info(f"Initializing OpenRouter client with API key: {api_key[:10]}...")
            self.llm_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            self.has_llm = True
        else:
            self.has_llm = False
            logger.warning("No OpenRouter API key - agent will run in basic mode")
    
    async def __aenter__(self):
        """Connect to MCP server and discover tools."""
        try:
            self.client = Client(self.server_url)
            await self.client.__aenter__()
            
            # Discover available tools
            tools_raw = await self.client.list_tools()
            # Convert Tool objects to dictionaries
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": tool.inputSchema or {}
                }
                for tool in tools_raw
            ]
            
            logger.info(f"Connected to MCP server: {len(self.tools)} tools, 0 resources, 0 prompts")
            return self
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MCP server: {e}")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up connection."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            self.client = None
    
    def describe_capabilities(self) -> Dict[str, Any]:
        """Describe agent capabilities for external inspection."""
        return {
            "tools": [{"name": tool["name"], "description": tool["description"]} for tool in self.tools],
            "resources": [],  # FastMCP doesn't expose resources in our simple setup
            "prompts": []     # FastMCP doesn't expose prompts in our simple setup
        }
    
    @property
    def tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return [tool["name"] for tool in self.tools]
    
    async def execute_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute a specific tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Formatted result string
        """
        if not self.client:
            raise RuntimeError("Agent not connected - use async context manager")
            
        # Add user_id explicitly since FastMCP exclude_args isn't working with standard MCP client
        args = dict(arguments or {})
        args["user_id"] = self.user_id
        
        try:
            result = await self.client.call_tool(tool_name, args)
            
            # FastMCP returns a list of TextContent objects
            if result and hasattr(result[0], 'text'):
                content = result[0].text
                return f"✓ {tool_name}: {content}"
            else:
                return f"✓ {tool_name}: {result}"
                
        except ClientError as e:
            error_msg = f"✗ {tool_name}: Error calling tool '{tool_name}': {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"✗ {tool_name}: Unexpected error: {e}"
            logger.error(error_msg)
            return error_msg
    
    def _format_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Formats the discovered MCP tools and adds internal tools for the LLM.
        """
        # Start with MCP tools from the server
        formatted_tools = []
        for tool in self.tools:
            if "name" in tool and "description" in tool and "inputSchema" in tool:
                formatted_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool.get("inputSchema", {}),
                        },
                    }
                )
        
        # Add our internal 'task_completed' tool
        formatted_tools.append(
            {
                "type": "function",
                "function": {
                    "name": "task_completed",
                    "description": "Call this tool to signal that you have successfully completed the user's request. Provide a final summary of the work you did.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "A concise summary of the results and work performed."
                            }
                        },
                        "required": ["summary"],
                    },
                },
            }
        )
        
        # Add our internal 'suggest_draft' tool
        formatted_tools.append(
            {
                "type": "function",
                "function": {
                    "name": "suggest_draft",
                    "description": "Call this tool to suggest a draft response. This will end the agent's work.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "draft_content": {
                                "type": "string",
                                "description": "The content of the draft to be suggested."
                            }
                        },
                        "required": ["draft_content"],
                    },
                },
            }
        )
        return formatted_tools
    
    async def _get_llm_decision(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get decision from LLM about what to do next."""
        if not self.has_llm:
            # Fallback to simple heuristic
            return {"action": "call_tool", "tool": self.tools[0]["name"], "arguments": {}}
        
        # Get tools in the OpenAI-compatible format
        llm_tools = self._format_tools_for_llm()
        
        try:
            response = self.llm_client.chat.completions.create(
                model="anthropic/claude-3.7-sonnet:thinking",
                messages=messages,
                tools=llm_tools,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if tool_name == "task_completed":
                    return {
                        "action": "complete",
                        "summary": arguments.get("summary", "Task completed.")
                    }
                elif tool_name == "suggest_draft":
                    return {
                        "action": "suggest_draft",
                        "draft": arguments.get("draft_content", "")
                    }
                else:
                    return {
                        "action": "call_tool",
                        "tool": tool_name,
                        "arguments": arguments
                    }
            else:
                # If the model responds without a tool call, we'll treat it as a final summary.
                return {
                    "action": "complete",
                    "summary": response_message.content
                }
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {"action": "call_tool", "tool": self.tools[0]["name"], "arguments": {}}
    
    async def run_intelligent_agent(self, messages: List[Dict[str, Any]], max_iterations: int = 15) -> List[Dict[str, Any]]:
        """
        Run the AI agent with intelligent decision-making.
        
        Args:
            messages: The conversation history to start the agent with.
            max_iterations: Maximum number of tool calls to make
            
        Returns:
            The final conversation history (list of message dicts)
        """
        if not self.tools:
            return messages
        
        if not messages:
            raise ValueError("The 'messages' list cannot be empty.")
            
        logger.info(f"Starting intelligent exploration with {len(self.tools)} available tools")
        
        # The conversation is now passed in directly.
        # We make a copy to avoid modifying the caller's list.
        current_messages = list(messages)
        
        for iteration in range(max_iterations):
            try:
                # Get LLM decision
                decision = await self._get_llm_decision(current_messages)
                
                if decision.get("action") == "complete":
                    summary = decision.get('summary', 'No summary provided.')
                    logger.info(f"Agent completed task with summary: {summary}")
                    break
                
                elif decision.get("action") == "suggest_draft":
                    draft = decision.get('draft', 'No draft content.')
                    logger.info(f"Agent suggested a draft: {draft}")
                    
                    # Add the final draft suggestion to the history before breaking
                    current_messages.append({
                        "role": "assistant",
                        "content": "I have a draft ready.",
                        "tool_calls": [{
                            "id": "call_suggest_draft",
                            "type": "function",
                            "function": {
                                "name": "suggest_draft",
                                "arguments": json.dumps({"draft_content": draft})
                            }
                        }]
                    })
                    break
                
                elif decision.get("action") == "call_tool":
                    tool_name = decision.get("tool")
                    tool_args = decision.get("arguments", {})
                    
                    if tool_name in self.tool_names:
                        # Add assistant's thought process to history
                        current_messages.append({
                            "role": "assistant",
                            "content": f"I should call the tool `{tool_name}` with arguments `{json.dumps(tool_args)}`.",
                            "tool_calls": [{
                                "id": f"call_{tool_name}",
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": json.dumps(tool_args)
                                }
                            }]
                        })
                        
                        # Execute the tool
                        result = await self.execute_tool(tool_name, tool_args)
                        
                        # Add tool execution result to history for the next turn
                        current_messages.append({
                            "role": "tool",
                            "tool_call_id": f"call_{tool_name}",
                            "name": tool_name,
                            "content": result,
                        })
                        
                    else:
                        logger.error(f"LLM tried to call an unknown tool: {tool_name}")
                        # Add error message to history
                        current_messages.append({
                            "role": "user",
                            "content": f"Error: You tried to call a tool named '{tool_name}' which does not exist."
                        })
                
                else:
                    logger.error(f"LLM returned an unknown action: {decision.get('action')}")
                    break
                    
            except Exception as e:
                logger.error(f"Agent loop failed: {e}")
                break
        
        logger.info(f"Intelligent exploration completed")
        return current_messages


# Convenience function for simple usage
async def run_intelligent_agent(
    server_url_or_path: str,
    user_id: str,
    agent_id: str,
    messages: List[Dict[str, Any]],
    max_iterations: int = 5,
    openrouter_api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Run an intelligent MCP agent with AI decision-making.
    
    Args:
        server_url_or_path: MCP server URL or path
        user_id: User ID for context
        agent_id: Agent ID for tracking  
        messages: The conversation history to start the agent with.
        max_iterations: Maximum number of tool calls
        openrouter_api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var)
        
    Returns:
        The final conversation history (list of message dicts)
    """
    async with GenericMCPAgent(server_url_or_path, user_id, agent_id, openrouter_api_key) as agent:
        return await agent.run_intelligent_agent(messages, max_iterations)


# Example usage
async def main():
    """Example of how to use the Generic MCP Agent."""
    
    # Example messages - this works with ANY MCP server
    messages = [
        {"role": "user", "content": "I need help with the 'example_thread'. Please check the 'messages' table and look for 'important information'."}
    ]
    
    # Run the agent - it will intelligently explore whatever tools are available
    final_conversation = await run_intelligent_agent(
        server_url_or_path="http://localhost:8000/mcp", 
        user_id="user123",
        agent_id="agent456", 
        messages=messages,
        max_iterations=3
    )
    
    print("\n--- Final Conversation ---")
    print(json.dumps(final_conversation, indent=2))


if __name__ == "__main__":
    asyncio.run(main()) 