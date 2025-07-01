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

### 1. Clone the repository
- Copy the repository url (`https://github.com/Itempass/mcphackathon-linkedin-intern.git`)
- Go to your terminal
- Navigate to the folder where you want to clone the project (eg. `cd Downloads` or `cd Documents`)
- Type `git clone https://github.com/Itempass/mcphackathon-linkedin-intern.git`

### 2. Set Environment Variables
- Navigate into the directory you just cloned using `cd mcphackathon-linkedin-intern`
- Rename `.env.example` to `.env` (on Mac: `cp .env.example .env` | on Windows: `copy .env.example .env`)
- Open the `.env` file to edit using `nano .env`
- Change `OPENROUTER_API_KEY` to your key. **Important:** navigate with your arrow keys.
- Use `ctrl + x` to save your changes

**im
**note**: `OPENAI_API_KEY` is not actually being used, so you can leave the placeholder value.

### 3. Build plugin
- navigate to the `plugin` directory (`cd plugin` in your current terminal)
- install frontend stuff using `npm install`
- build frontend using `npm run build`
- this will output the plugin code into the `plugin/dist` directory

### 4. Build the project and start the backend
- navigate up one level back into the root of the project using `cd ..`
- in the same directory, type `docker-compose up` to start building

**note:** make sure that you have Docker installed! If you haven't, read [the installation guide](https://docs.docker.com/engine/install/).


### 5. Try out the plugin
- now navigate in Chrome to `chrome://extensions/`
- enable Developer Mode (top right)
- Click Load Unpacked (top left)
- Select the `plugin/dist` folder
- open the plugin in Chrome by clicking the plugin icon
- refresh LinkedIn (**after** you have opened the plugin sidebar -> yep still buggy ;))
- hire 'Alex' as an intern and follow his instructions
- **VERY IMPORTANT:**: the plugin only works for messages opened through the message interface at the top of LinkedIn. It does not work for messages that are overlaid on your timeline. 

**note:** in the UI, you will see 3 'interns' you can choose from. Only Alex works. It was a hackathon, creating buttons that don't actually do anything is part of it ;) 
**note:** the AI is pretty slow atm, it can take a minute untill drafts start appearing.