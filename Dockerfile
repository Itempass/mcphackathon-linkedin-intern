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

# Create a startup script that runs both services in parallel
RUN echo '#!/bin/bash\n\
echo "Starting Database MCP Server in background..."\n\
cd /app/mcp_servers/database_mcp_server && python main.py &\n\
\n\
echo "Starting main FastAPI backend..."\n\
cd /app && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} &\n\
\n\
# Wait for all background processes\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables with defaults
ENV PORT=8000
ENV MCP_DB_SERVERPORT=8001
ENV BACKEND_BASE_URL=http://localhost

# Expose both ports
EXPOSE 8000 8001

# Start both services
CMD ["/app/start.sh"] 