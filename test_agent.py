#!/usr/bin/env python3
"""
Simple test script for the MCP Agent.
Tests connection to MCP server and basic tool functionality.
"""

import asyncio
import os
import logging
from typing import Dict, Any

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
    
    mcp_url = f"{backend_url}/mcp"
    logger.info(f"Testing connection to MCP server at: {mcp_url}")
    
    try:
        # Test basic connection and capability discovery
        async with GenericMCPAgent(mcp_url, "test_user", "test_agent") as agent:
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
        
    mcp_url = f"{backend_url}/mcp"
    
    try:
        async with GenericMCPAgent(mcp_url, "test_user", "test_agent") as agent:
            
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


async def test_agent_loop():
    """Test the full agent loop with a simple context."""
    
    backend_url = os.getenv("BACKEND_BASE_URL")
    if not backend_url:
        logger.error("BACKEND_BASE_URL environment variable not set!")
        return
        
    mcp_url = f"{backend_url}/mcp"
    
    logger.info("Testing intelligent exploration...")
    
    # Context that works with any MCP server
    test_context = {
        "thread_name": "test_thread_123",
        "search_query": "test query",
        "table_name": "messages",
        "message_id": "82b8f25cb895ad684a3f8bfc34794bf1",
        "user_id": "3d6296ea-3f22-44d8-b6f1-1a5fbf65e0b6",
        "action": "explore"
    }
    
    try:
        results = await run_intelligent_agent(
            server_url_or_path=mcp_url,
            user_id="3d6296ea-3f22-44d8-b6f1-1a5fbf65e0b6",
            agent_id="test_agent_456",
            context=test_context,
            max_iterations=3  # Keep it short for testing
        )
        
        logger.info(f"✓ Intelligent exploration completed with {len(results)} tool executions:")
        
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. {result}")
                
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
    print(f"📡 MCP Server: {backend_url}/mcp")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 