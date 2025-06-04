"""
Tests for the Development Environment MCP Server
"""

import pytest
import json
from unittest.mock import patch, mock_open
from pathlib import Path

from dev_environment_mcp.server import (
    EnvironmentDetector,
    CommandSyntaxProvider,
    EnvironmentMCPServer,
    standalone_detect_environment,
    standalone_get_command_syntax
)


class TestEnvironmentDetector:
    """Test environment detection functionality"""
    
    def test_detect_environment_windows(self):
        """Test Windows environment detection"""
        with patch('platform.system', return_value='Windows'), \
             patch('os.getenv') as mock_getenv:
            
            mock_getenv.side_effect = lambda key, default=None: {
                'USERNAME': 'testuser',
                'USERPROFILE': 'c:\\Users\\testuser'
            }.get(key, default)
            
            detector = EnvironmentDetector()
            env = detector.detect_environment()
            
            assert env.os_type == 'windows'
            assert env.shell == 'powershell'
            assert env.shell_syntax == 'powershell'
            assert env.python_cmd == 'python'
            assert env.user == 'testuser'
    
    def test_detect_environment_linux(self):
        """Test Linux environment detection"""
        with patch('platform.system', return_value='Linux'), \
             patch('os.getenv') as mock_getenv:
            
            mock_getenv.side_effect = lambda key, default=None: {
                'USER': 'testuser',
                'HOME': '/home/testuser',
                'SHELL': '/bin/bash'
            }.get(key, default)
            
            detector = EnvironmentDetector()
            env = detector.detect_environment()
            
            assert env.os_type == 'linux'
            assert env.shell == 'bash'
            assert env.shell_syntax == 'bash'
            assert env.python_cmd == 'python3'
            assert env.user == 'testuser'
    
    def test_detect_raspberry_pi(self):
        """Test Raspberry Pi detection"""
        mock_cpuinfo = "processor\t: 0\nmodel name\t: ARMv6-compatible processor rev 7 (v6l)\nBogoMIPS\t: 697.95\nFeatures\t: half thumb fastmult vfp edsp java tls\nCPU implementer\t: 0x41\nCPU architecture: 7\nCPU variant\t: 0x0\nCPU part\t: 0xb76\nCPU revision\t: 7\n\nHardware\t: BCM2835\nRevision\t: 000e\nSerial\t\t: 0000000012345678\nModel\t\t: Raspberry Pi Model B Rev 2"
        
        with patch('builtins.open', mock_open(read_data=mock_cpuinfo)):
            detector = EnvironmentDetector()
            assert detector._detect_raspberry_pi() == True
    
    def test_detect_container(self):
        """Test container detection"""
        # Test Docker detection
        with patch('os.path.exists', return_value=True):
            detector = EnvironmentDetector()
            assert detector._detect_container() == True
        
        # Test cgroup-based detection
        mock_cgroup = "11:blkio:/docker/1234567890abcdef\n10:memory:/docker/1234567890abcdef"
        with patch('os.path.exists', return_value=False), \
             patch('builtins.open', mock_open(read_data=mock_cgroup)):
            detector = EnvironmentDetector()
            assert detector._detect_container() == True


class TestCommandSyntaxProvider:
    """Test command syntax generation"""
    
    def test_get_command_syntax_windows(self):
        """Test command syntax for Windows"""
        with patch('platform.system', return_value='Windows'):
            detector = EnvironmentDetector()
            provider = CommandSyntaxProvider(detector)
            
            cmd_syntax = provider.get_command_syntax('test')
            assert 'python -m pytest' in cmd_syntax.shell_command
            assert cmd_syntax.environment.startswith('windows/')
    
    def test_get_command_syntax_linux(self):
        """Test command syntax for Linux"""
        with patch('platform.system', return_value='Linux'):
            detector = EnvironmentDetector()
            provider = CommandSyntaxProvider(detector)
            
            cmd_syntax = provider.get_command_syntax('test')
            assert 'python3 -m pytest' in cmd_syntax.shell_command
            assert cmd_syntax.environment.startswith('linux/')
    
    def test_format_command(self):
        """Test command template formatting"""
        with patch('platform.system', return_value='Linux'):
            detector = EnvironmentDetector()
            provider = CommandSyntaxProvider(detector)
            
            template = "{python_cmd} -m pytest {test_path}"
            variables = {"test_path": "test/unit/"}
            
            result = provider.format_command(template, variables)
            assert 'python3 -m pytest test/unit/' in result
    
    def test_unknown_operation(self):
        """Test handling of unknown operations"""
        detector = EnvironmentDetector()
        provider = CommandSyntaxProvider(detector)
        
        with pytest.raises(ValueError, match="Unknown operation"):
            provider.get_command_syntax('unknown_operation')


