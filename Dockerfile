# Stage 1: Build the Next.js frontend
FROM node:18-slim as builder
ARG MYSQL_DATABASE
ENV MYSQL_DATABASE=$MYSQL_DATABASE
ARG SQLITE_DB_PATH
ENV SQLITE_DB_PATH=$SQLITE_DB_PATH
WORKDIR /app/agentlogger
COPY agentlogger/package*.json ./
RUN npm install
COPY agentlogger ./
COPY data ./data
RUN npm run build

# Stage 2: Setup the Python backend and final image
FROM python:3.10-slim
ARG OPENROUTER_API_KEY
ARG MYSQL_DATABASE
ENV MYSQL_DATABASE=$MYSQL_DATABASE
ENV OPENROUTER_API_KEY=$OPENROUTER_API_KEY
ENV PYTHONPATH="/app"
WORKDIR /app

# Install supervisor and nodejs
RUN apt-get update && apt-get install -y supervisor nodejs npm

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY api ./api
COPY shared ./shared
COPY data ./data
COPY mcp_servers/database_mcp_server ./mcp_servers/database_mcp_server
COPY --from=builder /app/agentlogger /app/agentlogger

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports (only frontend will be published to host)
EXPOSE 3000
EXPOSE 8000
EXPOSE 8001

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 