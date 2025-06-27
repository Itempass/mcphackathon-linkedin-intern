#!/usr/bin/env python3
"""
Database Setup Script for MCP Server
Creates tables and adds mock data for testing
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import hashlib
import uuid

# Add project root to Python path to import shared models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from api.models.database_models import Base, Message, Agent, MessageType

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

async def main():
    """Main setup function"""
    print("🚀 Starting database setup...")
    
    try:
        await drop_tables()
        await create_tables()
        print("\n✅ Database setup completed successfully!")
        print("  - MySQL database tables created")
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
        raise
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 