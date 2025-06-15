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
from typing import Dict, List, Any, Optional
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
    
    def _create_system_prompt(self, context: Dict[str, Any]) -> str:
        """Create system prompt for the LLM based on available tools and context."""
        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in self.tools
        ])
        
        return f"""You are an AI assistant with access to MCP (Model Context Protocol) tools. Your job is to help the user by intelligently using these tools to gather information and complete tasks.

AVAILABLE TOOLS:
{tools_desc}

CONTEXT PROVIDED:
{json.dumps(context, indent=2)}

INSTRUCTIONS:
1. Analyze the context and determine what the user needs
2. Use the available tools intelligently to gather information or complete tasks
3. You can call multiple tools in sequence if needed
4. Always explain your reasoning before calling tools
5. Provide a helpful summary of what you discovered

When you want to call a tool, respond with JSON in this format:
{{"action": "call_tool", "tool": "tool_name", "arguments": {{"arg1": "value1"}}}}

When you're done, respond with:
{{"action": "complete", "summary": "What you accomplished"}}

Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
User ID: {self.user_id}
"""
    
    async def _get_llm_decision(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get decision from LLM about what to do next."""
        if not self.has_llm:
            # Fallback to simple heuristic
            return {"action": "call_tool", "tool": self.tools[0]["name"], "arguments": {}}
        
        try:
            response = self.llm_client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",  # Use a good model from OpenRouter
                messages=messages,
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"LLM response: {content}")
            
            # Try to parse as JSON
            try:
                decision = json.loads(content)
                logger.info(f"LLM decision: {decision}")
                return decision
            except json.JSONDecodeError:
                # Try to extract JSON from the response (LLM might provide explanation + JSON)
                import re
                # Look for JSON that starts with { and contains "action"
                json_start = content.find('{"action"')
                if json_start == -1:
                    json_start = content.find('{ "action"')
                
                if json_start != -1:
                    # Find the matching closing brace
                    brace_count = 0
                    json_end = json_start
                    for i, char in enumerate(content[json_start:], json_start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    
                    try:
                        json_str = content[json_start:json_end]
                        decision = json.loads(json_str)
                        logger.info(f"LLM decision (extracted): {decision}")
                        return decision
                    except json.JSONDecodeError:
                        pass
                
                # If not JSON, treat as reasoning and ask for next step
                logger.info(f"LLM provided reasoning instead of JSON: {content[:200]}...")
                return {
                    "action": "reasoning", 
                    "content": content,
                    "next": "call_tool" if any(tool["name"] in content.lower() for tool in self.tools) else "complete"
                }
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Fallback to simple exploration
            return {"action": "call_tool", "tool": self.tools[0]["name"], "arguments": {}}
    
    async def run_intelligent_agent(self, context: Dict[str, Any], max_iterations: int = 5) -> List[str]:
        """
        Run the AI agent with intelligent decision-making.
        
        Args:
            context: Context dictionary with user's request/data
            max_iterations: Maximum number of tool calls to make
            
        Returns:
            List of results from tool executions
        """
        if not self.tools:
            return ["No tools available"]
        
        logger.info(f"Starting intelligent exploration with {len(self.tools)} available tools")
        
        # Initialize conversation with system prompt
        messages = [
            {"role": "system", "content": self._create_system_prompt(context)},
            {"role": "user", "content": f"Please help me with this context: {json.dumps(context)}"}
        ]
        
        results = []
        
        for iteration in range(max_iterations):
            try:
                # Get LLM decision
                decision = await self._get_llm_decision(messages)
                
                if decision.get("action") == "complete":
                    logger.info(f"Agent completed task: {decision.get('summary', 'No summary')}")
                    break
                
                elif decision.get("action") == "call_tool":
                    tool_name = decision.get("tool")
                    tool_args = decision.get("arguments", {})
                    
                    if tool_name in self.tool_names:
                        # Execute the tool
                        result = await self.execute_tool(tool_name, tool_args)
                        results.append(result)
                        
                        # Add to conversation history
                        messages.append({
                            "role": "assistant", 
                            "content": f"I'll call {tool_name} with args {tool_args}"
                        })
                        messages.append({
                            "role": "user", 
                            "content": f"Tool result: {result}"
                        })
                        
                    else:
                        logger.error(f"Unknown tool: {tool_name}")
                        break
                
                elif decision.get("action") == "reasoning":
                    # LLM is thinking, add to conversation and continue
                    messages.append({
                        "role": "assistant",
                        "content": decision.get("content", "Thinking...")
                    })
                    messages.append({
                        "role": "user",
                        "content": "Please proceed with your next action."
                    })
                
                else:
                    logger.error(f"Unknown action: {decision.get('action')}")
                    break
                    
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                break
        
        logger.info(f"Intelligent exploration completed after {len(results)} actions")
        return results


# Convenience function for simple usage
async def run_intelligent_agent(
    server_url_or_path: str,
    user_id: str,
    agent_id: str,
    context: Dict[str, Any],
    max_iterations: int = 5,
    openrouter_api_key: Optional[str] = None
) -> List[str]:
    """
    Run an intelligent MCP agent with AI decision-making.
    
    Args:
        server_url_or_path: MCP server URL or path
        user_id: User ID for context
        agent_id: Agent ID for tracking  
        context: Context dictionary with user's request/data
        max_iterations: Maximum number of tool calls
        openrouter_api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var)
        
    Returns:
        List of results from tool executions
    """
    async with GenericMCPAgent(server_url_or_path, user_id, agent_id, openrouter_api_key) as agent:
        return await agent.run_intelligent_agent(context, max_iterations)


# Example usage
async def main():
    """Example of how to use the Generic MCP Agent."""
    
    # Example context - this works with ANY MCP server
    context = {
        "thread_name": "example_thread",
        "search_query": "important information",
        "table_name": "messages",
        "action": "explore"
    }
    
    # Run the agent - it will intelligently explore whatever tools are available
    results = await run_intelligent_agent(
        server_url_or_path="http://localhost:8000/mcp", 
        user_id="user123",
        agent_id="agent456", 
        context=context,
        max_iterations=3
    )
    
    # Process results
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main()) 