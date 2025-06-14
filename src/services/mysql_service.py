import os
import asyncio
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import hashlib
import uuid

from src.models.database_models import Base, Message, Agent, MessageType

# Load environment variables
load_dotenv()

# Database configuration
db_url = os.environ.get("MYSQL_DB")
if not db_url:
    raise ValueError("MYSQL_DB environment variable not set.")

if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)

engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def create_user_id(user_name: str) -> str:
    """Create a hash ID for user based on username"""
    return hashlib.sha256(user_name.encode()).hexdigest()[:32]

async def get_all_messages_of_type(user_id: str, message_type: MessageType) -> List[Message]:
    """
    Get all messages of a specific type for a user
    
    Args:
        user_id: The user ID
        message_type: The type of messages to retrieve (MessageType.DRAFT or MessageType.MESSAGE)
    
    Returns:
        List of Message objects
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Message).where(
            Message.user_id == user_id,
            Message.type == message_type
        )
        result = await session.execute(stmt)
        return result.scalars().all()

async def get_all_messages_of_thread(user_id: str, thread_name: str) -> List[Message]:
    """
    Get all messages in a specific thread for a user
    
    Args:
        user_id: The user ID
        thread_name: The name of the thread
    
    Returns:
        List of Message objects
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Message).where(
            Message.user_id == user_id,
            Message.thread_name == thread_name
        )
        result = await session.execute(stmt)
        return result.scalars().all()

async def get_message(user_id: str, message_id: str) -> Optional[Message]:
    """
    Get a specific message for a user
    
    Args:
        user_id: The user ID
        message_id: The ID of the message to retrieve
    
    Returns:
        Message object or None if not found
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Message).where(
            Message.user_id == user_id,
            Message.id == message_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def remove_message(user_id: str, message_id: str) -> bool:
    """
    Remove a message for a specific user
    
    Args:
        user_id: The user ID
        message_id: The ID of the message to remove
    
    Returns:
        True if message was removed, False if not found
    """
    async with AsyncSessionLocal() as session:
        stmt = delete(Message).where(
            Message.user_id == user_id,
            Message.id == message_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

async def remove_agent(user_id: str, agent_id: str) -> bool:
    """
    Remove an agent for a specific user
    
    Args:
        user_id: The user ID
        agent_id: The ID of the agent to remove
    
    Returns:
        True if agent was removed, False if not found
    """
    async with AsyncSessionLocal() as session:
        stmt = delete(Agent).where(
            Agent.user_id == user_id,
            Agent.id == agent_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

async def get_agent(user_id: str, agent_id: str) -> Optional[Agent]:
    """
    Get an agent for a user (includes messages)
    
    Args:
        user_id: The user ID
        agent_id: The agent ID
    
    Returns:
        Agent object or None if not found
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Agent).where(
            Agent.user_id == user_id,
            Agent.id == agent_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def upsert_agent(user_id: str, agent_id: str, messages_array: Optional[List[dict]] = None) -> Agent:
    """
    Insert or update an agent for a user (overwrites if exists)
    
    Args:
        user_id: The user ID
        agent_id: The ID for the agent
        messages_array: Optional list of LLM conversation messages in format:
                       [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]
    
    Returns:
        The created/updated Agent object
    """
    import json
    
    async with AsyncSessionLocal() as session:
        # Convert messages_array to JSON string if provided
        messages_json = None
        if messages_array:
            messages_json = json.dumps(messages_array)
        
        # Check if agent exists
        stmt = select(Agent).where(
            Agent.user_id == user_id,
            Agent.id == agent_id
        )
        result = await session.execute(stmt)
        existing_agent = result.scalar_one_or_none()
        
        if existing_agent:
            # Update existing agent
            existing_agent.messages = messages_json
            agent = existing_agent
        else:
            # Create new agent
            agent = Agent(
                id=agent_id,
                user_id=user_id,
                messages=messages_json
            )
            session.add(agent)
        
        await session.commit()
        await session.refresh(agent)
        return agent

async def add_message(
    user_id: str,
    message_id: str,
    message_type: MessageType,
    message_content: str,
    thread_name: str,
    sender_name: str,
    timestamp: datetime,
    agent_id: Optional[str] = None
) -> Message:
    """
    Add a new message for a user
    
    Args:
        user_id: The user ID
        message_id: The ID for the new message
        message_type: The type of the message (MessageType.DRAFT or MessageType.MESSAGE)
        message_content: The content of the message
        thread_name: The name of the thread
        sender_name: The name of the sender
        timestamp: The timestamp of the message
        agent_id: Optional agent ID to associate with the message
    
    Returns:
        The created Message object
    """
    async with AsyncSessionLocal() as session:
        message = Message(
            id=message_id,
            user_id=user_id,
            msg_content=message_content,
            type=message_type,
            thread_name=thread_name,
            sender_name=sender_name,
            timestamp=timestamp,
            agent_id=agent_id
        )
        
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

# Utility functions for creating IDs (same as in setup script)
def create_message_id(sender_name: str, timestamp: datetime, content: str) -> str:
    """Create a hash ID for message based on sender, timestamp, and content"""
    data = f"{sender_name}_{timestamp.isoformat()}_{content}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


# Close database connection
async def close_connection():
    """Close the database engine"""
    await engine.dispose()
