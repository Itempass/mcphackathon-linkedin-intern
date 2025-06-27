.PHONY: start-dev-servers stop-dev-servers

DB_PID_FILE=.db_server.pid
AGENTLOGGER_PID_FILE=.agentlogger.pid

# This target starts the database, agentlogger UI, and API servers for development.
# The database and agentlogger servers run in the background, and their PIDs are stored.
# Assumes a .env file is present for configuration.
# When you stop the foreground process (Ctrl+C), run 'make stop-dev-servers' to stop the background servers.
start-dev-servers:
	@echo "Starting Database MCP Server in the background..."
	@python mcp_servers/database_mcp_server/main.py & echo $$! > $(DB_PID_FILE)
	@echo "Starting Agentlogger UI Server in the background..."
	@npm run dev --prefix agentlogger & echo $$! > $(AGENTLOGGER_PID_FILE)
	@echo "Waiting 2 seconds for servers to initialize..."
	@sleep 2
	@echo "Starting API Server in the foreground..."
	@python api/main.py

# This target stops the background database and agentlogger servers using the stored PIDs.
stop-dev-servers:
	@echo "Stopping Database MCP Server..."
	@if [ -f $(DB_PID_FILE) ]; then \
		kill `cat $(DB_PID_FILE)` && rm $(DB_PID_FILE); \
		echo "Server stopped."; \
	else \
		echo "PID file not found. Server may not be running or was stopped manually."; \
	fi
	@echo "Stopping Agentlogger UI Server..."
	@if [ -f $(AGENTLOGGER_PID_FILE) ]; then \
		kill -`cat $(AGENTLOGGER_PID_FILE)` && rm $(AGENTLOGGER_PID_FILE); \
		echo "Server stopped."; \
	else \
		echo "PID file not found. Server may not be running or was stopped manually."; \
	fi 