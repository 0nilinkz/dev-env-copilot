<div align="center">
  <img src="dev-env-copilot-mcp-logo.png" alt="Development Environment Copilot" width="200" height="200">
  
  # Dev Environment Copilot
  ## VS Code Extension
  
  **Intelligent environment detection and command syntax assistance for GitHub Copilot**
</div>

---

This VS Code extension provides seamless integration of the Dev Environment Copilot MCP server with GitHub Copilot Chat.

## Features

- 🤖 **Auto-configures GitHub Copilot Chat** with MCP integration
- 🔍 **Environment Detection** directly in VS Code
- ⚙️ **Flexible Configuration** - NPM or Docker deployment
- 📊 **Visual Environment Info** with webview panels
- 🔄 **Server Management** - start, stop, restart MCP server

## Quick Setup

1. Install the extension
2. The extension will prompt to configure GitHub Copilot Chat integration
3. Choose NPM (default) or Docker mode
4. Restart VS Code
5. Start chatting with enhanced environment awareness!

## Commands

- `Dev Env Copilot: Detect Environment` - Show current environment details
- `Dev Env Copilot: Show Configuration` - Display current settings
- `Dev Env Copilot: Restart MCP Server` - Restart the background server

## Configuration

Access settings via `File > Preferences > Settings > Dev Environment Copilot`:

- **Enable/Disable** the extension
- **Log Level** for debugging
- **Docker Mode** for containerized deployment
- **Custom Config Path** for advanced configuration

## Requirements

- VS Code 1.85.0 or higher
- Node.js 14+ (for NPM mode) or Docker (for container mode)
- GitHub Copilot Chat extension

## Installation Methods

The extension supports multiple deployment modes:

### NPM Mode (Default)
Uses `npx dev-env-copilot` - automatically installs if needed.

### Docker Mode
Uses `docker run dev-env-copilot` - requires Docker to be installed.

## Troubleshooting

If the extension doesn't work:

1. Check if GitHub Copilot Chat is installed and enabled
2. Restart VS Code after initial configuration
3. Check the Developer Console (`Help > Toggle Developer Tools`) for errors
4. Use `Dev Env Copilot: Restart MCP Server` command

## License

MIT License - see LICENSE file for details.
