#!/usr/bin/env python3
"""
Development Environment MCP Server

A Model Context Protocol server for intelligent environment detection
and cross-platform development command assistance.
"""

import asyncio
import json
import sys
import os
import platform
import subprocess
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import anyio

# MCP Server implementation
@dataclass
class EnvironmentInfo:
    """Environment information structure"""
    os_type: str
    shell: str
    shell_syntax: str
    python_cmd: str
    node_cmd: str
    user: str
    home_dir: str
    workspace_dir: Optional[str] = None
    project_type: Optional[str] = None
    has_docker: bool = False
    has_git: bool = False

class EnvironmentDetector:
    """Detects development environment configuration"""
    
    def detect_environment(self, workspace_path: Optional[str] = None) -> EnvironmentInfo:
        """Detect current environment configuration"""
        os_type = platform.system().lower()
        
        # Detect shell and commands based on OS
        if os_type == 'windows':
            shell = 'powershell'
            shell_syntax = 'powershell'
            python_cmd = 'python'
            node_cmd = 'node'
            user = os.getenv('USERNAME', 'unknown')
            home_dir = os.getenv('USERPROFILE', '')
        else:  # Linux/macOS
            shell_env = os.getenv('SHELL', '/bin/bash')
            shell = os.path.basename(shell_env)
            shell_syntax = 'bash' if 'bash' in shell else shell
            python_cmd = 'python3'
            node_cmd = 'node'
            user = os.getenv('USER', 'unknown')
            home_dir = os.getenv('HOME', '')
        
        # Detect Docker and Git availability
        has_docker = self._command_exists('docker')
        has_git = self._command_exists('git')
        
        # Detect project type if workspace provided
        project_type = None
        if workspace_path and os.path.exists(workspace_path):
            project_type = self._detect_project_type(workspace_path)
        
        return EnvironmentInfo(
            os_type=os_type,
            shell=shell,
            shell_syntax=shell_syntax,
            python_cmd=python_cmd,
            node_cmd=node_cmd,
            user=user,            
            home_dir=home_dir,
            workspace_dir=workspace_path,
            project_type=project_type,
            has_docker=has_docker,
            has_git=has_git
        )
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            # Use 'where' on Windows, 'which' on Unix-like systems
            if platform.system().lower() == 'windows':
                result = subprocess.run(['where', command], 
                                      capture_output=True, 
                                      check=False, 
                                      timeout=2)
            else:
                result = subprocess.run(['which', command], 
                                      capture_output=True, 
                                      check=False, 
                                      timeout=2)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _detect_project_type(self, workspace_path: str) -> str:
        """Detect project type based on files in workspace"""
        path = Path(workspace_path)
        
        if (path / 'package.json').exists():
            return 'nodejs'
        elif (path / 'requirements.txt').exists() or (path / 'pyproject.toml').exists():
            return 'python'
        elif (path / 'Dockerfile').exists():
            return 'docker'
        elif (path / 'Cargo.toml').exists():
            return 'rust'
        elif (path / 'go.mod').exists():
            return 'go'
        else:
            return 'generic'

