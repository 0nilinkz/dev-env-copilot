# Docker MCP Server Setup for VS Code

## Quick Setup

1. **Build the Docker image** (if not already done):
   ```bash
   docker build -t dev-env-copilot-test .
   ```

2. **Add to your `.vscode/settings.json`**:
   ```json
   {
     "github.copilot.chat.experimental.mcp": {
       "enabled": true,
       "servers": {
         "dev-env-copilot": {
           "command": "docker",
           "args": ["run", "-i", "--rm", "dev-env-copilot-test"],
           "transport": "stdio"
         }
       }
     }
   }
   ```

3. **Restart VS Code** to load the new MCP server configuration

4. **Test in Copilot Chat**:
   - Open Copilot Chat (`Ctrl+Shift+I`)
   - Type: `@dev-env-copilot detect my environment`
   - The Docker MCP server should respond with environment details

## Advanced Configuration

See the `examples/` directory for more configuration options:
- `vscode_docker_windows.json` - Windows-specific settings
- `vscode_docker_volume.json` - With workspace volume mounting
- `vscode_tasks_docker.json` - Task-based Docker management

## Troubleshooting

- **MCP server not found**: Ensure the Docker image is built locally
- **Permission issues**: Make sure Docker Desktop is running
- **No response**: Check VS Code Developer Tools Console for MCP errors
