#!/usr/bin/env python3
"""
Development Environment MCP Server

A Model Context Protocol server that provides intelligent environment detection
and command syntax assistance for cross-platform development workflows.
"""

import json
import os
import platform
import sys
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import subprocess
import asyncio
from dataclasses import dataclass, asdict

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP SDK not available. Install with: pip install mcp")
    sys.exit(1)

# Initialize FastMCP server
mcp = FastMCP("dev-environment-copilot")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dev-env-copilot.log')
    ]
)
logger = logging.getLogger("dev-environment-mcp")


@dataclass
class EnvironmentInfo:
    """Environment detection results"""
    os_type: str
    shell: str
    shell_syntax: str
    python_cmd: str
    is_raspberry_pi: bool
    is_container: bool
    project_root: Optional[str]
    architecture: str
    python_version: str
    working_directory: str
    user: str
    home_directory: str


class EnvironmentDetector:
    """Core environment detection logic"""
    
    def __init__(self):
        self.cache = {}
        
    def detect_environment(self) -> EnvironmentInfo:
        """Detect current environment"""
        os_type = platform.system().lower()
        architecture = platform.machine()
        python_version = platform.python_version()
        working_directory = os.getcwd()
        user = os.getenv("USER", os.getenv("USERNAME", "unknown"))
        home_directory = os.getenv("HOME", os.getenv("USERPROFILE", ""))
        
        # Default values
        shell = "unknown"
        shell_syntax = "bash"
        python_cmd = "python3"
        project_root = None
        
        # OS-specific detection
        if os_type == "windows":
            shell = "powershell"
            shell_syntax = "powershell"
            python_cmd = "python"
            project_root = self._detect_windows_project_root()
        elif os_type in ["linux", "darwin"]:
            shell = os.getenv("SHELL", "/bin/bash").split("/")[-1]
            shell_syntax = "bash"
            python_cmd = "python3"
            project_root = self._detect_unix_project_root()
        
        # Hardware/container detection
        is_raspberry_pi = self._detect_raspberry_pi()
        is_container = self._detect_container()
        
        return EnvironmentInfo(
            os_type=os_type,
            shell=shell,
            shell_syntax=shell_syntax,
            python_cmd=python_cmd,
            is_raspberry_pi=is_raspberry_pi,
            is_container=is_container,
            project_root=project_root,
            architecture=architecture,
            python_version=python_version,
            working_directory=working_directory,
            user=user,
            home_directory=home_directory
        )
    
    def _detect_windows_project_root(self) -> Optional[str]:
        """Detect Windows project root"""
        possible_roots = [
            r"c:\dev\piw2_keyboard",
            r"c:\dev\bt-keyboard-switcher",
            os.getcwd()
        ]
        
        for root in possible_roots:
            if os.path.exists(root):
                return root
        return None
    
    def _detect_unix_project_root(self) -> Optional[str]:
        """Detect Unix project root"""
        user = os.getenv("USER", "user")
        possible_roots = [
            f"/home/{user}/piw2_keyboard",
            f"/home/{user}/bt-keyboard-switcher",
            f"/home/marty/bt-keyboard-switcher",  # Pi-specific
            os.getcwd()
        ]
        
        for root in possible_roots:
            if os.path.exists(root):
                return root
        return None
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                return "raspberry pi" in f.read().lower()
        except:
            return False
    
    def _detect_container(self) -> bool:
        """Detect if running in a container"""
        return (
            os.path.exists("/.dockerenv") or
            os.getenv("CONTAINER") is not None or
            os.getenv("DOCKER_CONTAINER") is not None
        )


class CommandGenerator:
    """Generate environment-specific commands"""
    
    @staticmethod
    def get_command_syntax(env_info: EnvironmentInfo, operation: str) -> Dict[str, str]:
        """Get command syntax for specific operation"""
        if env_info.shell_syntax == "powershell":
            return CommandGenerator._get_powershell_syntax(env_info, operation)
        else:
            return CommandGenerator._get_bash_syntax(env_info, operation)
    
    @staticmethod
    def _get_powershell_syntax(env_info: EnvironmentInfo, operation: str) -> Dict[str, str]:
        """PowerShell command patterns"""
        default_project = r"c:\dev\project"
        project_root = env_info.project_root or default_project
        
        commands = {
            "test": f"cd {project_root}; {env_info.python_cmd} -m pytest",
            "run": f"cd {project_root}; {env_info.python_cmd} -m main",
            "install": f"{env_info.python_cmd} -m pip install -r requirements.txt",
            "env_var": "$env:VARIABLE_NAME = 'value'",
            "list_dir": "Get-ChildItem",
            "chain": "cmd1; cmd2; cmd3",
            "build": f"cd {project_root}; {env_info.python_cmd} setup.py build"
        }
        
        default_example_path = r"c:\dev\project"
        example_path = env_info.project_root or default_example_path
        
        return {
            "command": commands.get(operation, f"{env_info.python_cmd} --help"),
            "shell": "PowerShell",
            "separator": ";",
            "example": f"cd {example_path}; {env_info.python_cmd} -m pytest test/"
        }
    
    @staticmethod
    def _get_bash_syntax(env_info: EnvironmentInfo, operation: str) -> Dict[str, str]:
        """Bash command patterns"""
        commands = {
            "test": f"cd {env_info.project_root or '/home/user/project'} && {env_info.python_cmd} -m pytest",
            "run": f"cd {env_info.project_root or '/home/user/project'} && {env_info.python_cmd} -m main",
            "install": f"{env_info.python_cmd} -m pip install -r requirements.txt",
            "env_var": "export VARIABLE_NAME='value'",
            "list_dir": "ls -la",
            "chain": "cmd1 && cmd2 && cmd3",
            "build": f"cd {env_info.project_root or '/home/user/project'} && {env_info.python_cmd} setup.py build"
        }
        
        # Pi-specific adjustments
        if env_info.is_raspberry_pi:
            commands["service"] = "sudo systemctl restart bt-keyboard-switcher"
            commands["logs"] = "sudo journalctl -u bt-keyboard-switcher -f"
        
        return {
            "command": commands.get(operation, f"{env_info.python_cmd} --help"),
            "shell": "Bash/Zsh",
            "separator": "&&",
            "example": f"cd {env_info.project_root or '/home/user/project'} && {env_info.python_cmd} -m pytest test/"
        }


