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
from fastmcp import Client
from fastmcp.exceptions import ClientError

# OpenRouter integration using modern OpenAI client
from openai import OpenAI


load_dotenv(override=True)
logger = logging.getLogger(__name__)

class GenericMCPAgent:
    """
    AI-powered MCP Agent that uses an LLM to intelligently decide which tools to call.
    
    Features:
    - Uses a shared, persistent connection to MCP servers
    - LLM-driven decision making
    - Multi-step reasoning and tool execution
    - Automatic user context injection
    """
    
    def __init__(self, clients: Dict[str, Client], user_id: str, agent_id: str, openrouter_api_key: Optional[str] = None):
        """
        Initialize the AI-powered MCP agent with existing client connections.
        
        Args:
            clients: A dictionary of pre-connected FastMCP.Client objects
            user_id: User ID for context
            agent_id: Agent ID for tracking
            openrouter_api_key: OpenRouter API key (optional, uses env var if not provided)
        """
        self.user_id = user_id
        self.agent_id = agent_id
        self.clients = list(clients.values())
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
        """
        Discovers available tools from the connected MCP clients.
        This should be called after the agent is initialized.
        """
        for client in self.clients:
            try:
                tools_raw = await client.list_tools()
                
                # Get current tool names to check for duplicates
                current_tool_names = self.tool_names

                # Convert Tool objects to dictionaries and store with client
                for tool in tools_raw:
                    if tool.name in current_tool_names:
                        logger.warning(f"Duplicate tool name '{tool.name}' found. The first one discovered will be used.")
                    
                    self.tools.append({
                        "name": tool.name,
                        "description": tool.description or "",
                        "inputSchema": tool.inputSchema or {},
                        "client": client  # Associate tool with its client
                    })
            except Exception as e:
                logger.error(f"Failed to discover tools for client connected to {client.server_url}: {e}")
        
        logger.info(f"Agent initialized with {len(self.tools)} tools from {len(self.clients)} clients.")

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
            raise RuntimeError("Agent not initialized correctly - no clients found.")
            
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
        
        formatted_tools = self._format_tools_for_llm()
        
        # Add a timestamp to the conversation history to know when the interaction started
        self.conversation_history.append({"role": "system", "content": f"Interaction started at {datetime.now().isoformat()}"})
        
        try:
            response = self.llm_client.chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),
                messages=messages,
                tools=formatted_tools,
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            return response_message
            
        except Exception as e:
            logger.error(f"Error getting LLM decision: {e}")
            return {"action": "error", "details": str(e)}

    async def run(self, messages: List[Dict[str, Any]], max_iterations: int = 15) -> List[Dict[str, Any]]:
        """
        Main agent loop for processing a conversation and executing tools.
        
        Args:
            messages: The initial messages in the conversation.
            max_iterations: The maximum number of tool calls to prevent infinite loops.
            
        Returns:
            The complete conversation history.
        """
        self.conversation_history = messages
        
        for i in range(max_iterations):
            print(f"--- Agent Iteration {i+1} ---")
            
            # Get the LLM's decision on what to do next
            llm_response = await self._get_llm_decision(self.conversation_history)
            
            # If the model wants to call a tool
            if llm_response.tool_calls:
                self.conversation_history.append(llm_response) # Add assistant's tool request
                
                # Execute all tool calls
                tool_outputs = []
                for tool_call in llm_response.tool_calls:
                    tool_name = tool_call.function.name
                    
                    # Handle internal 'task_completed' tool
                    if tool_name == "task_completed":
                        print("Agent completed the task.")
                        # End the loop by returning the history
                        return self.conversation_history
                    
                    # Handle internal 'suggest_draft' tool
                    if tool_name == "suggest_draft":
                        print("Agent suggested a draft.")
                        # End the loop, the service layer will handle the draft
                        return self.conversation_history

                    try:
                        arguments = json.loads(tool_call.function.arguments)
                        print(f"Tool Call: {tool_name}({arguments})")
                        
                        # Execute the tool and get the result
                        tool_result = await self.execute_tool(tool_name, arguments)
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result,
                        })

                    except json.JSONDecodeError:
                        error_msg = f"Error: Invalid JSON arguments for tool {tool_name}."
                        print(error_msg)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": error_msg,
                        })
                
                self.conversation_history.extend(tool_outputs) # Add tool results to history

            # If the model returns a standard message, the conversation is over
            else:
                self.conversation_history.append(llm_response)
                print("--- Agent Finished ---")
                break
                
        return self.conversation_history


async def run_intelligent_agent(
    mcp_clients: Dict[str, Client],
    user_id: str,
    agent_id: str,
    messages: List[Dict[str, Any]],
    max_iterations: int = 5,
    openrouter_api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    High-level function to run the agent with shared clients.
    
    Args:
        mcp_clients: A dictionary of pre-connected FastMCP.Client objects.
        user_id: The user's ID.
        agent_id: The agent's ID for this run.
        messages: The initial conversation messages.
        max_iterations: Max number of agent iterations.
        openrouter_api_key: OpenRouter API key.
        
    Returns:
        The full conversation history.
    """
    # Initialize the agent with the shared clients
    agent = GenericMCPAgent(mcp_clients, user_id, agent_id, openrouter_api_key)
    
    # Discover the tools from the connected clients
    await agent.discover_tools()
    
    # Run the agent's main processing loop
    conversation_history = await agent.run(messages, max_iterations)
    
    return conversation_history


async def main():
    """
    Example of how to run the agent directly.
    This requires MCP servers to be running.
    """
    # In a real app, these clients would be created at startup and passed in.
    db_mcp_url = "http://localhost:8001/mcp"
    gsheet_mcp_url = "http://localhost:8002/mcp"

    db_client = Client(db_mcp_url)
    gsheet_client = Client(gsheet_mcp_url)

    # Manually manage client connections for this standalone example
    await db_client.__aenter__()
    await gsheet_client.__aenter__()
    
    clients = {"db": db_client, "gsheet": gsheet_client}
    
    try:
        # Example: Ask the agent to read the sheet and summarize it
        user_id = "test_user"
        agent_id = "test_agent"
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the available tools to answer the user's question."},
            {"role": "user", "content": "Please read the Google Sheet and tell me what's in cell A1."}
        ]
        
        conversation = await run_intelligent_agent(clients, user_id, agent_id, messages)
        
        print("\n--- Final Conversation History ---")
        for message in conversation:
            print(message)
            
    finally:
        # Clean up connections
        await db_client.__aexit__(None, None, None)
        await gsheet_client.__aexit__(None, None, None)

if __name__ == "__main__":
    asyncio.run(main()) 