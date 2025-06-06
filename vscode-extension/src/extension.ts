import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import * as os from 'os';

let mcpServerProcess: ChildProcess | null = null;
let devenvChatParticipant: vscode.ChatParticipant | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('Dev Environment Copilot extension is now active!');

    // Auto-configure GitHub Copilot Chat MCP integration
    configureCopilotMCP(context);

    // Register @devenv chat participant
    registerDevenvChatParticipant(context);

    // Register commands
    const disposables = [
        vscode.commands.registerCommand('devEnvCopilot.detectEnvironment', detectEnvironment),
        vscode.commands.registerCommand('devEnvCopilot.showConfiguration', showConfiguration),
        vscode.commands.registerCommand('devEnvCopilot.restartServer', restartMCPServer),
        vscode.commands.registerCommand('devEnvCopilot.updateCopilotInstructions', updateCopilotInstructions)
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

async function registerDevenvChatParticipant(context: vscode.ExtensionContext) {
    try {
        devenvChatParticipant = vscode.chat.createChatParticipant('devEnvCopilot.devenv', handleDevenvChatRequest);
        devenvChatParticipant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');
        devenvChatParticipant.followupProvider = {
            provideFollowups: async (result: vscode.ChatResult, context: vscode.ChatContext, token: vscode.CancellationToken) => {
                return [{
                    prompt: '@devenv /show',
                    label: '🔍 Show Environment Info',
                    command: 'show'
                }, {
                    prompt: '@devenv /update',
                    label: '📝 Update Instructions File', 
                    command: 'update'
                }];
            }
        };

        context.subscriptions.push(devenvChatParticipant);
        console.log('@devenv chat participant registered successfully');
    } catch (error) {
        console.error('Failed to register @devenv chat participant:', error);
    }
}

async function handleDevenvChatRequest(
    request: vscode.ChatRequest,
    context: vscode.ChatContext,
    stream: vscode.ChatResponseStream,
    token: vscode.CancellationToken
): Promise<vscode.ChatResult> {
    try {
        // Handle different commands
        if (request.command === 'update') {
            await handleUpdateCommand(stream, token);
        } else if (request.command === 'show') {
            await handleShowCommand(stream, token);
        } else {
            // Default behavior - update the instructions file
            await handleUpdateCommand(stream, token);
        }

        return { metadata: { command: request.command || 'update' } };
    } catch (error) {
        console.error('@devenv chat request error:', error);
        stream.markdown(`❌ Sorry, there was an error: ${error}`);
        return { metadata: { command: request.command || 'error' } };
    }
}

async function handleUpdateCommand(stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
    stream.progress('🔍 Detecting environment...');
    
    // Get environment information
    const envInfo = await detectEnvironmentInfo();
    
    if (!envInfo) {
        stream.markdown('❌ Failed to detect environment information.');
        return;
    }

    stream.progress('📝 Writing to .vscode/copilot-instructions.md...');
    
    // Generate token-efficient instructions
    const instructions = generateTokenEfficientInstructions(envInfo);
    
    // Write to .vscode/copilot-instructions.md
    const success = await writeCopilotInstructions(instructions);
    
    if (success) {
        stream.markdown('✅ **Environment context written to `.vscode/copilot-instructions.md`**\n\n');
        stream.markdown('This file will now automatically provide context for all Copilot interactions in this workspace.\n\n');
        
        // Show the generated content
        stream.markdown('**Generated content:**\n');
        stream.markdown('```markdown\n' + instructions + '\n```');
        
        stream.button({
            command: 'vscode.open',
            title: 'Open copilot-instructions.md',
            arguments: [vscode.Uri.file(path.join(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '', '.vscode', 'copilot-instructions.md'))]
        });
    } else {
        stream.markdown('❌ Failed to write to `.vscode/copilot-instructions.md`. Make sure you have a workspace open.');
    }
}

async function handleShowCommand(stream: vscode.ChatResponseStream, token: vscode.CancellationToken) {
    stream.progress('🔍 Detecting environment...');
    
    const envInfo = await detectEnvironmentInfo();
    
    if (!envInfo) {
        stream.markdown('❌ Failed to detect environment information.');
        return;
    }

    stream.markdown('## 🔍 Current Environment\n\n');
    stream.markdown(`**OS:** ${envInfo.os || 'Unknown'}\n`);
    stream.markdown(`**Shell:** ${envInfo.shell || 'Unknown'}\n`);
    stream.markdown(`**Architecture:** ${envInfo.architecture || 'Unknown'}\n`);
    
    if (envInfo.python_version) {
        stream.markdown(`**Python:** ${envInfo.python_version}\n`);
    }
    if (envInfo.node_version) {
        stream.markdown(`**Node.js:** ${envInfo.node_version}\n`);
    }
    
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (workspaceFolder) {
        stream.markdown(`**Workspace:** ${workspaceFolder.name}\n`);
    }

    // Check if copilot-instructions.md exists
    const instructionsPath = path.join(workspaceFolder?.uri.fsPath || '', '.vscode', 'copilot-instructions.md');
    if (fs.existsSync(instructionsPath)) {
        stream.markdown('\n✅ `.vscode/copilot-instructions.md` exists and is providing context to Copilot.');
        stream.button({
            command: 'vscode.open',
            title: 'Open copilot-instructions.md',
            arguments: [vscode.Uri.file(instructionsPath)]
        });
    } else {
        stream.markdown('\n⚠️ `.vscode/copilot-instructions.md` not found. Use `/update` to create it.');
    }
}

async function detectEnvironmentInfo(): Promise<any> {
    try {
        const config = vscode.workspace.getConfiguration('devEnvCopilot');
        const useDocker = config.get('useDocker', false);

        // Try external command first
        if (await tryExternalEnvironmentDetection(useDocker)) {
            return await tryExternalEnvironmentDetection(useDocker);
        }
        
        // Fallback to built-in detection
        return await detectEnvironmentFallback();
    } catch (error) {
        console.error('Failed to detect environment:', error);
        return await detectEnvironmentFallback();
    }
}

async function tryExternalEnvironmentDetection(useDocker: boolean): Promise<any> {
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

        return new Promise<any>((resolve, reject) => {
            const timeout = setTimeout(() => {
                process.kill();
                reject(new Error('External detection timeout'));
            }, 5000);

            process.on('close', (code) => {
                clearTimeout(timeout);
                if (code === 0 && output.trim()) {
                    try {
                        const envInfo = JSON.parse(output);
                        resolve(envInfo);
                    } catch (error) {
                        reject(error);
                    }
                } else {
                    reject(new Error(`External detection failed with code ${code}`));
                }
            });
        });
    } catch (error) {
        throw error;
    }
}

