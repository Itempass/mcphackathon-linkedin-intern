from typing import Dict

# Global state to hold shared MCP clients
# This will be populated at application startup.
mcp_clients: Dict = {} 