class TestStandaloneFunctions:
    """Test standalone function interfaces"""
    
    def test_standalone_detect_environment_json(self):
        """Test standalone environment detection with JSON format"""
        result = standalone_detect_environment('json')
        data = json.loads(result)
        
        assert 'os_type' in data
        assert 'shell' in data
        assert 'python_cmd' in data
    
    def test_standalone_detect_environment_summary(self):
        """Test standalone environment detection with summary format"""
        result = standalone_detect_environment('summary')
        
        assert 'Environment Summary:' in result
        assert 'OS:' in result
        assert 'Shell:' in result
        assert 'Python:' in result
    
    def test_standalone_detect_environment_copilot(self):
        """Test standalone environment detection with Copilot format"""
        result = standalone_detect_environment('copilot')
        data = json.loads(result)
        
        assert 'environment' in data
        assert 'commands' in data
        assert 'paths' in data
        assert 'examples' in data
    
    def test_standalone_get_command_syntax(self):
        """Test standalone command syntax generation"""
        result = standalone_get_command_syntax('test')
        
        # Should return a shell command
        assert 'pytest' in result
    
    def test_standalone_get_command_syntax_with_explanation(self):
        """Test standalone command syntax with explanation format"""
        result = standalone_get_command_syntax('test', format_type='explanation')
        
        assert 'Operation:' in result
        assert 'Command:' in result
        assert 'Explanation:' in result
    
    def test_standalone_get_command_syntax_unknown_operation(self):
        """Test standalone command syntax with unknown operation"""
        result = standalone_get_command_syntax('unknown_operation')
        
        assert result.startswith('Error:')


class TestEnvironmentMCPServer:
    """Test MCP server functionality"""
    
    @pytest.fixture
    def server(self):
        """Create an MCP server instance for testing"""
        return EnvironmentMCPServer("test-server")
    
    def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server.server.name == "test-server"
        assert server.detector is not None
        assert server.command_provider is not None
        assert server.logger is not None
    
    def test_format_environment_summary(self, server):
        """Test environment summary formatting"""
        # Mock environment data
        from dev_environment_mcp.server import EnvironmentInfo
        
        env = EnvironmentInfo(
            os_type='linux',
            shell='bash',
            shell_syntax='bash',
            python_cmd='python3',
            is_raspberry_pi=False,
            is_container=False,
            project_root='/home/user/project',
            architecture='x86_64',
            python_version='3.9.0',
            working_directory='/home/user/project',
            user='testuser',
            home_directory='/home/testuser'
        )
        
        summary = server._format_environment_summary(env)
        
        assert 'Environment Summary:' in summary
        assert 'OS: Linux' in summary
        assert 'Shell: bash' in summary
        assert 'Python: python3' in summary
    
    def test_format_copilot_context(self, server):
        """Test Copilot context formatting"""
        from dev_environment_mcp.server import EnvironmentInfo
        
        env = EnvironmentInfo(
            os_type='windows',
            shell='powershell',
            shell_syntax='powershell',
            python_cmd='python',
            is_raspberry_pi=False,
            is_container=False,
            project_root='c:\\dev\\project',
            architecture='AMD64',
            python_version='3.10.0',
            working_directory='c:\\dev\\project',
            user='testuser',
            home_directory='c:\\Users\\testuser'
        )
        
        context = server._format_copilot_context(env)
        
        assert context['environment']['os'] == 'windows'
        assert context['environment']['shell'] == 'powershell'
        assert context['commands']['python'] == 'python'
        assert context['commands']['separator'] == ';'
        assert 'examples' in context


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the full system"""
    
    def test_full_workflow_windows(self):
        """Test full workflow on Windows"""
        with patch('platform.system', return_value='Windows'):
            # Test environment detection
            env_result = standalone_detect_environment('summary')
            assert 'Windows' in env_result
            
            # Test command syntax
            cmd_result = standalone_get_command_syntax('test')
            assert 'python -m pytest' in cmd_result
    
    def test_full_workflow_linux(self):
        """Test full workflow on Linux"""
        with patch('platform.system', return_value='Linux'):
            # Test environment detection
            env_result = standalone_detect_environment('summary')
            assert 'Linux' in env_result
            
            # Test command syntax
            cmd_result = standalone_get_command_syntax('test')
            assert 'python3 -m pytest' in cmd_result
    
    def test_server_tools_registration(self):
        """Test that MCP server properly registers all tools"""
        server = EnvironmentMCPServer("test-server")
        
        # Check that tools are registered
        expected_tools = [
            'detect_environment',
            'get_command_syntax', 
            'format_command',
            'get_project_context'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in server.server.tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