async function detectEnvironmentFallback(): Promise<any> {
    const envInfo: any = {
        os: os.platform(),
        architecture: os.arch(),
        shell: process.env.SHELL || process.env.ComSpec || 'unknown',
        node_version: process.version,
        timestamp: new Date().toISOString()
    };

    // Detect OS-specific info
    switch (os.platform()) {
        case 'win32':
            envInfo.os = `Windows ${os.release()}`;
            envInfo.shell = process.env.ComSpec?.includes('powershell') ? 'PowerShell' : 
                          process.env.ComSpec?.includes('cmd') ? 'Command Prompt' : 
                          'PowerShell'; // Default assumption for VS Code integrated terminal
            break;
        case 'darwin':
            envInfo.os = `macOS ${os.release()}`;
            break;
        case 'linux':
            envInfo.os = `Linux ${os.release()}`;
            break;
    }

    // Try to detect Python version
    try {
        const pythonVersion = await getCommandOutput('python --version');
        if (pythonVersion) {
            envInfo.python_version = pythonVersion.replace('Python ', '').trim();
        }
    } catch {
        try {
            const python3Version = await getCommandOutput('python3 --version');
            if (python3Version) {
                envInfo.python_version = python3Version.replace('Python ', '').trim();
            }
        } catch {
            // Python not available
        }
    }

    // Try to detect additional tools
    try {
        const gitVersion = await getCommandOutput('git --version');
        if (gitVersion) {
            envInfo.git_version = gitVersion.replace('git version ', '').trim();
        }
    } catch {
        // Git not available
    }

    return envInfo;
}

