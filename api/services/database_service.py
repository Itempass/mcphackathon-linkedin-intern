import os
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import hashlib
import uuid
from sqlalchemy.exc import IntegrityError
import json
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy import event
from sqlalchemy.engine import Engine

from api.models.database_models import Base, Message, Agent, MessageType
from shared.config import settings

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --- Database Configuration ---
# The async MySQL driver uses a different connection string format
engine = create_async_engine(
    f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
    pool_recycle=3600 # Recycle connections every hour
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
# --- Service Functions ---

def create_user_id(user_name: str) -> str:
    """Create a hash ID for user based on username"""
    return hashlib.sha256(user_name.encode()).hexdigest()[:32]

async def get_all_messages_of_type(user_id: str, message_type: MessageType) -> List[Message]:
    """
    Get all messages of a specific type for a user
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
    """
    logger.info(f"Upserting agent {agent_id} for user {user_id}.")
    async with AsyncSessionLocal() as session:
        messages_json = json.dumps(messages_array) if messages_array else None
        
        # Try to get the existing agent
        existing_agent = await session.get(Agent, agent_id)
        
        if existing_agent:
            # Update existing agent
            logger.info(f"Agent {agent_id} found. Updating messages.")
            existing_agent.messages = messages_json
            agent = existing_agent
        else:
            # Create new agent
            logger.info(f"Agent {agent_id} not found. Creating new agent record.")
            agent = Agent(
                id=agent_id,
                user_id=user_id,
                messages=messages_json
            )
            session.add(agent)
        
        await session.commit()
        await session.refresh(agent)
        logger.info(f"Successfully committed agent {agent_id} to the database.")
        return agent

async def add_message(
    user_id: str,
    message_id: str,
    message_type: MessageType,
    msg_content: str,
    thread_name: str,
    sender_name: str,
    timestamp: datetime,
    agent_id: Optional[str] = None
) -> Message:
    """
    Add a new message for a user, or do nothing if it already exists.
    """
    logger.debug(f"Adding message {message_id} for user {user_id}")
    
    async with AsyncSessionLocal() as session:
        stmt = mysql_insert(Message).values(
            id=message_id,
            user_id=user_id,
            msg_content=msg_content,
            type=message_type,
            thread_name=thread_name,
            sender_name=sender_name,
            timestamp=timestamp,
            agent_id=agent_id
        )
        
        # This is the key change: specify the columns for the conflict
        stmt = stmt.on_duplicate_key_update(id=stmt.inserted.id) # No-op on duplicate

        await session.execute(stmt)
        await session.commit()

        # After the upsert, fetch the message to return it
        message = await get_message(user_id, message_id)
        if message:
            logger.debug(f"Successfully added or found message {message_id}")
            return message
        else:
            # This case should ideally not be hit if the insert happened,
            # but as a safeguard, we log it.
            logger.error(f"Failed to add or find message {message_id} after upsert attempt.")
            raise Exception("Could not retrieve message after upsert.")

def create_message_id(sender_name: str, timestamp: datetime, content: str) -> str:
    """Create a unique hash ID for the message"""
    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
    hash_input = f"{sender_name}-{time_str}-{content}"
    return hashlib.sha256(hash_input.encode()).hexdigest()

async def close_connection():
    """Closes the database engine connection."""
    await engine.dispose() 