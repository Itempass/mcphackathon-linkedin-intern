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
import mysql.connector

# Add project root to Python path to import shared models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from api.models.database_models import Base, Message, Agent, MessageType

# Load environment variables
load_dotenv(override=True)

# --- Database Configuration ---
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_host = os.getenv("MYSQL_HOST", "db")
db_name = os.getenv("MYSQL_DATABASE")

if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("One or more MySQL environment variables are not set (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE).")

# The async MySQL driver uses a different connection string format
db_url = f"mysql+aiomysql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_async_engine(db_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    """Create all database tables if they don't already exist."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully (if they didn't exist).")

async def main():
    """Main setup function"""
    print("🚀 Starting database setup...")
    
    try:
        await create_tables()
        print("\n✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 