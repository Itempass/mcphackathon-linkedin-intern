# Plan: Database MCP Server

This document outlines the plan to create a new MCP server that provides an AI-friendly API for our existing MySQL database.

## Objective

The goal is to build a standalone MCP server using the `enrichmcp` framework. This server will connect to our MySQL database, interpret its schema, and expose it through a networked API that AI agents can easily query and navigate. The project will be self-contained within the `mcp_servers/database_mcp_server/` directory.

## Architecture: Networked API

We will implement a networked API architecture. The `database_mcp_server` will run as an independent, standalone web server process. Other components, such as agents located in the `src/` directory, will interact with it by making network requests to its endpoints.

This approach creates a clean separation of concerns, enhances reusability, and aligns with the design philosophy of the `enrichmcp` framework. For more details on how a client agent will interact with this server, see the `documentation/plans/agent_interaction_plan.md` document.

## Project Structure

The final file structure for the new MCP server will be as follows:

```
mcp_servers/
└── database_mcp_server/
    ├── README.md
    ├── requirements.txt
    ├── main.py
    └── models.py
```

## Component Breakdown

Each file has a distinct and important role in the server's operation:

### `requirements.txt` - Dependencies

This file will list all the Python libraries required for the server to run. Using a `requirements.txt` file ensures that anyone running the project can easily install the correct dependencies. The key libraries will be:
- `enrichmcp`: The core framework for building the MCP server.
- `SQLAlchemy`: The library for mapping database tables to Python objects (ORM).
- `aiomysql`: An asynchronous driver that allows our Python code to communicate with the MySQL database efficiently.
- `uvicorn`: A high-performance server to run our application.
- `python-dotenv`: A utility to load environment variables, like our database connection string, from a `.env` file into the application's environment.

### `models.py` - Database Schema Definition

This file will contain the data models that represent our database's structure. We will use SQLAlchemy 2.0's ORM capabilities to define Python classes that map directly to our MySQL tables.

- We will define a `Base` class using `DeclarativeBase` and `EnrichSQLAlchemyMixin`. All other models will inherit from this `Base`.
- Each class will represent a table (e.g., a `User(Base)` class for the `users` table).
- The attributes of each class will use `Mapped` and `mapped_column` to represent the table's columns (e.g., `id: Mapped[int] = mapped_column(primary_key=True)`).
- SQLAlchemy `relationship` constructs will be defined within these classes to represent foreign key connections between tables (e.g., a `orders: Mapped[list["Order"]] = relationship()`).

This approach allows SQLAlchemy to understand our full database schema, including the relationships between tables, which is crucial for the automatic API generation.

### `main.py` - The Core Application

This is the heart of the MCP server. It will be responsible for orchestrating all the different components to run a standalone web server, heavily inspired by robust application lifecycle patterns.

1.  **Environment Loading**: It will start by using `python-dotenv` to load environment variables from the root `.env` file. This includes the `MYSQL_DB` connection string and the `MCP_DB_SERVERPORT` for the server to listen on.
2.  **Lifespan Management**: We will implement a dedicated `lifespan` async context manager.
    -   **On Startup**: This manager will create an `async_engine` using SQLAlchemy's `create_async_engine` function and the MySQL connection string. It will then yield a dictionary containing this engine, making it available to the application as shared context.
    -   **On Shutdown**: The `finally` block of the manager will ensure the engine's resources are properly disposed of.
3.  **Application Initialization**: It will create an instance of the `EnrichMCP` application, passing the `lifespan` manager to its `lifespan` parameter.
4.  **Automatic Model Integration**: The most critical step will be to use the `include_sqlalchemy_models(app, Base)` function. This function will inspect all model classes in `models.py` that inherit from our `Base` and automatically generate the entire MCP API. It will create `get`, `list`, and `search` resources for each model and automatically create the resolvers for any defined `relationships`. This saves a significant amount of boilerplate code.
5.  **Runnable Server**: Finally, it will include the necessary code to run the application using `uvicorn`. The server will be configured to run on the host `0.0.0.0` and the port specified by the `MCP_DB_SERVERPORT` variable (defaulting to `8001`).

### `README.md` - Instructions

This file will provide clear, step-by-step instructions for developers on how to set up, configure, and run the database MCP server. This will include commands for installing dependencies from `requirements.txt` and starting the server with `uvicorn`.

## Future Customization

This architecture is designed for extension. While `include_sqlalchemy_models` provides a powerful baseline, we can incrementally add custom logic as needed. For example, if we need a highly specialized query for a specific relationship, we can write a manual resolver (`@User.orders.resolver`) for it. This new resolver will override the automatically generated one, allowing us to introduce complex business logic without having to rewrite the entire server.

## Actionable Steps

I will proceed with the implementation in the following order:

1.  **Create `requirements.txt`**: Add all the necessary dependencies.
2.  **Create `models.py`**: Define the initial SQLAlchemy models with placeholder `User` and `Order` classes.
3.  **Create `main.py`**: Implement the core application logic to connect to the database and serve the auto-generated API.
4.  **Create `README.md`**: Write the setup and usage instructions. 