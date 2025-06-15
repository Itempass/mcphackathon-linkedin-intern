#!/usr/bin/env python3
"""
Simple test script for the MCP Agent.
Tests connection to MCP server and basic tool functionality.
"""

import asyncio
import os
import logging
import json
from typing import Dict, Any

from fastmcp import Client
from src.agent import GenericMCPAgent, run_intelligent_agent

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_basic_connection():
    """Test basic connection and tool listing."""
    
    # Get MCP server URL from environment
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        logger.error("BACKEND_BASE_URL environment variable not set!")
        logger.info("Please set it like: export BACKEND_BASE_URL=http://localhost:8000")
        return
    
    mcp_url = f"{backend_url}/db-mcp"
    logger.info(f"Testing connection to MCP server at: {mcp_url}")
    
    try:
        # Test basic connection and capability discovery
        client = Client(mcp_url)
        async with GenericMCPAgent([client], "test_user", "test_agent") as agent:
            logger.info("✓ Successfully connected to MCP server!")
            
            # Show discovered capabilities
            capabilities = agent.describe_capabilities()
            
            logger.info(f"✓ Discovered capabilities:")
            logger.info(f"  - {len(capabilities['tools'])} tools")
            logger.info(f"  - {len(capabilities['resources'])} resources") 
            logger.info(f"  - {len(capabilities['prompts'])} prompts")
            
            for tool in capabilities['tools']:
                logger.info(f"  Tool: {tool['name']} - {tool['description']}")
            
            return agent.tools
            
    except Exception as e:
        logger.error(f"✗ Failed to connect to MCP server: {e}")
        logger.info("Make sure your MCP server is running and accessible")
        return None


async def test_tool_execution():
    """Test executing a simple tool."""
    
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        logger.error("BACKEND_BASE_URL environment variable not set!")
        return
        
    mcp_url = f"{backend_url}/db-mcp"
    
    try:
        client = Client(mcp_url)
        async with GenericMCPAgent([client], "test_user", "test_agent") as agent:
            
            # Test executing the first available tool
            if agent.tool_names:
                tool_name = agent.tool_names[0]  # Test first available tool
                logger.info(f"Testing tool: {tool_name}")
                
                # Simple test - just call the tool with no arguments
                result = await agent.execute_tool(tool_name, {})
                logger.info(f"Result: {result}")
            else:
                logger.info("No tools available to test")
                
    except Exception as e:
        logger.error(f"✗ Tool execution test failed: {e}")


async def debug_gsheet_agent():
    """Connect to gsheet agent and print raw LLM output for debugging."""
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        logger.error("BACKEND_BASE_URL environment variable not set!")
        return
        
    mcp_url = f"{backend_url}/gsheet-mcp"
    logger.info(f"--- Debugging gsheet agent at: {mcp_url} ---")
    
    try:
        client = Client(mcp_url)
        async with GenericMCPAgent([client], "test_user", "debug_agent") as agent:
            if not agent.tools:
                logger.warning("No tools found for gsheet agent. Cannot debug.")
                return

            logger.info("GSheet agent tools loaded. Preparing to call LLM...")
            
            # A prompt designed to trigger a tool call on the gsheet server
            messages = [
                {"role": "user", "content": "Please read the data from the sheet."}
            ]

            # Get tools in the OpenAI-compatible format
            llm_tools = agent._format_tools_for_llm()

            logger.info("Sending request to LLM...")
            
            # Manually call the LLM to inspect the raw response
            response = agent.llm_client.chat.completions.create(
                model="anthropic/claude-3.7-sonnet:thinking",
                messages=messages,
                tools=llm_tools,
                tool_choice="auto",
            )
            
            logger.info("--- RAW LLM RESPONSE ---")
            # Using model_dump_json for pydantic models gives a nice, clean json string
            logger.info(response.model_dump_json(indent=2))
            logger.info("--- END RAW LLM RESPONSE ---")

            # We can also try to replicate the failure here
            try:
                response_message = response.choices[0].message
                if response_message.tool_calls:
                    tool_call = response_message.tool_calls[0]
                    logger.info("Attempting to parse arguments...")
                    # Fix: Handle empty argument string from LLM
                    arguments_str = tool_call.function.arguments
                    if not arguments_str:
                        arguments = {}
                    else:
                        arguments = json.loads(arguments_str)
                    logger.info(f"Successfully parsed arguments: {arguments}")
                else:
                    logger.info("LLM did not return a tool call.")
            except Exception as e:
                logger.error(f"!!! Replicated the JSON parsing error: {e}")

    except Exception as e:
        logger.error(f"✗ Debugging gsheet agent failed: {e}")


async def test_agent_loop():
    """Test the full agent loop with a simple context."""
    
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        logger.error("BACKEND_BASE_URL environment variable not set!")
        return
        
    mcp_url = f"{backend_url}/db-mcp"
    
    logger.info("Testing intelligent exploration...")
    
    # A simple, universal prompt that should work with any tool set
    messages = [
        {"role": "user", "content": "Please perform a simple test of your capabilities."}
    ]
    
    try:
        client = Client(mcp_url)
        results = await run_intelligent_agent(
            mcp_clients=[client],
            user_id="fb202dd1-8fd2-41e0-8532-8d714d024151",
            agent_id="test_agent_456",
            messages=messages,
            max_iterations=3  # Keep it short for testing
        )
        
        logger.info(f"✓ Intelligent exploration completed. Final conversation length: {len(results)}")
        
    except Exception as e:
        logger.error(f"✗ Intelligent exploration test failed: {e}")


async def main():
    """Run all tests."""
    
    logger.info("=" * 50)
    logger.info("MCP Agent Test Suite")
    logger.info("=" * 50)
    
    # Test 1: Basic connection
    logger.info("\n1. Testing basic connection...")
    tools = await test_basic_connection()
    
    if not tools:
        logger.error("Cannot continue tests - connection failed")
        return
    
    # Test 2: Tool execution  
    logger.info("\n2. Testing tool execution...")
    await test_tool_execution()
    
    # Test 3: Intelligent exploration
    logger.info("\n3. Testing intelligent exploration...")
    await test_agent_loop()
    
    # Test 4: Debug GSheet Agent
    logger.info("\n4. Debugging GSheet Agent LLM call...")
    await debug_gsheet_agent()
    
    logger.info("\n" + "=" * 50)
    logger.info("Test suite completed!")
    logger.info("=" * 50)


if __name__ == "__main__":
    # Check environment first
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        print("\n❌ BACKEND_BASE_URL environment variable not set!")
        print("Please set it first, for example:")
        print("  export BACKEND_BASE_URL=http://localhost:8000")
        print("  python test_agent.py")
        exit(1)
    
    print(f"\n🚀 Starting MCP Agent tests...")
    print(f"📡 MCP Server: {backend_url}/db-mcp")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 