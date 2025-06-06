/**
 * Dev Environment Copilot MCP Server - NPM Wrapper (Debug Version)
 * 
 * This is a Node.js wrapper that launches the Python MCP server.
 * It handles cross-platform Python execution and argument forwarding.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Debug logging
function debug(msg) {
    console.error(`[DEBUG] ${msg}`);
}

debug('Wrapper starting...');

// Detect Python command
function getPythonCommand() {
    const isWindows = process.platform === 'win32';

    // Try different Python commands in order of preference
    const pythonCandidates = isWindows
        ? ['python', 'python3', 'py']
        : ['python3', 'python'];

    debug(`Platform: ${process.platform}, candidates: ${pythonCandidates.join(', ')}`);
    return pythonCandidates;
}

// Find the Python package
function findPythonPackage() {
    // First, try to find the installed package
    const packageDir = path.dirname(__dirname);
    const srcPath = path.join(packageDir, 'src', 'dev_environment_mcp', 'mcp_server.py');

    debug(`Looking for package at: ${srcPath}`);

    if (fs.existsSync(srcPath)) {
        debug('Found local package');
        return ['-m', 'dev_environment_mcp.mcp_server'];
    }

    debug('Using installed package fallback');
    // Fallback: try to run as installed package
    return ['-m', 'dev_environment_mcp.mcp_server'];
}

async function findWorkingPython() {
    const candidates = getPythonCommand();

    for (const cmd of candidates) {
        debug(`Trying Python command: ${cmd}`);
        try {
            const result = await new Promise((resolve, reject) => {
                const proc = spawn(cmd, ['--version'], {
                    stdio: ['ignore', 'pipe', 'pipe'],
                    timeout: 5000
                });

                let output = '';
                proc.stdout.on('data', (data) => {
                    output += data.toString();
                });

                proc.stderr.on('data', (data) => {
                    output += data.toString();
                });

                proc.on('close', (code) => {
                    debug(`${cmd} exited with code: ${code}, output: ${output.trim()}`);
                    if (code === 0) {
                        resolve({ cmd, output });
                    } else {
                        reject(new Error(`Exit code ${code}`));
                    }
                });

                proc.on('error', (err) => {
                    debug(`${cmd} error: ${err.message}`);
                    reject(err);
                });
            });

            if (result.output.includes('Python')) {
                debug(`Found working Python: ${result.cmd}`);
                return result.cmd;
            }
        } catch (err) {
            debug(`${cmd} failed: ${err.message}`);
            // Try next candidate
            continue;
        }
    }

    throw new Error('No working Python installation found. Please install Python 3.8+ and ensure it is in your PATH.');
}

async function main() {
    try {
        debug('Starting main function...');

        // Find working Python
        const pythonCmd = await findWorkingPython();
        debug(`Using Python: ${pythonCmd}`);

        // Get package arguments
        const packageArgs = findPythonPackage();
        debug(`Package args: ${packageArgs.join(' ')}`);

        // Forward all arguments to Python
        const args = [...packageArgs, ...process.argv.slice(2)];
        debug(`Final args: ${args.join(' ')}`);

        debug(`Launching: ${pythonCmd} ${args.join(' ')}`);

        // Spawn Python process with stdio inheritance
        const pythonProcess = spawn(pythonCmd, args, {
            stdio: 'inherit',
            env: {
                ...process.env,
                PYTHONUNBUFFERED: '1',
            }
        });

        debug('Python process started');

        // Handle process events
        pythonProcess.on('error', (err) => {
            debug(`Failed to start Python process: ${err.message}`);
            console.error(`Failed to start Python process: ${err.message}`);
            process.exit(1);
        });

        pythonProcess.on('close', (code) => {
            debug(`Python process exited with code: ${code}`);
            process.exit(code || 0);
        });

        // Handle Ctrl+C gracefully
        process.on('SIGINT', () => {
            debug('Received SIGINT, killing Python process');
            pythonProcess.kill('SIGINT');
        });

        process.on('SIGTERM', () => {
            debug('Received SIGTERM, killing Python process');
            pythonProcess.kill('SIGTERM');
        });

    } catch (err) {
        debug(`Error in main: ${err.message}`);
        console.error(`Error: ${err.message}`);
        console.error('\nTroubleshooting:');
        console.error('1. Ensure Python 3.8+ is installed and in your PATH');
        console.error('2. Try running: pip install dev-env-copilot');
        console.error('3. For manual installation: cd to this directory and run: pip install -e .');
        process.exit(1);
    }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    debug(`Unhandled Rejection: ${reason}`);
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

if (require.main === module) {
    debug('Running as main module');
    main();
} else {
    debug('Loaded as module');
}
