# Using dev-env-copilot Docker Image with VS Code

This guide shows you how to configure VS Code to use your local `dev-env-copilot:latest` Docker image as an MCP server for GitHub Copilot.

## Prerequisites

1. **Docker Desktop** running on your system
2. **VS Code** with GitHub Copilot extension
3. **Local Docker image** built: `dev-env-copilot:latest`

## Build the Docker Image

First, ensure you have the Docker image built locally:

```bash
# In the dev-env-copilot directory
docker build -t dev-env-copilot:latest .

# Verify the image exists
docker images | grep dev-env-copilot
```

## VS Code Configuration Options

### Option 1: Workspace-Specific Settings (Recommended)

Create or update `.vscode/settings.json` in your project workspace:

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot-docker": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "--interactive",
          "--volume", "${workspaceFolder}:/workspace:ro",
          "dev-env-copilot:latest"
        ],
        "env": {
          "DOCKER_BUILDKIT": "1"
        },
        "initializationOptions": {
          "workspaceFolder": "/workspace"
        }
      }
    }
  }
}
```

### Option 2: Global Settings

Add to your global VS Code settings (Ctrl+Shift+P → "Preferences: Open Settings (JSON)"):

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot-global": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "--interactive",
          "--volume", "${workspaceFolder}:/workspace:ro",
          "dev-env-copilot:latest"
        ],
        "env": {
          "DOCKER_BUILDKIT": "1"
        }
      }
    }
  }
}
```

### Option 3: Docker Compose Integration

If you prefer using docker-compose:

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot-compose": {
        "command": "docker-compose",
        "args": [
          "-f", "${workspaceFolder}/../dev-env-copilot/docker-compose.yml",
          "run",
          "--rm",
          "--volume", "${workspaceFolder}:/workspace:ro",
          "dev-env-copilot"
        ]
      }
    }
  }
}
```

### Option 4: Persistent Container

For better performance, use a long-running container:

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot-persistent": {
        "command": "docker",
        "args": [
          "exec",
          "-i",
          "dev-env-copilot-server",
          "python",
          "-m", "dev_environment_mcp.server"
        ]
      }
    }
  }
}
```

First start the persistent container:
```bash
docker run -d --name dev-env-copilot-server -v "$(pwd):/workspace:ro" dev-env-copilot:latest tail -f /dev/null
```

## VS Code Tasks Integration

Create `.vscode/tasks.json` for easy Docker commands:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "docker-mcp-detect-environment",
      "type": "shell",
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive",
        "--volume", "${workspaceFolder}:/workspace:ro",
        "dev-env-copilot:latest",
        "detect_environment"
      ],
      "group": "build"
    },
    {
      "label": "docker-mcp-start-server",
      "type": "shell",
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive",
        "--name", "dev-env-copilot-server",
        "--volume", "${workspaceFolder}:/workspace:ro",
        "dev-env-copilot:latest"
      ],
      "isBackground": true
    }
  ]
}
```

Run tasks with: `Ctrl+Shift+P` → "Tasks: Run Task"

## Windows-Specific Configuration

For Windows users, add Windows-specific volume mounting:

```json
{
  "github.copilot.chat.experimental.mcp": {
    "enabled": true,
    "servers": {
      "dev-env-copilot-windows": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "--interactive",
          "--volume", "${workspaceFolder}:/workspace:ro",
          "--volume", "C:\\Users\\${env:USERNAME}\\AppData\\Local\\dev-env-copilot:/home/mcp-user/.config:ro",
          "dev-env-copilot:latest"
        ],
        "env": {
          "DOCKER_BUILDKIT": "1",
          "DOCKER_HOST": "npipe:////./pipe/docker_engine"
        }
      }
    }
  }
}
```

## Testing the Integration

1. **Restart VS Code** after adding the configuration
2. **Open Copilot Chat** (Ctrl+Shift+P → "GitHub Copilot: Open Chat")
3. **Test the MCP server**:
   ```
   @workspace Can you detect my environment and suggest the correct test command?
   ```

## Command Line Testing

You can also test the Docker MCP server directly:

```bash
# Interactive mode
docker run -it --rm -v "$(pwd):/workspace:ro" dev-env-copilot:latest

# One-off commands
docker run --rm -v "$(pwd):/workspace:ro" dev-env-copilot:latest detect_environment
docker run --rm -v "$(pwd):/workspace:ro" dev-env-copilot:latest get_command_syntax test
```

## Troubleshooting

### Docker Issues
- **Ensure Docker Desktop is running**
- **Verify image exists**: `docker images | grep dev-env-copilot`
- **Check Docker version**: `docker --version`

### VS Code Issues
- **Restart VS Code** after configuration changes
- **Check Copilot logs**: View → Output → GitHub Copilot
- **Verify MCP experimental features** are enabled

### Permission Issues
- **Volume mounting**: Ensure the workspace directory is accessible
- **Docker permissions**: On Linux, ensure user is in docker group

### Image Updates
When you update your MCP server code:
```bash
# Rebuild the image
docker build -t dev-env-copilot:latest .

# Restart VS Code to pick up changes
```

## Advanced Configuration

### Environment Variables
Pass environment variables to the container:

```json
{
  "env": {
    "DOCKER_BUILDKIT": "1",
    "MCP_DEBUG": "true",
    "WORKSPACE_PATH": "/workspace"
  }
}
```

### Custom Docker Registry
If using a private registry:

```json
{
  "args": [
    "run",
    "--rm",
    "--interactive",
    "your-registry.com/dev-env-copilot:latest"
  ]
}
```

### Network Configuration
For containers that need network access:

```json
{
  "args": [
    "run",
    "--rm",
    "--interactive",
    "--network", "host",
    "dev-env-copilot:latest"
  ]
}
```

## Performance Tips

1. **Use persistent containers** for frequent usage
2. **Mount only necessary directories** to reduce I/O
3. **Use Docker BuildKit** for faster builds
4. **Consider multi-stage builds** for smaller images
5. **Cache Docker layers** effectively

## Security Considerations

- **Read-only volumes**: Use `:ro` for workspace mounts
- **Minimal privileges**: Run containers with minimal permissions
- **No secrets in images**: Don't embed secrets in Docker images
- **Regular updates**: Keep base images updated

This configuration allows VS Code Copilot to seamlessly use your Docker-containerized MCP server for environment detection and command suggestions!
