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
from typing import Dict, List, Any, Optional, Tuple, Union
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
    
    def __init__(self, clients: List[Client], user_id: str, agent_id: str, openrouter_api_key: Optional[str] = None):
        """
        Initialize the AI-powered MCP agent.
        
        Args:
            clients: A list of pre-initialized FastMCP Client objects.
            user_id: User ID for context
            agent_id: Agent ID for tracking
            openrouter_api_key: OpenRouter API key (optional, uses env var if not provided)
        """
        self.clients = clients
        self.user_id = user_id
        self.agent_id = agent_id
        self.tools: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize OpenRouter client
        api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if api_key:
            self.llm_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            self.has_llm = True
        else:
            self.has_llm = False
            logger.warning("No OpenRouter API key - agent will run in basic mode")
    
    async def discover_tools(self):
        """Connect temporarily to discover tools from all clients."""
        all_tools = []
        for client in self.clients:
            try:
                # Use a short-lived connection for discovery
                async with client:
                    tools_raw = await client.list_tools()
                    
                    # Get current tool names to check for duplicates
                    current_tool_names = [t["name"] for t in all_tools]

                    # Convert Tool objects to dictionaries and store with client
                    for tool in tools_raw:
                        if tool.name in current_tool_names:
                            logger.warning(f"Duplicate tool name '{tool.name}' found. The first one discovered will be used.")
                            continue # Skip duplicate
                        
                        all_tools.append({
                            "name": tool.name,
                            "description": tool.description or "",
                            "inputSchema": tool.inputSchema or {},
                            "client": client  # Associate tool with its client
                        })
            except Exception as e:
                logger.error(f"Failed to discover tools for client {client.server_url}: {e}")

        self.tools = all_tools
        logger.info(f"Tool discovery complete: {len(self.tools)} tools found across {len(self.clients)} clients.")

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
        if not self.clients:
            raise RuntimeError("Agent not connected - use async context manager")
            
        # Find the tool and its associated client
        tool_to_execute = None
        for tool in self.tools:
            if tool["name"] == tool_name:
                tool_to_execute = tool
                break
        
        if not tool_to_execute:
            error_msg = f"✗ {tool_name}: Error - tool not found."
            logger.error(error_msg)
            return error_msg

        client = tool_to_execute["client"]

        # Add user_id explicitly since FastMCP exclude_args isn't working with standard MCP client
        args = dict(arguments or {})
        args["user_id"] = self.user_id
        
        try:
            # Use a short-lived connection for the actual tool call
            async with client:
                result = await client.call_tool(tool_name, args)
            
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
            error_msg = f"✗ {tool_name}: Unexpected error during tool call '{tool_name}': {e}"
            logger.error(error_msg, exc_info=True)
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
        
        # Prepare the conversation for the LLM
        llm_messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        llm_messages.extend(messages)
        
        logger.info(f"🤖 Getting LLM decision with {len(llm_messages)} messages and {len(self.tools)} tools...")
        
        # Get response from OpenRouter
        response = self.llm_client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.7-sonnet:thinking"),
            messages=llm_messages,
            tools=self._format_tools_for_llm(),
            tool_choice="auto",
        )
        
        return response.choices[0].message
    
    async def run_intelligent_agent(self, messages: List[Dict[str, Any]], max_iterations: int = 15) -> List[Dict[str, Any]]:
        """
        The main loop for the agent to process a conversation.
        """
        self.conversation_history = list(messages)
        
        for i in range(max_iterations):
            logger.info(f"--- Agent Iteration {i+1}/{max_iterations} ---")
            
            # Get LLM decision
            assistant_response = await self._get_llm_decision(self.conversation_history)
            
            # If the model wants to call a tool
            if assistant_response.tool_calls:
                # Add the assistant's response to history as a dictionary
                self.conversation_history.append(assistant_response.model_dump())
                
                # Execute all tool calls
                for tool_call in assistant_response.tool_calls:
                    tool_name = tool_call.function.name
                    
                    # Handle our internal 'task_completed' tool
                    if tool_name == "task_completed":
                        logger.info("✅ Agent signaled task completion.")
                        return self.conversation_history
                    # Handle our internal 'suggest_draft' tool
                    if tool_name == "suggest_draft":
                        logger.info("✅ Agent suggested a draft. Ending execution.")
                        return self.conversation_history
                        
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                        logger.info(f"Tool call: {tool_name}({arguments})")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode arguments for tool {tool_name}: {tool_call.function.arguments}")
                        tool_result = f"Error: Invalid JSON arguments for {tool_name}"
                        arguments = {} # Set empty dict to avoid breaking downstream
                    
                    # Execute the tool and get the result
                    tool_result = await self.execute_tool(tool_name, arguments)
                    
                    # Add the tool result to the conversation history
                    self.conversation_history.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result,
                        }
                    )
            
            # If the model returns a regular message, it's the final answer
            else:
                logger.info("🤖 LLM provided a final answer.")
                # Add the assistant's response to history as a dictionary
                self.conversation_history.append(assistant_response.model_dump())
                return self.conversation_history

        logger.warning("Agent reached max iterations. Returning conversation history.")
        return self.conversation_history


async def run_intelligent_agent(
    mcp_clients: List[Client],
    user_id: str,
    agent_id: str,
    messages: List[Dict[str, Any]],
    max_iterations: int = 5,
    openrouter_api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    High-level function to create, setup, and run the intelligent agent.

    Args:
        mcp_clients: A list of pre-initialized FastMCP Client objects.
        user_id: The user's ID.
        agent_id: The agent's ID for this run.
        messages: The initial conversation messages.
        max_iterations: The maximum number of LLM <-> tool loops.
        openrouter_api_key: The OpenRouter API key.
        
    Returns:
        The complete conversation history.
    """
    agent = GenericMCPAgent(mcp_clients, user_id, agent_id, openrouter_api_key)
    
    # Discover tools using short-lived connections
    await agent.discover_tools()
    
    # Run the main agent loop
    conversation_history = await agent.run_intelligent_agent(messages, max_iterations)
    
    return conversation_history


# Example usage
async def main():
    """Example of how to use the Generic MCP Agent."""
    
    # Example messages - this works with ANY MCP server
    messages = [
        {"role": "user", "content": "I need help with the 'example_thread'. Please check the 'messages' table and look for 'important information'."}
    ]
    
    # Run the agent - it will intelligently explore whatever tools are available
    final_conversation = await run_intelligent_agent(
        mcp_clients=[Client("http://localhost:8001/db-mcp")], 
        user_id="user123",
        agent_id="agent456", 
        messages=messages,
        max_iterations=3
    )
    
    print("\n--- Final Conversation ---")
    print(json.dumps(final_conversation, indent=2))


if __name__ == "__main__":
    asyncio.run(main()) 