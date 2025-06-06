import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

let mcpServerProcess: ChildProcess | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Dev Environment Copilot extension is now active!');

    // Auto-configure GitHub Copilot Chat MCP integration
    configureCopilotMCP(context);

    // Register commands
    const disposables = [
        vscode.commands.registerCommand('devEnvCopilot.detectEnvironment', detectEnvironment),
        vscode.commands.registerCommand('devEnvCopilot.showConfiguration', showConfiguration),
        vscode.commands.registerCommand('devEnvCopilot.restartServer', restartMCPServer)
    ];

    context.subscriptions.push(...disposables);

    // Start MCP server if enabled
    const config = vscode.workspace.getConfiguration('devEnvCopilot');
    if (config.get('enabled', true)) {
        startMCPServer(context);
    }
}

export function deactivate() {
    if (mcpServerProcess) {
        mcpServerProcess.kill();
        mcpServerProcess = null;
    }
}

async function configureCopilotMCP(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration();
    const mcpConfig = config.get('github.copilot.chat.experimental.mcp') as any;

    if (!mcpConfig || !mcpConfig.enabled) {
        const response = await vscode.window.showInformationMessage(
            'Dev Environment Copilot can enhance GitHub Copilot Chat with environment awareness. Configure now?',
            'Yes', 'No'
        );

        if (response === 'Yes') {
            const useDocker = vscode.workspace.getConfiguration('devEnvCopilot').get('useDocker', false);
            
            const newMcpConfig = {
                enabled: true,
                servers: {
                    'dev-env-copilot': useDocker ? {
                        command: 'docker',
                        args: ['run', '--rm', '--interactive', 'dev-env-copilot']
                    } : {
                        command: 'npx',
                        args: ['dev-env-copilot']
                    }
                }
            };

            await config.update('github.copilot.chat.experimental.mcp', newMcpConfig, vscode.ConfigurationTarget.Global);
            
            vscode.window.showInformationMessage(
                'GitHub Copilot Chat MCP integration configured! Restart VS Code to activate.'
            );
        }
    }
}

async function startMCPServer(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('devEnvCopilot');
    const useDocker = config.get('useDocker', false);
    const logLevel = config.get('logLevel', 'INFO');

    try {
        if (useDocker) {
            // Check if Docker is available
            const dockerCheck = spawn('docker', ['--version']);
            dockerCheck.on('error', () => {
                vscode.window.showErrorMessage('Docker not found. Please install Docker or disable the "useDocker" setting.');
                return;
            });

            mcpServerProcess = spawn('docker', ['run', '--rm', '--interactive', 'dev-env-copilot'], {
                env: { ...process.env, DEV_ENV_MCP_LOG_LEVEL: logLevel }
            });
        } else {
            // Use local installation
            const serverPath = path.join(context.extensionPath, '..', 'bin', 'dev-env-copilot.js');
            mcpServerProcess = spawn('node', [serverPath], {
                env: { ...process.env, DEV_ENV_MCP_LOG_LEVEL: logLevel }
            });
        }

        mcpServerProcess.on('error', (error) => {
            console.error('MCP Server error:', error);
            vscode.window.showErrorMessage(`Dev Environment Copilot MCP Server error: ${error.message}`);
        });

        mcpServerProcess.on('exit', (code) => {
            console.log(`MCP Server exited with code ${code}`);
            mcpServerProcess = null;
        });

        console.log('Dev Environment Copilot MCP Server started');
    } catch (error) {
        console.error('Failed to start MCP Server:', error);
        vscode.window.showErrorMessage(`Failed to start Dev Environment Copilot MCP Server: ${error}`);
    }
}

