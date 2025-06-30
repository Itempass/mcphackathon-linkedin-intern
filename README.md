# LinkedIn AI Assistant

This project was created for a hackathon. As such, it's more of a proof-of-concept than a fully functional application. We're proud to have won third place!

## What it does

At a high level, this project is a browser plugin that assists users in responding to LinkedIn messages.

- A browser plugin watches the LinkedIn HTML for new messages.
- When a new message is detected, the message and conversation history are sent to a backend server.
- The backend uses an AI model to generate a draft reply.
- The draft reply is then displayed to the user in the plugin.

**note**: The original goal was to implement a vector db so we could do semantic search on old LinkedIn messages to reply in a similar way (eg. you already answered that question in another chat -> the Agent would find it and reply in the same way). I unfortunately broke this implementation during refactoring, so I removed it for now.

## Project Structure

The project is a monorepo containing several components:

- `plugin/`: A browser extension that injects itself into LinkedIn.
- `api/`: A Python-based backend using FastAPI that receives messages from the plugin and interacts with an AI model.
- `agentlogger/`: A Next.js application for viewing agent logs and traces.
- `mcp_servers/database_mcp_server`: Provides an interface for the agent to the database containing LinkedIn messages.
- `shared/`: Shared Python code used by different backend components.
- `data/`: Contains the SQLite database and other data.
- `documentation/`: Documentation for the project.
- `tests/`: Contains small test scripts for the backend API and services, not fully automated tests.
- `Dockerfile`, `docker-compose.yml`: Files for building and running the application using Docker.
- `supervisord.conf`: Configuration for process management.

