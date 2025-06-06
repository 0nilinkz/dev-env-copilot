# Change Log

## [1.0.0] - 2025-06-06

### Added
- Initial release of Dev Environment Copilot VS Code extension
- Auto-configuration of GitHub Copilot Chat MCP integration
- Environment detection with visual webview display
- Support for both NPM and Docker deployment modes
- Configuration management through VS Code settings
- MCP server lifecycle management (start, stop, restart)
- Cross-platform support (Windows, macOS, Linux)

### Features
- **Auto MCP Setup**: Automatically configures GitHub Copilot Chat integration
- **Environment Detection**: Real-time environment analysis and display
- **Flexible Deployment**: Choose between NPM or Docker modes
- **Visual Configuration**: Webview-based configuration and status display
- **Server Management**: Built-in MCP server lifecycle controls

### Commands
- `devEnvCopilot.detectEnvironment`: Show environment detection results
- `devEnvCopilot.showConfiguration`: Display current extension configuration  
- `devEnvCopilot.restartServer`: Restart the MCP server process

### Configuration Options
- `devEnvCopilot.enabled`: Enable/disable the extension
- `devEnvCopilot.logLevel`: Set logging level (DEBUG, INFO, WARN, ERROR)
- `devEnvCopilot.useDocker`: Use Docker instead of NPM for deployment
- `devEnvCopilot.customConfigPath`: Path to custom configuration file
