# Global Context Injection Feature

## Overview

The Dev Environment Copilot extension now includes advanced **Global Context Injection** capabilities that allow you to:

1. **Inject environment context** into all Copilot prompts automatically
2. **Add custom global instructions** that apply to every Copilot interaction  
3. **Create a unified chat participant** that enhances prompts with contextual information
4. **Configure context inclusion** on a per-type basis (environment, workspace, etc.)

## Features

### 🌍 Global Chat Participant

The extension registers a custom chat participant `@devEnvGlobalContext` that you can use in GitHub Copilot Chat to get enhanced responses with automatic context injection.

**Usage:**
```
@devEnvGlobalContext What's the best way to install dependencies in my current environment?
```

### ⚙️ Configuration Options

All global context features are configurable through VS Code settings:

```json
{
  "devEnvCopilot.globalContext.enabled": false,
  "devEnvCopilot.globalContext.instructions": "",
  "devEnvCopilot.globalContext.includeEnvironment": true,
  "devEnvCopilot.globalContext.includeWorkspace": true
}
```

### 🎯 Available Commands

The extension provides several commands accessible via the Command Palette:

- **Dev Env Copilot: Toggle Global Context Injection** - Enable/disable global context
- **Dev Env Copilot: Update Global Instructions** - Set custom instructions for all prompts
- **Dev Env Copilot: Show Global Context Status** - View current configuration and cached context

## How It Works

### Context Injection Process

1. **Environment Detection**: Automatically detects your OS, shell, architecture, Python/Node.js versions
2. **Context Caching**: Caches environment information for 5 minutes to avoid repeated detection
3. **Prompt Enhancement**: When you interact with `@devEnvGlobalContext`, your prompt is enhanced with:
   - Environment information (OS, shell, versions)
   - Workspace context (project name, path)
   - Your custom global instructions
   - The original user query

### Example Enhanced Prompt

Original prompt:
```
How do I install pandas?
```

Enhanced prompt sent to Copilot:
```
**Environment Context:**
- OS: Windows 11
- Shell: PowerShell 7.4.0
- Architecture: x64
- Python: 3.11.7
- Node.js: 20.10.0

**Workspace Context:**
- Root: my-data-project
- Path: C:\dev\my-data-project

**Global Instructions:**
Always consider cross-platform compatibility when suggesting commands

**User Query:** How do I install pandas?
```

## Setup and Usage

### 1. Enable Global Context

Use the Command Palette:
```
> Dev Env Copilot: Toggle Global Context Injection
```

Or configure in settings:
```json
{
  "devEnvCopilot.globalContext.enabled": true
}
```

### 2. Set Global Instructions (Optional)

Use the Command Palette:
```
> Dev Env Copilot: Update Global Instructions
```

Or configure in settings:
```json
{
  "devEnvCopilot.globalContext.instructions": "Always provide cross-platform solutions when possible. Prefer npm over yarn for Node.js projects."
}
```

### 3. Use the Chat Participant

In GitHub Copilot Chat, type:
```
@devEnvGlobalContext [your question]
```

### 4. Monitor Status

Check your current configuration:
```
> Dev Env Copilot: Show Global Context Status
```

This opens a detailed view showing:
- Current configuration status
- Your global instructions
- Cached environment context
- Last update timestamp
- Usage instructions

## Advanced Configuration

### Fine-tune Context Inclusion

You can control what information gets included:

```json
{
  "devEnvCopilot.globalContext.includeEnvironment": true,  // OS, shell, versions
  "devEnvCopilot.globalContext.includeWorkspace": true     // Project info
}
```

### Custom Instructions Examples

**Cross-platform focus:**
```
"Always consider cross-platform compatibility. Provide commands for Windows (PowerShell), macOS, and Linux when applicable."
```

**Security-conscious:**
```
"Always suggest secure coding practices. Warn about potential security issues. Prefer official packages and avoid deprecated dependencies."
```

**Team standards:**
```
"Follow our team's coding standards: use TypeScript for new JavaScript projects, prefer functional programming patterns, include comprehensive error handling."
```

## Technical Implementation

### Chat Participant Registration

The extension registers a VS Code Chat Participant that:
- Intercepts chat requests
- Enhances prompts with contextual information
- Uses the VS Code Language Model API to send enhanced requests
- Returns formatted responses with injected context

### Context Caching

- Environment information is cached for 5 minutes
- Cache is automatically refreshed when stale
- Failed environment detection gracefully degrades functionality

### Error Handling

- Graceful fallbacks when environment detection fails
- Clear error messages when Language Model API is unavailable
- Non-blocking operation - doesn't interfere with normal Copilot usage

## Limitations and Considerations

1. **Requires GitHub Copilot**: The feature depends on GitHub Copilot being available and enabled
2. **Context Length**: Large context injections may hit token limits in some scenarios
3. **Performance**: First use may be slower while environment context is detected
4. **Scope**: Currently works through the chat participant interface, not automatic injection into all Copilot interactions

## Future Enhancements

Potential future improvements could include:

1. **Automatic Prompt Interception**: Hook into all Copilot prompts automatically (not just chat participant)
2. **Project-specific Context**: Include relevant files, dependencies, and project structure
3. **Dynamic Context**: Real-time context based on current file/selection
4. **Context Templates**: Pre-defined context templates for different project types
5. **Team Sharing**: Share global instructions across team members

## Troubleshooting

### Chat Participant Not Available

1. Ensure the extension is installed and enabled
2. Restart VS Code after enabling global context
3. Check that GitHub Copilot extension is active

### Environment Context Not Loading

1. Verify that the dev-env-copilot CLI is installed (`npm install -g dev-env-copilot`)
2. Check extension logs in VS Code Developer Tools
3. Try toggling Docker mode if using containerized setup

### Language Model Errors

1. Ensure GitHub Copilot subscription is active
2. Check GitHub Copilot extension status
3. Try signing out and back into GitHub Copilot

---

This global context injection feature represents a significant enhancement to the dev-env-copilot extension, providing intelligent context awareness for all your Copilot interactions!
