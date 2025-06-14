#!/usr/bin/env python3
"""
Database Setup Script for MCP Server
Creates tables and adds mock data for testing
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import hashlib
import uuid

from models import Base, Message, Agent, AgentThread, MessageType, AgentMessageType

# Load environment variables
load_dotenv(override=True)

# Database configuration
db_url = os.environ.get("MYSQL_DB")
if not db_url:
    raise ValueError("MYSQL_DB environment variable not set.")

if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)

engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def create_message_id(sender_name: str, timestamp: datetime, content: str) -> str:
    """Create a hash ID for message based on sender, timestamp, and content"""
    data = f"{sender_name}_{timestamp.isoformat()}_{content}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

def create_user_id(user_name: str) -> str:
    """Create a hash ID for user based on username"""
    return hashlib.sha256(user_name.encode()).hexdigest()[:32]

async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

async def add_mock_data():
    """Add mock data to the database"""
    print("Adding mock data...")
    
    async with AsyncSessionLocal() as session:
        # Create mock agents
        agent1_id = str(uuid.uuid4())
        agent2_id = str(uuid.uuid4())
        
        agent1 = Agent(id=agent1_id)
        agent2 = Agent(id=agent2_id)
        
        session.add(agent1)
        session.add(agent2)
        
        # Create mock messages
        timestamp1 = datetime(2024, 6, 14, 10, 30, 0)
        timestamp2 = datetime(2024, 6, 14, 11, 15, 0)
        timestamp3 = datetime(2024, 6, 14, 12, 0, 0)
        
        message1 = Message(
            id=create_message_id("john_doe", timestamp1, "Hello, this is my first message!"),
            user_id=create_user_id("john_doe"),
            msg_content="Hello, this is my first message!",
            type=MessageType.MESSAGE,
            thread_name="general_chat",
            sender_name="john_doe",
            timestamp=timestamp1,
            agent_id=agent1_id
        )
        
        message2 = Message(
            id=create_message_id("jane_smith", timestamp2, "Working on the database integration."),
            user_id=create_user_id("jane_smith"),
            msg_content="Working on the database integration.",
            type=MessageType.MESSAGE,
            thread_name="development",
            sender_name="jane_smith",
            timestamp=timestamp2,
            agent_id=agent2_id
        )
        
        message3 = Message(
            id=create_message_id("alice_johnson", timestamp3, "This is a draft message for review."),
            user_id=create_user_id("alice_johnson"),
            msg_content="This is a draft message for review.",
            type=MessageType.DRAFT,
            thread_name="general_chat",
            sender_name="alice_johnson",
            timestamp=timestamp3,
            agent_id=None  # No agent assigned to this message
        )
        
        session.add(message1)
        session.add(message2)
        session.add(message3)
        
        # Create mock agent threads
        thread1 = AgentThread(
            type=AgentMessageType.system_prompt,
            content="You are a helpful assistant specialized in database operations.",
            agent_id=agent1_id
        )
        
        thread2 = AgentThread(
            type=AgentMessageType.user_prompt,
            content="Please help me understand the database schema.",
            agent_id=agent1_id
        )
        
        thread3 = AgentThread(
            type=AgentMessageType.toolcall_response_success,
            content="Database query executed successfully. Found 3 matching records.",
            agent_id=agent2_id
        )
        
        session.add(thread1)
        session.add(thread2)
        session.add(thread3)
        
        # Commit all changes
        await session.commit()
        
    print("✅ Mock data added successfully:")
    print("  - 2 Agents")
    print("  - 3 Messages (2 MESSAGE type, 1 DRAFT type)")
    print("  - 3 Agent Threads")

async def main():
    """Main setup function"""
    print("🚀 Starting database setup...")
    
    try:
        await create_tables()
        await add_mock_data()
        print("\n✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
        raise
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 