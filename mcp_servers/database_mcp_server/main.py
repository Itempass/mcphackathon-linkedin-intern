import sys
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, text, inspect
from sqlalchemy.engine import Inspector
import logging

from shared.config import settings

logger = logging.getLogger(__name__)

# Add project root to Python path to import shared models
# This is no longer needed with PYTHONPATH set in supervisord
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# sys.path.insert(0, project_root)

from fastmcp import FastMCP, Context
from api.models.database_models import Base, Message, Agent, MessageType
from api.services import qdrant_client

# --- Configuration ---
# Use the same MySQL engine configuration as the rest of the application
engine = create_async_engine(
    f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
    pool_recycle=3600 # Recycle connections every hour
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# --- FastMCP Application Setup ---
mcp = FastMCP("Database MCP Server")

# --- Service Initialization ---

async def get_db_session():
    """Get a database session"""
    async with AsyncSessionLocal() as session:
        return session

# --- Database Inspection Tools ---

#@mcp.tool(exclude_args=["user_id"])
# TODO: we didn't implement vector search yet, so this tool is not used.
async def get_similar_message(
    user_id: str = None, 
    message_id: Optional[str] = None, 
    message_content: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get messages similar to a specific message by using its content as a query vector.
    Can be used by passing a message_id to fetch the message, or by passing message_content directly.
    If message_id is provided, it will be used to fetch the message content.
    
    Args:
        message_id: The ID of the message to find similar messages for.
        message_content: The content of the message to find similar messages for.
    
    Returns:
        List of similar messages.
    """
    top_k = 10
    query_content = None
    original_message = None

    if user_id is None:
        raise ValueError("user_id is required")
    
    if not message_id and not message_content:
        raise ValueError("Either message_id or message_content must be provided.")

    if message_id:
        original_message = await get_message(user_id, message_id)
        if original_message:
            query_content = original_message.msg_content
        else:
            # If message_id is provided but not found, return a clear message.
            return [{"message": f"Message with ID '{message_id}' not found."}]
    
    # If no message_id was provided, use message_content.
    if not query_content and message_content:
        query_content = message_content
    
    # If for some reason we still don't have content, we can't proceed.
    if not query_content:
        return [{"message": "Could not determine content for similarity search."}]

    # Query Qdrant for similar messages
    similar_messages = qdrant_client.semantic_search(
        collection_name="emails",
        user_id=user_id, 
        query=query_content, 
        top_k=top_k
    )
    
    if not similar_messages:
        # If no similar messages are found, return a clear message
        return [{"message": "No similar messages found."}]

    # Format the results to include the original message info
    results = []
    for msg in similar_messages:
        # Skip the original message in results if we started from a message_id
        if original_message and msg.get('message_id') == original_message.id:
            continue
            
        result = {
            "message_id": msg.get('message_id'),
            "message_content": msg.get('msg_content'),
            "sent or received by user?": msg.get('direction')
        }
        results.append(result)
    
    return results

async def get_message(user_id: str, message_id: str) -> Optional[Message]:
    """Retrieves a single message by its ID and user ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id, Message.user_id == user_id)
        )
        return result.scalar_one_or_none()

async def get_all_messages_of_thread(user_id: str, thread_name: str) -> List[Message]:
    """Retrieves all messages in a thread for a specific user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message).where(Message.user_id == user_id, Message.thread_name == thread_name)
        )
        return result.scalars().all()

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
    host = "0.0.0.0"
    port = settings.CONTAINERPORT_MCP
    
    print(f"🚀 Starting FastMCP Database Server on http://{host}:{port}/mcp")
    mcp.run(transport="streamable-http", host=host, port=port, path="/mcp") 