class CommandSyntaxProvider:
    """Provides cross-platform command syntax assistance"""
    
    def __init__(self, environment: EnvironmentInfo):
        self.env = environment
    
    def get_command_syntax(self, intent: str, options: Dict[str, Any] = None) -> Dict[str, str]:
        """Get platform-specific command syntax for a given intent"""
        options = options or {}
        
        commands = {
            'list_files': self._list_files_command(),
            'change_directory': self._change_directory_command(options.get('path', '.')),
            'create_directory': self._create_directory_command(options.get('path', 'newdir')),
            'copy_file': self._copy_file_command(options.get('source', 'file1'), options.get('dest', 'file2')),
            'move_file': self._move_file_command(options.get('source', 'file1'), options.get('dest', 'file2')),
            'delete_file': self._delete_file_command(options.get('path', 'file')),
            'view_file': self._view_file_command(options.get('path', 'file')),
            'edit_file': self._edit_file_command(options.get('path', 'file')),
            'find_files': self._find_files_command(options.get('pattern', '*')),
            'install_packages': self._install_packages_command(options.get('packages', [])),
            'run_tests': self._run_tests_command(),
            'start_server': self._start_server_command(),
            'docker_build': self._docker_build_command(),
            'git_status': self._git_status_command(),
        }
        
        if intent in commands:
            return commands[intent]
        else:
            return {'error': f'Unknown intent: {intent}'}
    
    def _list_files_command(self) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': 'Get-ChildItem',
                'cmd': 'dir',
                'description': 'List files and directories'
            }
        else:
            return {
                'bash': 'ls -la',
                'zsh': 'ls -la',
                'description': 'List files and directories with details'
            }
    
    def _change_directory_command(self, path: str) -> Dict[str, str]:
        return {
            'universal': f'cd "{path}"',
            'description': f'Change to directory: {path}'
        }
    
    def _create_directory_command(self, path: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'New-Item -ItemType Directory -Path "{path}"',
                'cmd': f'mkdir "{path}"',
                'description': f'Create directory: {path}'
            }
        else:
            return {
                'bash': f'mkdir -p "{path}"',
                'description': f'Create directory (with parents): {path}'
            }
    
    def _copy_file_command(self, source: str, dest: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'Copy-Item "{source}" "{dest}"',
                'cmd': f'copy "{source}" "{dest}"',
                'description': f'Copy {source} to {dest}'
            }
        else:
            return {
                'bash': f'cp "{source}" "{dest}"',
                'description': f'Copy {source} to {dest}'
            }
    
    def _move_file_command(self, source: str, dest: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'Move-Item "{source}" "{dest}"',
                'cmd': f'move "{source}" "{dest}"',
                'description': f'Move {source} to {dest}'
            }
        else:
            return {
                'bash': f'mv "{source}" "{dest}"',
                'description': f'Move {source} to {dest}'
            }
    
    def _delete_file_command(self, path: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'Remove-Item "{path}"',
                'cmd': f'del "{path}"',
                'description': f'Delete: {path}'
            }
        else:
            return {
                'bash': f'rm "{path}"',
                'description': f'Delete: {path}'
            }
    
    def _view_file_command(self, path: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'Get-Content "{path}"',
                'cmd': f'type "{path}"',
                'description': f'View file contents: {path}'
            }
        else:
            return {
                'bash': f'cat "{path}"',
                'description': f'View file contents: {path}'
            }
    
    def _edit_file_command(self, path: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'notepad "{path}"',
                'cmd': f'notepad "{path}"',
                'description': f'Edit file: {path}'
            }
        else:
            return {
                'bash': f'nano "{path}"',
                'vim': f'vim "{path}"',
                'description': f'Edit file: {path}'
            }
    
    def _find_files_command(self, pattern: str) -> Dict[str, str]:
        if self.env.os_type == 'windows':
            return {
                'powershell': f'Get-ChildItem -Recurse -Name "{pattern}"',
                'cmd': f'dir /s /b "{pattern}"',
                'description': f'Find files matching: {pattern}'
            }
        else:
            return {
                'bash': f'find . -name "{pattern}"',
                'description': f'Find files matching: {pattern}'
            }
    
    def _install_packages_command(self, packages: List[str]) -> Dict[str, str]:
        if not packages:
            packages = ['package-name']
        
        commands = {}
        
        if self.env.project_type == 'nodejs':
            pkg_list = ' '.join(packages)
            commands['npm'] = f'npm install {pkg_list}'
            commands['yarn'] = f'yarn add {pkg_list}'
        elif self.env.project_type == 'python':
            pkg_list = ' '.join(packages)
            commands['pip'] = f'{self.env.python_cmd} -m pip install {pkg_list}'
        
        commands['description'] = f'Install packages: {", ".join(packages)}'
        return commands
    
    def _run_tests_command(self) -> Dict[str, str]:
        commands = {}
        
        if self.env.project_type == 'nodejs':
            commands['npm'] = 'npm test'
            commands['yarn'] = 'yarn test'
        elif self.env.project_type == 'python':
            commands['pytest'] = 'pytest'
            commands['unittest'] = f'{self.env.python_cmd} -m unittest'
        
        commands['description'] = 'Run project tests'
        return commands
    
    def _start_server_command(self) -> Dict[str, str]:
        commands = {}
        
        if self.env.project_type == 'nodejs':
            commands['npm'] = 'npm start'
            commands['yarn'] = 'yarn start'
        elif self.env.project_type == 'python':
            commands['flask'] = 'flask run'
            commands['django'] = f'{self.env.python_cmd} manage.py runserver'
        
        commands['description'] = 'Start development server'
        return commands
    
    def _docker_build_command(self) -> Dict[str, str]:
        if self.env.has_docker:
            return {
                'docker': 'docker build -t myapp .',
                'docker-compose': 'docker-compose build',
                'description': 'Build Docker image'
            }
        else:
            return {
                'error': 'Docker not available',
                'description': 'Docker is not installed or not accessible'
            }
    
    def _git_status_command(self) -> Dict[str, str]:
        if self.env.has_git:
            return {
                'git': 'git status',
                'git-short': 'git status --short',
                'description': 'Check Git repository status'
            }
        else:
            return {
                'error': 'Git not available',
                'description': 'Git is not installed or not accessible'
            }

# MCP Server setup
app = Server("dev-env-copilot")

# Global instances
detector = EnvironmentDetector()

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="detect_environment",
            description="Detect current development environment configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_path": {
                        "type": "string",
                        "description": "Optional workspace path to analyze"
                    }
                }
            }
        ),
        Tool(
            name="get_command_syntax",
            description="Get platform-specific command syntax for development tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description": "The development task intent",
                        "enum": [
                            "list_files", "change_directory", "create_directory", 
                            "copy_file", "move_file", "delete_file", "view_file", 
                            "edit_file", "find_files", "install_packages", 
                            "run_tests", "start_server", "docker_build", "git_status"
                        ]
                    },
                    "options": {
                        "type": "object",
                        "description": "Additional options for the command (e.g., path, packages)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Optional workspace path for context"
                    }
                },
                "required": ["intent"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    if name == "detect_environment":
        workspace_path = arguments.get("workspace_path")
        env_info = detector.detect_environment(workspace_path)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(asdict(env_info), indent=2)
            )
        ]
    
    elif name == "get_command_syntax":
        intent = arguments.get("intent")
        options = arguments.get("options", {})
        workspace_path = arguments.get("workspace_path")
        
        # Get environment for context
        env_info = detector.detect_environment(workspace_path)
        
        # Get command syntax
        syntax_provider = CommandSyntaxProvider(env_info)
        commands = syntax_provider.get_command_syntax(intent, options)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(commands, indent=2)
            )
        ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    anyio.run(main)
