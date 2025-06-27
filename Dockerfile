# Stage 1: Build the Next.js frontend
FROM node:20-slim as builder
ARG MYSQL_DB
ENV MYSQL_DB=$MYSQL_DB
WORKDIR /app/agentlogger
COPY agentlogger/package*.json ./
RUN npm install
COPY agentlogger ./
RUN npm run build

# Stage 2: Setup the Python backend and final image
FROM python:3.10-slim
WORKDIR /app

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy application code
COPY api ./api
COPY mcp_servers/database_mcp_server ./mcp_servers/database_mcp_server
COPY --from=builder /app/agentlogger /app/agentlogger

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports (only frontend will be published to host)
EXPOSE 3000
EXPOSE 8000
EXPOSE 8001

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 