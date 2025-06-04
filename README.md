# Development Environment MCP Server

A Model Context Protocol (MCP) server that provides intelligent environment detection and command syntax assistance for cross-platform development workflows.

## Features

- **Automatic Environment Detection**: Detects Windows, Linux, macOS, and Raspberry Pi environments
- **Shell-Aware Command Syntax**: Provides correct terminal command syntax for PowerShell, Bash, Zsh
- **VS Code Integration**: Seamless integration with GitHub Copilot and VS Code tasks
- **Cross-Platform**: Works across Windows, Linux, and macOS development environments
- **Extensible**: Easy to extend with new tools and environment detection logic

## Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install dev-environment-mcp

# Or install from source
git clone https://github.com/yourusername/dev-environment-mcp.git
cd dev-environment-mcp
pip install -e .
```

### Standalone Usage

```bash
# Run as standalone script
dev-env-mcp --help

# Get environment summary
dev-env-mcp detect-environment --format summary

# Get command syntax for specific operation
dev-env-mcp get-command-syntax --operation test --format shell
```

### MCP Server Mode

```bash
# Run as MCP server (stdio transport)
dev-env-mcp --mcp-mode

# Run as HTTP server
dev-env-mcp --mcp-mode --transport http --port 8080
```

## VS Code Integration

### Method 1: Direct MCP Integration

Add to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "dev-environment": {
      "command": "dev-env-mcp",
      "args": ["--mcp-mode"],
      "transport": "stdio"
    }
  }
}
```

### Method 2: Task Integration

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "detect-environment",
      "type": "shell",
      "command": "dev-env-mcp",
      "args": ["detect-environment", "--format", "copilot"],
      "group": "build"
    }
  ]
}
```

### Method 3: Extension Integration

Install the companion VS Code extension:

1. Open VS Code Extensions (`Ctrl+Shift+X`)
2. Search for "Development Environment MCP"
3. Install and reload VS Code

## Copilot Integration

The server provides context-aware assistance for:

- **Terminal Commands**: Automatically formats commands for your OS/shell
- **Environment Variables**: Correct syntax for setting env vars
- **File Operations**: Platform-appropriate file manipulation commands
- **Development Workflows**: Context-aware suggestions for common dev tasks

### Example Usage with Copilot

```
User: "Run the tests"
Copilot: (detects Windows PowerShell) "python -m pytest test/"

User: "Run the tests" 
Copilot: (detects Linux) "python3 -m pytest test/"

User: "Set environment variable"
Copilot: (Windows) "$env:PYTHONPATH = 'c:\dev\project'"
Copilot: (Linux) "export PYTHONPATH=/home/user/project"
```

## Available Tools

The MCP server exposes these tools:

### `detect_environment`
Detects current OS, shell, hardware, and provides environment context.

**Parameters:**
- `format` (string): Output format - "json", "summary", "copilot"

### `get_command_syntax`
Provides correct command syntax for the current environment.

**Parameters:**
- `operation` (string): Operation type - "test", "build", "deploy", "install"
- `target` (string, optional): Target environment - "local", "remote", "pi"
- `format` (string): Output format - "shell", "explanation", "examples"

### `format_command`
Formats a generic command for the current environment.

**Parameters:**
- `command_template` (string): Template command with placeholders
- `variables` (object): Variables to substitute in template

### `get_project_context`
Analyzes current project structure and provides relevant context.

**Parameters:**
- `include_files` (boolean): Include file listing in output
- `analyze_dependencies` (boolean): Analyze package.json/requirements.txt

## Configuration

### Environment Variables

- `DEV_ENV_MCP_CONFIG`: Path to custom configuration file
- `DEV_ENV_MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARN, ERROR)
- `DEV_ENV_MCP_CACHE_TTL`: Cache TTL for environment detection (seconds)

### Custom Configuration

Create a `dev-env-mcp.json` config file:

```json
{
  "detection": {
    "cache_ttl": 300,
    "enable_hardware_detection": true,
    "custom_environments": {
      "my-docker": {
        "detect_command": "cat /.dockerenv",
        "shell": "bash",
        "python_cmd": "python3"
      }
    }
  },
  "commands": {
    "custom_operations": {
      "my-build": {
        "windows": "msbuild /p:Configuration=Release",
        "linux": "make build",
        "macos": "xcodebuild -configuration Release"
      }
    }
  }
}
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/yourusername/dev-environment-mcp.git
cd dev-environment-mcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest test/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Model Context Protocol](https://github.com/modelcontextprotocol/specification) - Official MCP specification
- [VS Code MCP Extension](https://marketplace.visualstudio.com/items?itemName=modelcontextprotocol.mcp) - VS Code MCP support
- [GitHub Copilot](https://github.com/features/copilot) - AI pair programmer integration

## Support

- 📚 [Documentation](https://github.com/yourusername/dev-environment-mcp/wiki)
- 🐛 [Issue Tracker](https://github.com/yourusername/dev-environment-mcp/issues)
- 💬 [Discussions](https://github.com/yourusername/dev-environment-mcp/discussions)