async function getCommandOutput(command: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const [cmd, ...args] = command.split(' ');
        const process = spawn(cmd, args, { shell: true });
        let output = '';

        process.stdout.on('data', (data) => {
            output += data.toString();
        });

        const timeout = setTimeout(() => {
            process.kill();
            reject(new Error('Command timeout'));
        }, 3000);

        process.on('close', (code) => {
            clearTimeout(timeout);
            if (code === 0) {
                resolve(output.trim());
            } else {
                reject(new Error(`Command failed with code ${code}`));
            }
        });
    });
}

async function detectEnvironment() {
    const envInfo = await detectEnvironmentInfo();
    
    if (envInfo) {
        const panel = vscode.window.createWebviewPanel(
            'devEnvInfo',
            'Environment Information',
            vscode.ViewColumn.One,
            {}
        );

        panel.webview.html = generateEnvironmentHTML(envInfo);
    } else {
        vscode.window.showErrorMessage('Failed to detect environment');
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

async function updateCopilotInstructions() {
    const envInfo = await detectEnvironmentInfo();
    
    if (!envInfo) {
        vscode.window.showErrorMessage('Failed to detect environment information');
        return;
    }

    const instructions = generateTokenEfficientInstructions(envInfo);
    const success = await writeCopilotInstructions(instructions);
    
    if (success) {
        vscode.window.showInformationMessage('✅ Updated .vscode/copilot-instructions.md with current environment context');
    } else {
        vscode.window.showErrorMessage('❌ Failed to update copilot-instructions.md');
    }
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

function generateTokenEfficientInstructions(envInfo: any): string {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    
    let instructions = '# Development Environment Context\n\n';
    
    // Core environment info - very concise
    instructions += `**Environment:** ${envInfo.os} ${envInfo.architecture} | ${envInfo.shell}\n`;
    
    // Runtime versions - only if detected
    const runtimes = [];
    if (envInfo.python_version) runtimes.push(`Python ${envInfo.python_version}`);
    if (envInfo.node_version) runtimes.push(`Node.js ${envInfo.node_version}`);
    if (runtimes.length > 0) {
        instructions += `**Runtimes:** ${runtimes.join(', ')}\n`;
    }
    
    // Workspace info
    if (workspaceFolder) {
        instructions += `**Project:** ${workspaceFolder.name}\n`;
    }
    
    instructions += '\n**Instructions:**\n';
    instructions += '- Provide commands compatible with the detected environment\n';
    instructions += '- Use appropriate shell syntax for the detected shell\n';
    instructions += '- Consider cross-platform compatibility when relevant\n';
    
    // OS-specific hints
    if (envInfo.os?.toLowerCase().includes('windows')) {
        instructions += '- Use PowerShell syntax for Windows commands\n';
        instructions += '- Use backslashes for Windows paths when appropriate\n';
    } else if (envInfo.os?.toLowerCase().includes('mac')) {
        instructions += '- Use macOS-specific commands and paths when appropriate\n';
    } else if (envInfo.os?.toLowerCase().includes('linux')) {
        instructions += '- Use Linux-specific commands and package managers when appropriate\n';
    }
    
    instructions += `\n*Auto-generated by Dev Environment Copilot on ${new Date().toISOString().split('T')[0]}*`;
    
    return instructions;
}

async function writeCopilotInstructions(instructions: string): Promise<boolean> {
    try {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return false;
        }

        const vscodeDir = path.join(workspaceFolder.uri.fsPath, '.vscode');
        const instructionsPath = path.join(vscodeDir, 'copilot-instructions.md');

        // Create .vscode directory if it doesn't exist
        if (!fs.existsSync(vscodeDir)) {
            fs.mkdirSync(vscodeDir, { recursive: true });
        }

        // Write the instructions file
        fs.writeFileSync(instructionsPath, instructions, 'utf8');
        
        return true;
    } catch (error) {
        console.error('Failed to write copilot-instructions.md:', error);
        return false;
    }
}
