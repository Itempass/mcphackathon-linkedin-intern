# FeatureForm's MCP Hackathon - LinkedIn AI Assistant

This project was created for a hackathon. As such, it's more of a proof-of-concept than a fully functional application. We're proud to have won third place!

## What it does

At a high level, this project is a browser plugin that assists users in responding to LinkedIn messages.

- A browser plugin watches the LinkedIn HTML for new messages.
- When a new message is detected, the message and conversation history are sent to a backend server.
- The backend uses an AI model to generate a draft reply.
- The draft reply is then displayed to the user in the plugin.

**note on Vector DB & Semantic Search**: The original goal was to implement a vector db so we could do semantic search on old LinkedIn messages to reply in a similar way (eg. you already answered that question in another chat -> the Agent would find it and reply in the same way). I unfortunately broke this implementation during refactoring, so I removed it for now.

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

## Installation
### 1. Set Environment Variables
- Rename `.env.example` to `.env`
- Change `OPENROUTER_API_KEY` and `OPENAI_API_KEY` to your keys

**note**: `OPENAI_API_KEY` is not actually being used, but is still required by the code to start up. This was part of the semantic search logic (see note in [What it does](#what-it-does)).

### 2. Build plugin
- navigate to `plugin` directory (`cd plugin`)
- install frontend stuff `npm install`
- build frontend `npm run build`
- this will output the plugin code into the `plugin/dist` directory
- now navigate in Chrome to `chrome://extensions/`
- enable Developer Mode (top right)
- Click Load Unpacked (top left)
- Select the `dist` folder

### 3. Start backend
- navigate to the root directory of this project
- `docker-compose up`

**note** make sure that you have Docker installed!

### 4. Try out the plugin
- open the plugin in Chrome by clicking the plugin icon
- refresh LinkedIn

**note** in the UI, you will see 3 'interns' you can choose from. Only Alex works. It was a hackathon, creating buttons that don't actually do anything is part of it ;) 