# Database MCP Server

FastMCP server providing AI-friendly database tools for Users and Orders management.

## Quick Start

1. **Environment Setup**
   ```bash
   # Set in .env file
   MYSQL_DB=mysql://username:password@host:port/database
   FASTMCP_PORT=8001
   ```

2. **Install & Run**
   ```bash
   cd mcp_servers/database_mcp_server
   pip install -r requirements.txt
   python main.py
   ```

3. **Connect**
   - URL: `http://localhost:8001/mcp`
   - Transport: `streamable-http`

## Testing & Development

### Using MCP Inspector
1. Start the server: `python main.py`
2. Run inspector: `fastmcp dev main.py`
3. Add server URL: `http://localhost:8001/mcp`

### Direct Testing
```python
from fastmcp import Client

async def test():
    async with Client("http://localhost:8001/mcp") as client:
        # List tools
        tools = await client.list_tools()
        print([tool.name for tool in tools])
        
        # Test database stats
        stats = await client.call_tool("get_database_stats", {})
        print(stats)
```