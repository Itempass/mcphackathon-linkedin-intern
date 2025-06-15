import os
import sys
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, text, inspect
from sqlalchemy.engine import Inspector
import logging

logger = logging.getLogger(__name__)

# Add project root to Python path to import shared models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
print(f"DEBUG: Project root: {project_root}")
print(f"DEBUG: Python path: {sys.path[:3]}")

from fastmcp import FastMCP, Context
from src.models.database_models import Base, Message, Agent, MessageType
from src.services.mysql_service import *
from src.services.pinecone_service import PineconeService

# --- Configuration ---
load_dotenv(override=True)
db_url = os.environ.get("MYSQL_DB")
if not db_url:
    raise ValueError("MYSQL_DB environment variable not set.")

if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)

engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# --- FastMCP Application Setup ---
mcp = FastMCP("Database MCP Server")

# --- Service Initialization ---
pinecone_svc = PineconeService()

async def get_db_session():
    """Get a database session"""
    async with AsyncSessionLocal() as session:
        return session

# --- Database Inspection Tools ---

@mcp.tool(exclude_args=["user_id"])
async def get_similar_message(message_id: str, user_id: str = None) -> List[Dict[str, Any]]:
    """
    Get messages similar to a specific message by using the message content as a query vector
    
    Args:
        message_id: The ID of the message to find similar messages for
    
    Returns:
        List of similar messages
    """
    top_k = 10

    if user_id is None:
        raise ValueError("user_id is required")
    
    # Get the original message from MySQL
    original_message = await get_message(user_id, message_id)
    if original_message is None:
        raise ValueError(f"Message with ID '{message_id}' not found for user '{user_id}'")
    
    # Use the message content as the query for finding similar messages
    query_content = original_message.msg_content
    
    # Query Pinecone for similar messages
    similar_messages = pinecone_svc.query_messages(user_id, query_content, top_k)
    print(f"DEBUG: Similar messages: {similar_messages}")
    # Format the results to include the original message info
    results = []
    for msg in similar_messages:
        # Skip the original message in results (same message_id)
        if msg.get('message_id') == message_id:
            continue
            
        result = {
            "message_id": msg.get('message_id'),
            "message_content": msg.get('msg_content'),
            "sent or received by user?": msg.get('direction')
        }
        results.append(result)
    
    return results

@mcp.tool(exclude_args=["user_id"])
async def get_thread_by_message_id(message_id: str, user_id: str = None) -> List[Dict[str, Any]]:
    """
    Get all messages in a thread, identified by a single message_id in that thread.

    Args:
        message_id: The ID of one message in the desired thread.

    Returns:
        A list of all messages in the thread, sorted by timestamp.
    """
    if user_id is None:
        raise ValueError("user_id is required")

    # 1. Get the message to find the thread_name
    message = await get_message(user_id, message_id)
    if not message:
        raise ValueError(f"Message with ID '{message_id}' not found for user '{user_id}'")

    thread_name = message.thread_name

    # 2. Get all messages from that thread
    thread_messages = await get_all_messages_of_thread(user_id, thread_name)

    # Sort messages by timestamp to maintain conversational order
    thread_messages.sort(key=lambda m: m.timestamp)

    # 3. Format messages into a list of dicts
    results = []
    for msg in thread_messages:
        results.append({
            "id": msg.id,
            "msg_content": msg.msg_content,
            "type": msg.type.name if msg.type else None,
            "thread_name": msg.thread_name,
            "sender_name": msg.sender_name,
            "timestamp": msg.timestamp.isoformat(),
            "agent_id": msg.agent_id,
        })

    return results

# --- Server Execution ---
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_DB_SERVERPORT"))
    
    print(f"🚀 Starting FastMCP Database Server on http://{host}:{port}/mcp")
    mcp.run(transport="streamable-http", host=host, port=port, path="/mcp") 