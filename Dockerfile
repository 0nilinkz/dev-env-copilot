# Dev Environment Copilot MCP Server - Docker Image
FROM python:3.11-slim

# Set metadata
LABEL org.opencontainers.image.title="Dev Environment Copilot MCP Server"
LABEL org.opencontainers.image.description="MCP Server for intelligent environment detection and command syntax assistance"
LABEL org.opencontainers.image.source="https://github.com/0nilinkz/dev-env-copilot"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements first (for better Docker layer caching)
COPY requirements.txt ./
COPY pyproject.toml ./
COPY setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY README.md LICENSE ./

# Install the package in development mode
RUN pip install -e .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash mcp-user
USER mcp-user
WORKDIR /home/mcp-user

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import dev_environment_mcp; print('OK')" || exit 1

# Default command - run the MCP server
CMD ["python", "-m", "dev_environment_mcp"]

# Expose no ports (MCP server uses stdio)
# Volume for configuration (optional)
VOLUME ["/home/mcp-user/.config"]

# Usage:
# Build: docker build -t dev-env-copilot .
# Run: docker run -i dev-env-copilot
# With config: docker run -i -v "$(pwd)/config:/home/mcp-user/.config" dev-env-copilot