# Global detector instance
detector = EnvironmentDetector()


@mcp.tool()
async def detect_environment() -> str:
    """Detect the current development environment and return detailed information.
    
    Returns comprehensive environment details including OS, shell, Python command,
    project paths, and hardware-specific information.
    """
    try:
        env_info = detector.detect_environment()
        
        result = {
            "environment": asdict(env_info),
            "summary": {
                "os": env_info.os_type,
                "shell": env_info.shell,
                "python_command": env_info.python_cmd,
                "project_root": env_info.project_root,
                "recommended_separator": ";" if env_info.shell_syntax == "powershell" else "&&"
            },
            "status": "success"
        }
        
        logger.info(f"Environment detected: {env_info.os_type} - {env_info.shell}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Environment detection failed: {e}")
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })


@mcp.tool()
async def get_command_syntax(operation: str) -> str:
    """Get environment-specific command syntax for common development operations.
    
    Args:
        operation: The operation to get syntax for (test, run, install, build, etc.)
    """
    try:
        env_info = detector.detect_environment()
        command_info = CommandGenerator.get_command_syntax(env_info, operation)
        
        result = {
            "operation": operation,
            "environment": {
                "os": env_info.os_type,
                "shell": env_info.shell_syntax
            },
            "command": command_info["command"],
            "shell_type": command_info["shell"],
            "command_separator": command_info["separator"],
            "example": command_info["example"],
            "status": "success"
        }
        
        logger.info(f"Generated {operation} command for {env_info.os_type}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Command syntax generation failed: {e}")
        return json.dumps({
            "error": str(e),
            "operation": operation,
            "status": "failed"
        })


@mcp.tool()
async def get_project_commands() -> str:
    """Get project-specific commands for the current development environment.
    
    Returns common commands needed for the detected project type and environment.
    """
    try:
        env_info = detector.detect_environment()
        
        # Common project commands
        commands = []
        
        if env_info.shell_syntax == "powershell":
            base_path = env_info.project_root or "c:\\dev\\project"
            commands = [
                {
                    "name": "Test",
                    "command": f"cd {base_path}; {env_info.python_cmd} -m pytest",
                    "description": "Run project tests"
                },
                {
                    "name": "Run",
                    "command": f"cd {base_path}; {env_info.python_cmd} -m main",
                    "description": "Run the main application"
                },
                {
                    "name": "Install Dependencies",
                    "command": f"cd {base_path}; {env_info.python_cmd} -m pip install -r requirements.txt",
                    "description": "Install project dependencies"
                },
                {
                    "name": "Lint",
                    "command": f"cd {base_path}; ruff check .",
                    "description": "Run code linting"
                }
            ]
        else:
            base_path = env_info.project_root or "/home/user/project"
            commands = [
                {
                    "name": "Test",
                    "command": f"cd {base_path} && {env_info.python_cmd} -m pytest",
                    "description": "Run project tests"
                },
                {
                    "name": "Run",
                    "command": f"cd {base_path} && {env_info.python_cmd} -m main",
                    "description": "Run the main application"
                },
                {
                    "name": "Install Dependencies",
                    "command": f"cd {base_path} && {env_info.python_cmd} -m pip install -r requirements.txt",
                    "description": "Install project dependencies"
                },
                {
                    "name": "Lint",
                    "command": f"cd {base_path} && ruff check .",
                    "description": "Run code linting"
                }
            ]
            
            # Add Pi-specific commands
            if env_info.is_raspberry_pi:
                commands.extend([
                    {
                        "name": "Deploy to Pi",
                        "command": "./deploy.ps1",
                        "description": "Deploy changes to Raspberry Pi"
                    },
                    {
                        "name": "Check Service",
                        "command": "sudo systemctl status bt-keyboard-switcher",
                        "description": "Check service status on Pi"
                    },
                    {
                        "name": "View Logs",
                        "command": "sudo journalctl -u bt-keyboard-switcher -f",
                        "description": "View service logs on Pi"
                    }
                ])
        
        result = {
            "environment": {
                "os": env_info.os_type,
                "shell": env_info.shell_syntax,
                "project_root": env_info.project_root
            },
            "commands": commands,
            "status": "success"
        }
        
        logger.info(f"Generated {len(commands)} project commands")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Project commands generation failed: {e}")
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })


def main():
    """Main entry point for the MCP server"""
    logger.info("Starting Dev Environment MCP Server")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
