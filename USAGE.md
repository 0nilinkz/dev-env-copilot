# Development Environment MCP Package

## Installation Methods

### Method 1: PyPI Installation (Coming Soon)

```bash
pip install dev-environment-mcp
```

### Method 2: Direct GitHub Installation

```bash
pip install git+https://github.com/yourusername/dev-environment-mcp.git
```

### Method 3: Local Development Installation

```bash
git clone https://github.com/yourusername/dev-environment-mcp.git
cd dev-environment-mcp
pip install -e .
```

## VS Code Integration

### Option 1: MCP Server Configuration

Add to your VS Code settings (`.vscode/settings.json`):

```json
{
  "mcp.servers": {
    "dev-environment": {
      "command": "dev-env-mcp",
      "args": ["--mcp-mode", "--transport", "stdio"],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Option 2: Task-Based Integration

Add to your project's `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "detect-environment",
      "type": "shell",
      "command": "dev-env-mcp",
      "args": ["detect-environment", "--format", "summary"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false
      }
    },
    {
      "label": "get-test-command",
      "type": "shell", 
      "command": "dev-env-mcp",
      "args": ["get-command-syntax", "--operation", "test", "--format", "shell"],
      "group": "test"
    }
  ]
}
```

### Option 3: Manual Commands

Use directly in VS Code terminal:

```bash
# Detect environment
dev-env-mcp detect-environment --format summary

# Get command syntax
dev-env-mcp get-command-syntax --operation test --format shell

# Run as MCP server
dev-env-mcp --mcp-mode --transport http --port 8080
```

## Standalone Usage

The tool works independently of VS Code:

```bash
# Environment detection
dev-env-mcp detect-environment --format json
dev-env-mcp detect-environment --format summary
dev-env-mcp detect-environment --format copilot

# Command syntax help
dev-env-mcp get-command-syntax --operation test --target local
dev-env-mcp get-command-syntax --operation deploy --target pi --format explanation

# MCP server modes
dev-env-mcp --mcp-mode --transport stdio
dev-env-mcp --mcp-mode --transport http --host 0.0.0.0 --port 9000
```

## Configuration

### Environment Variables

- `DEV_ENV_MCP_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARN, ERROR)
- `DEV_ENV_MCP_CACHE_TTL`: Cache duration for environment detection (seconds)

### Custom Configuration File

Create `~/.config/dev-env-mcp/config.json`:

```json
{
  "detection": {
    "cache_ttl": 300,
    "enable_hardware_detection": true,
    "custom_project_roots": [
      "/custom/dev/path",
      "c:\\custom\\dev\\path"
    ]
  },
  "commands": {
    "custom_operations": {
      "my-test": {
        "windows": "npm test",
        "linux": "npm test",
        "pi": "sudo npm test"
      }
    }
  },
  "logging": {
    "level": "INFO",
    "file": "~/.local/logs/dev-env-mcp.log"
  }
}
```

## Integration Examples

### GitHub Copilot Chat

When using Copilot Chat in VS Code, the MCP server provides context:

```
User: "Run the tests"
Copilot: (uses MCP to detect Windows) "python -m pytest test/"

User: "Set PYTHONPATH environment variable"  
Copilot: (detects PowerShell) "$env:PYTHONPATH = 'c:\dev\project'"
```

### Terminal Command Generation

The tool adapts commands to your environment:

```bash
# On Windows (PowerShell)
$ dev-env-mcp get-command-syntax --operation test
python -m pytest test/

# On Linux (Bash)
$ dev-env-mcp get-command-syntax --operation test  
python3 -m pytest test/

# On Raspberry Pi
$ dev-env-mcp get-command-syntax --operation test --target pi
sudo python3 -m pytest test/
```

## API Reference

### Command Line Interface

```
dev-env-mcp [OPTIONS] [COMMAND]

Options:
  --version              Show version
  --mcp-mode            Run as MCP server
  --transport stdio|http Transport for MCP mode
  --host HOST           Host for HTTP transport
  --port PORT           Port for HTTP transport  
  --log-level LEVEL     Logging level

Commands:
  detect-environment    Detect current environment
  get-command-syntax    Get command syntax for operation
```

### MCP Tools

When running as an MCP server, exposes these tools:

- `detect_environment(format="json|summary|copilot")`: Environment detection
- `get_command_syntax(operation, target="local", format="shell")`: Command syntax
- `format_command(template, variables)`: Template formatting
- `get_project_context(include_files=false, analyze_dependencies=true)`: Project analysis

## Troubleshooting

### Common Issues

**1. Command not found after installation**
```bash
# Check if installed correctly
pip show dev-environment-mcp

# Try with full python path
python -m dev_environment_mcp.server --version
```

**2. MCP server not responding**
```bash
# Test standalone mode first
dev-env-mcp detect-environment

# Check logs
dev-env-mcp --mcp-mode --log-level DEBUG
```

**3. VS Code integration not working**
- Verify VS Code has MCP support enabled
- Check the `.vscode/settings.json` configuration
- Try task-based integration as fallback

### Debug Mode

Enable detailed logging:

```bash
export DEV_ENV_MCP_LOG_LEVEL=DEBUG  # Linux/macOS
$env:DEV_ENV_MCP_LOG_LEVEL = "DEBUG"  # Windows

dev-env-mcp detect-environment --format summary
```

## Contributing

See the main repository for contribution guidelines and development setup.
