# Plan: Agent to MCP Server Interaction

This document outlines how a client-side agent, located in the `src/` directory, will communicate with and utilize the `database_mcp_server`.

## Objective

To enable a Python agent in `src/` to connect to, understand, and query the data exposed by the `database_mcp_server`. The goal is to treat the database server as an intelligent, navigable data source, abstracting away direct database queries.

## Core Concepts

The interaction relies on the client-server architecture of the MCP protocol.

1.  **The Server**: Our `database_mcp_server` acts as the data provider. Its sole job is to expose the database schema and data in a structured, AI-friendly way.
2.  **The Agent**: The agent in `src/` acts as the **client**. It is the consumer of the data provided by the server. It will contain its own logic and will make requests to the server to get the data it needs.
3.  **MCP Client Library**: To facilitate communication, the agent will need to use an MCP client library. This library handles the underlying network requests (HTTP) and makes interacting with the server feel like using a regular Python library.

## Interaction Workflow

Here is a step-by-step breakdown of how the agent will work with the server.

### Step 1: Connection and Discovery

First, the agent needs to know the server exists and what it can do.

1.  **Establish Connection**: The agent, using the MCP client library, will be configured with the URL of the running `database_mcp_server` (e.g., `http://127.0.0.1:8000`).
2.  **Explore the Data Model**: The agent's first action will be to call the `explore_data_model()` function on the server. This is a standard MCP function.
3.  **Receive the Schema**: The server will respond with a complete schema of its capabilities. This schema will describe all the available entities (like `User` and `Order`), their fields (`id`, `email`, `total`), their data types, and critically, the **relationships** between them (like a `User` having a list of `Orders`).

This discovery step is crucial. It allows the agent to dynamically understand the API without having it hardcoded.

### Step 2: Querying Data

Once the agent knows the schema, it can start asking for data. The `enrichmcp` framework automatically creates several functions for the agent to call.

-   **Listing Records**: The agent can request a list of all records for an entity, for example, by calling a function like `list_users()`. It can also provide parameters to filter the results, such as `list_users(status='active')`.
-   **Fetching a Single Record**: The agent can retrieve a specific record by its identifier, for instance, by calling `get_user(id=123)`.

The MCP client library will make these remote functions appear as if they were local methods, hiding the complexity of the API call.

### Step 3: Navigating Relationships

This is one of the most powerful features. The schema tells the agent how entities are connected, and the agent can traverse these connections.

1.  **Fetch an initial record**: The agent fetches a single `User` object.
2.  **Access a related attribute**: This `User` object, returned by the server, will have an attribute for its relationships, such as `.orders`.
3.  **Trigger a new request**: When the agent accesses `user.orders`, the MCP client library, under the hood, automatically makes a new request to the server to fetch the orders associated with that specific user.

This allows the agent to navigate the data graph intuitively, moving from one entity to another (e.g., from a User to their Orders, and from an Order to the User who placed it) just by accessing object attributes.

## Summary: Agent Lifecycle

In essence, the agent in `src/` will:

1.  **Initialize** an MCP client with the server's address.
2.  **Discover** the server's data model by exploring its schema.
3.  **Query** for the specific data it needs using high-level functions (`list_users`, `get_user`).
4.  **Navigate** between related data points to build a complete picture.
5.  **Process** the retrieved data to perform its designated task.

This approach effectively decouples the agent's logic from the database's implementation, allowing the two to be developed and maintained independently. The MCP server acts as a semantic bridge between them. 