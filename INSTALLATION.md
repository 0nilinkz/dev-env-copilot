# Installation Guide - Dev Environment Copilot

This MCP server can be installed and used in multiple ways to support different workflows and environments.

## 🚀 Quick Start

Choose your preferred installation method:

### 1. **NPM Installation** (Recommended for Node.js users)
```bash
# Install globally
npm install -g dev-env-copilot

# Or use without installing
npx dev-env-copilot

# Run the MCP server
dev-env-copilot
```

### 2. **Pip Installation** (Recommended for Python users)
```bash
# Install from PyPI
pip install dev-env-copilot

# Run the MCP server
python -m dev_environment_mcp.mcp_server
```

### 3. **Docker Installation** (Recommended for containerized environments)
```bash
# Pull and run from Docker Hub (when published)
docker run -i dev-env-copilot

# Or build locally
git clone https://github.com/0nilinkz/dev-env-copilot.git
cd dev-env-copilot
docker build -t dev-env-copilot .
docker run -i dev-env-copilot
```

---

## 📦 Detailed Installation Instructions

### NPM Installation

#### Global Installation
```bash
npm install -g dev-env-copilot
```

**Requirements:**
- Node.js 14+ 
- Python 3.8+

**Usage:**
```bash
# Run MCP server
dev-env-copilot

# With specific arguments
dev-env-copilot --debug

# Check version
dev-env-copilot --version
```

#### Local Project Installation
```bash
# Add to your project
npm install dev-env-copilot --save-dev

# Run via npx
npx dev-env-copilot

# Or via package.json scripts
# Add to package.json:
{
  "scripts": {
    "mcp-server": "dev-env-copilot"
  }
}
npm run mcp-server
```

### Pip Installation

#### From PyPI (when published)
```bash
# Install globally
pip install dev-env-copilot

# Or in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install dev-env-copilot
```

#### From Source
```bash
git clone https://github.com/0nilinkz/dev-env-copilot.git
cd dev-env-copilot
pip install -e .
```

**Usage:**
```bash
# Run MCP server
python -m dev_environment_mcp.mcp_server

# With arguments
python -m dev_environment_mcp.mcp_server --debug

# Or if installed globally
dev-env-copilot-server
```

### Docker Installation

#### Using Docker Run
```bash
# Pull from registry (when published)
docker pull dev-env-copilot

# Run MCP server
docker run -i dev-env-copilot

# With custom configuration
docker run -i -v "$(pwd)/config:/home/mcp-user/.config" dev-env-copilot
```

#### Using Docker Compose
```bash
git clone https://github.com/0nilinkz/dev-env-copilot.git
cd dev-env-copilot

# Run with docker-compose
docker-compose up dev-env-copilot

# For development
docker-compose --profile dev up dev-env-copilot-dev
```

#### Building from Source
```bash
git clone https://github.com/0nilinkz/dev-env-copilot.git
cd dev-env-copilot

# Build image
docker build -t dev-env-copilot .

# Run container
docker run -i dev-env-copilot

# Or with compose
docker-compose build
docker-compose up
```

---

## 🔧 MCP Client Configuration

### VS Code with Copilot

#### Method 1: Via Settings.json
Add to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot": {
        "command": "npx",
        "args": ["dev-env-copilot"],
        "env": {
          "NODE_ENV": "production"
        }
      }
    }
  }
}
```

#### Method 2: Via Tasks
Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "start-mcp-server",
      "type": "shell",
      "command": "npx",
      "args": ["dev-env-copilot"],
      "group": "build",
      "isBackground": true,
      "presentation": {
        "echo": false,
        "reveal": "never"
      }
    }
  ]
}
```

### Claude Desktop

Add to Claude Desktop config (`~/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dev-env-copilot": {
      "command": "npx",
      "args": ["dev-env-copilot"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### Other MCP Clients

For clients that support stdio transport:

```bash
# Command to run
npx dev-env-copilot

# Or with Python
python -m dev_environment_mcp.mcp_server

# Or with Docker
docker run -i dev-env-copilot
```

---

## 🛠️ Development Setup

### For Contributors

```bash
# Clone repository
git clone https://github.com/0nilinkz/dev-env-copilot.git
cd dev-env-copilot

# Install in development mode
pip install -e .

# Install npm dependencies for testing
npm install

# Run tests
python -m pytest tests/
npm test

# Build Docker image
docker build -t dev-env-copilot-dev .
```

### Testing MCP Server

```bash
# Test Python installation
python -c "import dev_environment_mcp; print('OK')"

# Test MCP server
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | python -m dev_environment_mcp.mcp_server

# Test npm wrapper
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | npx dev-env-copilot

# Test Docker
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | docker run -i dev-env-copilot
```

---

## 🚨 Troubleshooting

### Common Issues

#### Python Not Found (NPM)
```bash
# Error: No working Python installation found
# Solution: Install Python 3.8+ and ensure it's in PATH

# Windows
winget install python
# or download from python.org

# macOS
brew install python3

# Linux
sudo apt update && sudo apt install python3 python3-pip
```

#### Module Not Found (Pip)
```bash
# Error: ModuleNotFoundError: No module named 'dev_environment_mcp'
# Solution: Reinstall the package

pip uninstall dev-env-copilot
pip install dev-env-copilot

# Or install from source
pip install -e .
```

#### Docker Permission Issues
```bash
# Error: Permission denied
# Solution: Add user to docker group or use sudo

# Add user to docker group
sudo usermod -aG docker $USER
logout  # Then log back in

# Or run with sudo
sudo docker run -i dev-env-copilot
```

#### MCP Connection Issues
```bash
# Test MCP server manually
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | [your-command]

# Check server logs
[your-command] --debug

# Verify JSON-RPC format
[your-command] --test-mode
```

### Getting Help

- **GitHub Issues**: https://github.com/0nilinkz/dev-env-copilot/issues
- **Discussions**: https://github.com/0nilinkz/dev-env-copilot/discussions
- **Documentation**: https://github.com/0nilinkz/dev-env-copilot/blob/main/README.md

---

## 📋 Requirements Summary

| Method | Node.js | Python | Docker | Platform |
|--------|---------|--------|---------|----------|
| NPM    | 14+     | 3.8+   | No      | All      |
| Pip    | No      | 3.8+   | No      | All      |
| Docker | No      | No     | Yes     | All      |

All methods support Windows, macOS, and Linux.
