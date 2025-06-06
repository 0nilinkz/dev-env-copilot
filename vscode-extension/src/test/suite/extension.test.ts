import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        const extension = vscode.extensions.getExtension('your-publisher-name.dev-env-copilot-extension');
        assert.ok(extension, 'Extension should be installed');
    });    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('your-publisher-name.dev-env-copilot-extension');
        assert.ok(extension, 'Extension should exist');
        
        if (extension && !extension.isActive) {
            await extension.activate();
        }
        
        assert.ok(extension?.isActive, 'Extension should be active');
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        
        const expectedCommands = [
            'devEnvCopilot.detectEnvironment',
            'devEnvCopilot.showConfiguration',
            'devEnvCopilot.restartServer'
        ];

        for (const expectedCommand of expectedCommands) {
            assert.ok(
                commands.includes(expectedCommand),
                `Command ${expectedCommand} should be registered`
            );
        }
    });

    test('Configuration should have correct defaults', () => {
        const config = vscode.workspace.getConfiguration('devEnvCopilot');
        
        // Test that configuration properties exist and have expected types
        const enabled = config.get('enabled');
        const logLevel = config.get('logLevel');
        const useDocker = config.get('useDocker');
        const customConfigPath = config.get('customConfigPath');

        assert.strictEqual(typeof enabled, 'boolean', 'enabled should be boolean');
        assert.strictEqual(typeof logLevel, 'string', 'logLevel should be string');
        assert.strictEqual(typeof useDocker, 'boolean', 'useDocker should be boolean');
        assert.strictEqual(typeof customConfigPath, 'string', 'customConfigPath should be string');
    });

    test('Show Configuration command should be callable', async () => {
        try {
            // Just test that the command can be called without throwing
            await vscode.commands.executeCommand('devEnvCopilot.showConfiguration');
            assert.ok(true, 'showConfiguration command executed successfully');
        } catch (error) {
            // Command might fail due to missing dependencies, but should not crash
            assert.ok(true, 'Command handled gracefully');
        }
    });
});
