#!/usr/bin/env python3
"""
Database Setup Script for MCP Server
Creates tables and adds mock data for testing
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import hashlib
import uuid

# Add project root to Python path to import shared models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.models.database_models import Base, Message, Agent, MessageType

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

async def drop_tables():
    """Drop all existing database tables"""
    print("Dropping existing database tables...")
    async with engine.begin() as conn:
        # Disable foreign key checks to allow dropping tables with constraints
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Get all table names and drop them
        result = await conn.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        
        for (table_name,) in tables:
            print(f"  Dropping table: {table_name}")
            await conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
        
        # Re-enable foreign key checks
        await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
    print("✅ All existing tables wiped successfully")

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
        
        agent1 = Agent(id=agent1_id, user_id=create_user_id("system"))
        agent2 = Agent(id=agent2_id, user_id=create_user_id("system"))
        
        session.add(agent1)
        session.add(agent2)
        
        # Create mock messages
        timestamp1 = datetime(2024, 6, 14, 10, 30, 0)
        timestamp2 = datetime(2024, 6, 14, 11, 15, 0)
        timestamp3 = datetime(2024, 6, 14, 12, 0, 0)
        timestamp4 = datetime(2024, 6, 14, 13, 30, 0)
        timestamp5 = datetime(2024, 6, 14, 14, 45, 0)
        
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
        
        message4 = Message(
            id=create_message_id("bob_wilson", timestamp4, "Can someone help me with the API documentation?"),
            user_id=create_user_id("bob_wilson"),
            msg_content="Can someone help me with the API documentation?",
            type=MessageType.MESSAGE,
            thread_name="support",
            sender_name="bob_wilson",
            timestamp=timestamp4,
            agent_id=agent1_id
        )
        
        message5 = Message(
            id=create_message_id("carol_davis", timestamp5, "Draft proposal for the new feature."),
            user_id=create_user_id("carol_davis"),
            msg_content="Draft proposal for the new feature.",
            type=MessageType.DRAFT,
            thread_name="development",
            sender_name="carol_davis",
            timestamp=timestamp5,
            agent_id=agent2_id
        )
        
        session.add(message1)
        session.add(message2)
        session.add(message3)
        session.add(message4)
        session.add(message5)
        
        # Commit all changes
        await session.commit()
        
    print("✅ Mock data added successfully:")
    print("  - 2 Agents")
    print("  - 5 Messages (3 MESSAGE type, 2 DRAFT type)")

async def main():
    """Main setup function"""
    print("🚀 Starting database setup...")
    
    try:
        await drop_tables()
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