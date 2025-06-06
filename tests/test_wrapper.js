// Quick test of the wrapper functionality
const { spawn } = require('child_process');

console.log('Testing Node.js wrapper...');

const proc = spawn('node', ['bin/dev-env-copilot.js', '--version'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    timeout: 5000
});

proc.stdout.on('data', (data) => {
    console.log('STDOUT:', data.toString());
});

proc.stderr.on('data', (data) => {
    console.log('STDERR:', data.toString());
});

proc.on('close', (code) => {
    console.log(`Process exited with code: ${code}`);
});

proc.on('error', (err) => {
    console.log('Error:', err.message);
});

// Kill after 3 seconds
setTimeout(() => {
    console.log('Killing process after timeout...');
    proc.kill();
}, 3000);
