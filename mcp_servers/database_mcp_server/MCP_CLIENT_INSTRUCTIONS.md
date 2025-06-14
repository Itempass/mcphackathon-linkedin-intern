# Database MCP Server - Client Instructions

This guide explains how to connect to and use the Database MCP Server using the FastMCP client.

## Overview

The Database MCP Server provides tools for inspecting database structure and retrieving data:

- `get_tables`: List all tables in the database
- `get_table_structure`: Get detailed schema information for a specific table
- `get_last_added_rows`: Retrieve the most recent rows from a table (with user-specific filtering)

## Setup

1. **Install FastMCP**:
   ```bash
   pip install fastmcp
   ```

2. **Environment Variable**:
   Set the `BACKEND_BASE_URL` and `MYSQL_DB` environment variables:
   ```bash
   export BACKEND_BASE_URL="<your_backend_base_url>"
   export MYSQL_DB="mysql://username:password@localhost:3306/mcp_db"
   ```

## Database Schema

The server manages two main tables:

1. **Messages**
   ```sql
   CREATE TABLE messages (
       id VARCHAR(32) PRIMARY KEY,
       user_id VARCHAR(32) NOT NULL,
       msg_content TEXT NOT NULL,
       type ENUM('DRAFT', 'MESSAGE') NOT NULL,
       thread_name VARCHAR(255) NOT NULL,
       sender_name VARCHAR(255) NOT NULL,
       timestamp DATETIME NOT NULL,
       agent_id VARCHAR(36)
   );
   ```

2. **Agents**
   ```sql
   CREATE TABLE agents (
       id VARCHAR(36) PRIMARY KEY,
       user_id VARCHAR(32) NOT NULL,
       messages JSON
   );
   ```

## Basic Usage

```python
import os
import asyncio
from fastmcp import Client

# Connect to the MCP server
base_url = os.getenv("BACKEND_BASE_URL")
client = Client(f"{base_url}/mcp")

async def main():
    async with client:
        # List all tables
        tables = await client.call_tool("get_tables")
        print("Tables:", tables[0].text)
        
        # Get table structure
        structure = await client.call_tool("get_table_structure", {
            "table_name": "messages"
        })
        print("Structure:", structure[0].text)
        
        # Get recent rows
        recent = await client.call_tool("get_last_added_rows", {
            "table_name": "messages",
            "rows": 5
        })
        print("Recent data:", recent[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools

### get_tables
Lists all database tables.
```python
tables_result = await client.call_tool("get_tables")
tables = eval(tables_result[0].text)  # Returns list of table names
```

### get_table_structure
Get schema information for a table.
```python
structure = await client.call_tool("get_table_structure", {
    "table_name": "your_table_name"
})
schema = eval(structure[0].text)  # Returns dict with columns, keys, etc.
```

### get_last_added_rows
Get recent rows from a table.
```python
recent = await client.call_tool("get_last_added_rows", {
    "table_name": "your_table_name",
    "rows": 10  # optional, defaults to 10
})
data = eval(recent[0].text)  # Returns list of row dictionaries
```

## Complete Example

```python
import os
import asyncio
from fastmcp import Client

async def explore_database():
    base_url = os.getenv("BACKEND_BASE_URL")
    client = Client(f"{base_url}/mcp")
    
    async with client:
        # Get all tables
        tables_result = await client.call_tool("get_tables")
        tables = eval(tables_result[0].text)
        print(f"Found {len(tables)} tables: {tables}")
        
        # Explore messages table
        structure = await client.call_tool("get_table_structure", {
            "table_name": "messages"
        })
        schema = eval(structure[0].text)
        print("\nMessages table columns:")
        for col in schema['columns']:
            print(f"  - {col['name']}: {col['type']}")
        
        # Get recent messages
        recent = await client.call_tool("get_last_added_rows", {
            "table_name": "messages",
            "rows": 3
        })
        data = eval(recent[0].text)
        print(f"\nRecent messages: {len(data)} rows")
        for msg in data:
            print(f"  - {msg['sender_name']}: {msg['msg_content'][:50]}...")

if __name__ == "__main__":
    asyncio.run(explore_database())
```

## Error Handling

```python
from fastmcp.exceptions import ClientError

async with client:
    try:
        result = await client.call_tool("get_table_structure", {
            "table_name": "nonexistent_table"
        })
    except ClientError as e:
        print(f"Error: {e}")
```

## Notes

- **User Isolation**: Data is automatically filtered by user when applicable
- **Data Format**: All responses are returned as text that can be parsed with `eval()`
- **Connection**: Always use `async with client:` for proper connection management
- **Message IDs**: Generated as SHA-256 hash of sender, timestamp, and content
- **Agent IDs**: Generated as UUIDs

For more FastMCP information, see: https://gofastmcp.com/clients/client 