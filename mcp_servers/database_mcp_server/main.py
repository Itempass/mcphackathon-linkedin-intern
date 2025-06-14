import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, text, inspect
from sqlalchemy.engine import Inspector

from fastmcp import FastMCP, Context
from models import Base, Message, Agent, AgentThread, MessageType, AgentMessageType

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

async def get_db_session():
    """Get a database session"""
    async with AsyncSessionLocal() as session:
        return session

# --- Database Inspection Tools ---

@mcp.tool(exclude_args=["user_id"])
async def get_tables(user_id: str = None) -> List[str]:
    """Get a list of all tables in the database"""
   
    
    async with engine.begin() as conn:
        # Run the inspection in the async context
        def get_table_names(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        table_names = await conn.run_sync(get_table_names)
        return table_names

@mcp.tool(exclude_args=["user_id"])
async def get_table_structure(table_name: str, user_id: str = None) -> Dict[str, Any]:
    """Get the structure/schema of a specific table including columns, types, and constraints"""

    
    async with engine.begin() as conn:
        def inspect_table(connection):
            inspector = inspect(connection)
            
            # Check if table exists
            if table_name not in inspector.get_table_names():
                return None
            
            # Get column information
            columns = inspector.get_columns(table_name)
            
            # Get primary keys
            primary_keys = inspector.get_pk_constraint(table_name)
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            
            return {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": col["default"],
                        "autoincrement": col.get("autoincrement", False)
                    }
                    for col in columns
                ],
                "primary_keys": primary_keys["constrained_columns"] if primary_keys else [],
                "foreign_keys": [
                    {
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],  
                        "referred_columns": fk["referred_columns"]
                    }
                    for fk in foreign_keys
                ],
                "indexes": [
                    {
                        "name": idx["name"],
                        "columns": idx["column_names"],
                        "unique": idx["unique"]
                    }
                    for idx in indexes
                ]
            }
        
        result = await conn.run_sync(inspect_table)
        if result is None:
            raise ValueError(f"Table '{table_name}' not found")
        
        return result

@mcp.tool(exclude_args=["user_id"])
async def get_last_added_rows(table_name: str, rows: int = 10, user_id: str = None) -> List[Dict[str, Any]]:
    """Get the last N rows added to a table (ordered by ID or primary key, defaults to 10 rows)"""
    if user_id is None:
        raise ValueError("user_id is required")
    
    async with AsyncSessionLocal() as session:
        # First, get table structure to find primary key or ID column
        async with engine.begin() as conn:
            def get_pk_column(connection):
                inspector = inspect(connection)
                
                if table_name not in inspector.get_table_names():
                    return None
                
                # Get primary key constraint
                pk_constraint = inspector.get_pk_constraint(table_name)
                if pk_constraint and pk_constraint["constrained_columns"]:
                    return pk_constraint["constrained_columns"][0]
                
                # Fallback: look for common ID column names
                columns = inspector.get_columns(table_name)
                for col in columns:
                    if col["name"].lower() in ["id", "pk", "primary_key"]:
                        return col["name"]
                
                # If no obvious primary key, use the first column
                return columns[0]["name"] if columns else None
            
            pk_column = await conn.run_sync(get_pk_column)
            
            if pk_column is None:
                raise ValueError(f"Table '{table_name}' not found")
        
        # Check if table has a user_id column for filtering
        async with engine.begin() as conn:
            def has_user_id_column(connection):
                inspector = inspect(connection)
                columns = inspector.get_columns(table_name)
                return any(col["name"] == "user_id" for col in columns)
            
            has_user_id = await conn.run_sync(has_user_id_column)
        
        # Build query with optional user_id filtering
        if has_user_id and user_id:
            query = text(f"SELECT * FROM {table_name} WHERE user_id = :user_id ORDER BY {pk_column} DESC LIMIT :limit")
            result = await session.execute(query, {"user_id": user_id, "limit": rows})
        else:
            query = text(f"SELECT * FROM {table_name} ORDER BY {pk_column} DESC LIMIT :limit")
            result = await session.execute(query, {"limit": rows})
        
        # Convert rows to dictionaries
        rows_data = []
        for row in result:
            row_dict = {}
            for key, value in row._mapping.items():
                # Convert non-serializable types to strings
                if hasattr(value, 'isoformat'):  # datetime objects
                    row_dict[key] = value.isoformat()
                else:
                    row_dict[key] = value
            rows_data.append(row_dict)
        
        return rows_data

# --- Server Execution ---
if __name__ == "__main__":
    host = os.environ.get("0.0.0.0")
    port = int(os.environ.get("MCP_DB_SERVERPORT"))
    
    print(f"🚀 Starting FastMCP Database Server on http://{host}:{port}/mcp")
    mcp.run(transport="streamable-http", host=host, port=port, path="/mcp") 