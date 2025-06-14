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

# Create a startup script that runs the combined app
RUN echo '#!/bin/bash\n\
echo "Starting combined FastAPI + MCP server on port 8000..."\n\
cd /app && uvicorn src.main:app --host 0.0.0.0 --port 8000' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables with defaults
ENV PORT=8000
ENV MCP_DB_SERVERPORT=8001
ENV BACKEND_BASE_URL=http://localhost

# Expose single port
EXPOSE 8000

# Start both services
CMD ["/app/start.sh"] 