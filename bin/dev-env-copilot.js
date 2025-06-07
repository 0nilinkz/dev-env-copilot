#!/usr/bin/env node

/**
 * Dev Environment Copilot MCP Server
 * Node.js wrapper for the Python MCP server
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Find Python executable
function findPython() {
    const pythonCommands = process.platform === 'win32' 
        ? ['python', 'python3', 'py'] 
        : ['python3', 'python'];
    
    for (const cmd of pythonCommands) {
        try {
            const result = require('child_process').execSync(`${cmd} --version`, { 
                encoding: 'utf8', 
                stdio: 'pipe' 
            });
            if (result.includes('Python')) {
                return cmd;
            }
        } catch (e) {
            // Continue to next command
        }
    }
    
    throw new Error('Python not found. Please install Python 3.7 or later.');
}

// Get the path to the Python server
function getServerPath() {
    // This script is in bin/, server is in src/dev_environment_mcp/
    const serverPath = path.join(__dirname, '..', 'src', 'dev_environment_mcp', 'server.py');
    
    if (!fs.existsSync(serverPath)) {
        throw new Error(`MCP server not found at: ${serverPath}`);
    }
    
    return serverPath;
}

async function main() {
    try {
        const python = findPython();
        const serverPath = getServerPath();
        
        console.error(`Starting Dev Environment Copilot MCP Server...`);
        console.error(`Python: ${python}`);
        console.error(`Server: ${serverPath}`);
          // Start the Python MCP server
        const serverProcess = spawn(python, [serverPath], {
            stdio: ['inherit', 'inherit', 'inherit'],
            env: {
                ...process.env,
                PYTHONPATH: path.join(__dirname, '..', 'src')
            }
        });
        
        // Handle process events
        serverProcess.on('error', (error) => {
            console.error(`Failed to start MCP server: ${error.message}`);
            process.exit(1);
        });
        
        serverProcess.on('close', (code) => {
            console.error(`MCP server exited with code ${code}`);
            process.exit(code || 0);
        });
        
        // Handle shutdown signals
        process.on('SIGINT', () => {
            console.error('Received SIGINT, shutting down...');
            serverProcess.kill('SIGINT');
        });
        
        process.on('SIGTERM', () => {
            console.error('Received SIGTERM, shutting down...');
            serverProcess.kill('SIGTERM');
        });
        
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error(`Unhandled error: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { main };
