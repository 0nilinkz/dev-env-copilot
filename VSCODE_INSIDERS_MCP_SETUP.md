# Setting up Dev Environment Copilot MCP Server in VS Code Insiders

## Quick Setup

1. **Open VS Code Insiders settings**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Preferences: Open User Settings (JSON)"
   - Select it to open your `settings.json`

2. **Add MCP server configuration**:
   Add this to your `settings.json`:

```json
{
  "mcp.servers": {
    "dev-env-copilot": {
      "command": "node",
      "args": ["c:\\dev\\dev-env-copilot\\bin\\dev-env-copilot.js"],
      "env": {
        "PYTHONPATH": "c:\\dev\\dev-env-copilot\\src"
      }
    }
  }
}
```

3. **Alternative: Use the config file**:
   If VS Code supports loading MCP config from a file, you can reference:
   `c:\dev\dev-env-copilot\vscode-mcp-config.json`

## Tools Available

Once configured, you'll have access to these MCP tools:

- **`detect_environment`**: Analyzes your current development environment
- **`get_command_syntax`**: Provides cross-platform command syntax for various development tasks

## Testing the Setup

1. **Restart VS Code Insiders** after adding the configuration
2. **Open a Chat/Copilot session** 
3. **Try asking**: "What's my current development environment?"
4. The MCP server should provide detailed environment information

## Troubleshooting

- Make sure Node.js is installed and accessible
- Make sure Python 3.7+ is installed with the required packages (`mcp`, `anyio`, `pydantic`)
- Check the VS Code Insiders console for any error messages
- Verify the file paths in the configuration match your system

## What the MCP Server Provides

The server will automatically detect:
- Your operating system (Windows, Linux, macOS)
- Default shell and command syntax
- Available tools (Docker, Git, etc.)
- Project type (Node.js, Python, etc.)
- Appropriate commands for your platform

You can then ask Copilot for help with platform-specific commands, and it will use the MCP server to provide accurate syntax for your environment.
