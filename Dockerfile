# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements files first for better caching
COPY requirements.txt .
COPY mcp_servers/database_mcp_server/requirements.txt ./mcp_servers/database_mcp_server/

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r mcp_servers/database_mcp_server/requirements.txt

# Copy the entire project
COPY . .

# Create a startup script that can run different services
RUN echo '#!/bin/bash\n\
case "$1" in\n\
  "main")\n\
    echo "Starting main FastAPI backend..."\n\
    cd /app && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}\n\
    ;;\n\
  "db-mcp")\n\
    echo "Starting Database MCP Server..."\n\
    cd /app/mcp_servers/database_mcp_server && python main.py\n\
    ;;\n\
  *)\n\
    echo "Usage: $0 {main|db-mcp}"\n\
    echo "  main    - Start the main FastAPI backend"\n\
    echo "  db-mcp  - Start the Database MCP Server"\n\
    exit 1\n\
    ;;\n\
esac' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables with defaults
ENV PORT=8000
ENV MCP_DB_SERVERPORT=8001
ENV BACKEND_BASE_URL=http://localhost

# Expose both ports
EXPOSE 8000 8001

# Default command shows usage
CMD ["/app/start.sh"] 