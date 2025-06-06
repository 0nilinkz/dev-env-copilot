# MCP Integration Examples

This directory contains configuration examples for integrating the Dev Environment Copilot MCP server with various clients.

## VS Code Integration

### Method 1: VS Code Settings (Experimental MCP Support)

Add to your `.vscode/settings.json`:

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

### Method 2: VS Code Tasks

Add to your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "start-dev-env-copilot",
      "type": "shell",
      "command": "npx",
      "args": ["dev-env-copilot"],
      "group": "build",
      "isBackground": true,
      "presentation": {
        "echo": false,
        "reveal": "never",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "test-dev-env-copilot",
      "type": "shell",
      "command": "echo",
      "args": [
        "{\"jsonrpc\": \"2.0\", \"method\": \"tools/list\", \"id\": 1}"
      ],
      "options": {
        "shell": {
          "executable": "powershell.exe",
          "args": ["-Command", "echo '{\"jsonrpc\": \"2.0\", \"method\": \"tools/list\", \"id\": 1}' | npx dev-env-copilot"]
        }
      },
      "group": "test"
    }
  ]
}
```

## Claude Desktop Integration

Add to your Claude Desktop config file (`%APPDATA%/Claude/claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "dev-env-copilot": {
      "command": "npx",
      "args": ["dev-env-copilot"]
    }
  }
}
```

Alternative with Python:
```json
{
  "mcpServers": {
    "dev-env-copilot": {
      "command": "python",
      "args": ["-m", "dev_environment_mcp.mcp_server"]
    }
  }
}
```

Alternative with Docker:
```json
{
  "mcpServers": {
    "dev-env-copilot": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "dev-env-copilot"]
    }
  }
}
```

## Generic MCP Client Integration

For any MCP client that supports stdio transport:

### NPM Installation
```bash
npx dev-env-copilot
```

### Pip Installation
```bash
python -m dev_environment_mcp.mcp_server
```

### Docker Installation
```bash
docker run -i dev-env-copilot
```

## Testing Your Integration

Test the MCP server with a simple JSON-RPC request:

### Windows PowerShell
```powershell
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | npx dev-env-copilot
```

### Bash/Zsh
```bash
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | npx dev-env-copilot
```

### Expected Response
You should see a JSON response listing available tools like:
- `detect_environment`
- `get_command_syntax`
- `get_shell_commands`

## Troubleshooting

1. **Python not found**: Ensure Python 3.8+ is installed and in PATH
2. **Module not found**: Run `pip install dev-env-copilot`
3. **Permission denied**: Try `pip install --user dev-env-copilot`
4. **Docker issues**: Ensure Docker is running and user has permissions

## Environment Variables

You can customize behavior with environment variables:

```bash
# Enable debug mode
DEBUG=1 npx dev-env-copilot

# Set custom config path
DEV_ENV_CONFIG_PATH=/path/to/config.json npx dev-env-copilot
```
