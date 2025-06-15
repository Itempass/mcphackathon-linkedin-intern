# MCP Agent Interaction Implementation Plan

## Overview
This document outlines the implementation plan for the agent's interaction with MCP servers. The MCP server implementation itself is outside our scope - we only need to implement the client-side interaction.

## Core Components

### 1. MCP Client Wrapper
- Implement an async wrapper around the FastMCP client
- Handle connection management and error handling
- Provide high-level methods for each MCP tool interaction

### 2. Tool Implementations

#### 2.1 Database Tools
Based on MCP_CLIENT_INSTRUCTIONS.md, implement the following tools:
- `get_tables`: List all available tables
- `get_table_structure`: Get schema for specific table
- `get_last_added_rows`: Retrieve recent rows with user filtering

#### 2.2 Semantic Search Tools
From sequence diagrams, implement:
- `find_similar_messages`: Find semantically similar messages
- `semantic_search`: General semantic search across messages

### 3. Agent Integration Layer

#### 3.1 Tool Registration
- Register MCP tools with the agent system
- Map agent tool calls to appropriate MCP client methods
- Handle tool call responses and error conditions

#### 3.2 Context Management
- Track message context for agent interactions
- Maintain user context for MCP calls
- Handle agent_id linking with drafts

## Implementation Steps

1. **Setup Phase**
   ```python
   # Basic structure
   class MCPClientWrapper:
       def __init__(self, base_url: str):
           self.client = Client(f"{base_url}/db-mcp")
           
       async def __aenter__(self):
           return await self.client.__aenter__()
           
       async def __aexit__(self, *args):
           await self.client.__aexit__(*args)
   ```

2. **Database Tools Implementation**
   ```python
   class MCPDatabaseTools:
       async def get_tables(self):
           return await self.client.call_tool("get_tables")
           
       async def get_table_structure(self, table_name: str):
           return await self.client.call_tool("get_table_structure", 
                                            {"table_name": table_name})
           
       async def get_last_added_rows(self, table_name: str, rows: int = 10):
           return await self.client.call_tool("get_last_added_rows",
                                            {"table_name": table_name, 
                                             "rows": rows})
   ```

3. **Search Tools Implementation**
   ```python
   class MCPSearchTools:
       async def find_similar_messages(self, 
                                     message_content: str, 
                                     user_id: str):
           return await self.client.call_tool("find_similar_messages",
                                            {"message_content": message_content,
                                             "user_id": user_id})
           
       async def semantic_search(self, 
                               search_query: str,
                               user_id: str):
           return await self.client.call_tool("semantic_search",
                                            {"search_query": search_query,
                                             "user_id": user_id})
   ```

4. **Agent Integration**
   ```python
   class AgentMCPTools:
       def register_tools(self):
           return {
               "find_similar_messages": self.find_similar_messages,
               "semantic_search": self.semantic_search,
               # Add other tools as needed
           }
   ```

## Error Handling

1. **Connection Errors**
   - Implement retry logic for transient failures
   - Proper error propagation to agent system
   - Clear error messages for debugging

2. **Data Validation**
   - Validate all inputs before sending to MCP
   - Handle malformed responses
   - Type checking and conversion

## Testing Strategy

1. **Unit Tests**
   - Test each MCP tool wrapper independently
   - Mock MCP server responses
   - Test error conditions

2. **Integration Tests**
   - Test agent-MCP interaction flow
   - Verify correct handling of tool calls
   - Test error recovery

3. **End-to-End Tests**
   - Test complete message processing flow
   - Verify draft creation and updates
   - Test user context handling

## Security Considerations

1. **User Context**
   - Always include user_id in relevant calls
   - Validate user permissions
   - Handle user-specific data isolation

2. **Error Messages**
   - Sanitize error messages
   - Prevent information leakage
   - Proper logging levels

## Implementation Notes

1. **Async Handling**
   - Use proper async/await patterns
   - Handle concurrent tool calls
   - Manage connection lifecycle

2. **Resource Management**
   - Proper connection pooling
   - Resource cleanup
   - Memory management

3. **Monitoring**
   - Add telemetry for tool calls
   - Track response times
   - Monitor error rates

## Next Steps

1. Implement MCPClientWrapper base class
2. Add database tools implementation
3. Add search tools implementation
4. Integrate with agent system
5. Add comprehensive test suite
6. Add monitoring and telemetry
7. Document API and usage patterns

## Dependencies

- FastMCP client library
- Async runtime support
- JSON handling
- Logging framework 