async function detectEnvironment() {
    const config = vscode.workspace.getConfiguration('devEnvCopilot');
    const useDocker = config.get('useDocker', false);

    try {
        const command = useDocker ? 'docker' : 'npx';
        const args = useDocker 
            ? ['run', '--rm', 'dev-env-copilot', 'detect-environment', '--format', 'json']
            : ['dev-env-copilot', 'detect-environment', '--format', 'json'];

        const process = spawn(command, args);
        let output = '';

        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        process.on('close', (code) => {
            if (code === 0) {
                try {
                    const envInfo = JSON.parse(output);
                    const panel = vscode.window.createWebviewPanel(
                        'devEnvInfo',
                        'Environment Information',
                        vscode.ViewColumn.One,
                        {}
                    );

                    panel.webview.html = generateEnvironmentHTML(envInfo);
                } catch (error) {
                    vscode.window.showErrorMessage('Failed to parse environment information');
                }
            } else {
                vscode.window.showErrorMessage('Failed to detect environment');
            }
        });
    } catch (error) {
        vscode.window.showErrorMessage(`Environment detection failed: ${error}`);
    }
}

async function showConfiguration() {
    const config = vscode.workspace.getConfiguration('devEnvCopilot');
    const configInfo = {
        enabled: config.get('enabled'),
        logLevel: config.get('logLevel'),
        useDocker: config.get('useDocker'),
        customConfigPath: config.get('customConfigPath')
    };

    const panel = vscode.window.createWebviewPanel(
        'devEnvConfig',
        'Dev Environment Copilot Configuration',
        vscode.ViewColumn.One,
        {}
    );

    panel.webview.html = generateConfigHTML(configInfo);
}

async function restartMCPServer() {
    if (mcpServerProcess) {
        mcpServerProcess.kill();
        mcpServerProcess = null;
    }

    // Wait a moment before restarting
    setTimeout(() => {
        const context = { extensionPath: '' } as vscode.ExtensionContext; // This would be passed properly
        startMCPServer(context);
        vscode.window.showInformationMessage('Dev Environment Copilot MCP Server restarted');
    }, 1000);
}

function generateEnvironmentHTML(envInfo: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Environment Information</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .info-group { margin-bottom: 20px; }
            .info-label { font-weight: bold; color: var(--vscode-textPreformat-foreground); }
            .info-value { margin-left: 10px; }
            pre { background: var(--vscode-textBlockQuote-background); padding: 10px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>🔍 Environment Detection Results</h1>
        <div class="info-group">
            <span class="info-label">Operating System:</span>
            <span class="info-value">${envInfo.os || 'Unknown'}</span>
        </div>
        <div class="info-group">
            <span class="info-label">Shell:</span>
            <span class="info-value">${envInfo.shell || 'Unknown'}</span>
        </div>
        <div class="info-group">
            <span class="info-label">Architecture:</span>
            <span class="info-value">${envInfo.architecture || 'Unknown'}</span>
        </div>
        <div class="info-group">
            <span class="info-label">Python Version:</span>
            <span class="info-value">${envInfo.python_version || 'Not detected'}</span>
        </div>
        <div class="info-group">
            <span class="info-label">Node.js Version:</span>
            <span class="info-value">${envInfo.node_version || 'Not detected'}</span>
        </div>
        <h2>📊 Full Environment Data</h2>
        <pre>${JSON.stringify(envInfo, null, 2)}</pre>
    </body>
    </html>`;
}

function generateConfigHTML(config: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configuration</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .config-item { margin-bottom: 15px; }
            .config-label { font-weight: bold; display: inline-block; width: 200px; }
            .config-value { color: var(--vscode-textLink-foreground); }
        </style>
    </head>
    <body>
        <h1>⚙️ Dev Environment Copilot Configuration</h1>
        <div class="config-item">
            <span class="config-label">Enabled:</span>
            <span class="config-value">${config.enabled ? '✅ Yes' : '❌ No'}</span>
        </div>
        <div class="config-item">
            <span class="config-label">Log Level:</span>
            <span class="config-value">${config.logLevel}</span>
        </div>
        <div class="config-item">
            <span class="config-label">Use Docker:</span>
            <span class="config-value">${config.useDocker ? '🐳 Yes' : '📦 No (NPM)'}</span>
        </div>
        <div class="config-item">
            <span class="config-label">Custom Config Path:</span>
            <span class="config-value">${config.customConfigPath || 'Default'}</span>
        </div>
        <p><em>You can modify these settings in VS Code Settings under "Dev Environment Copilot"</em></p>
    </body>
    </html>`;
}
