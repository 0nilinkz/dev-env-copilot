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
import argparse
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import subprocess
import asyncio
from dataclasses import dataclass, asdict

try:
    import psutil
except ImportError:
    psutil = None

# MCP Protocol imports (these would come from the MCP SDK when available)
try:
    from mcp import Server, Tool, ToolResult
    from mcp.types import TextContent, ImageContent
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for environments without MCP SDK
    MCP_AVAILABLE = False
    
    # Mock classes for standalone operation
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
        
        def tool(self, name: str, description: str = ""):
            def decorator(func):
                self.tools[name] = func
                return func
            return decorator
    
    class ToolResult:
        def __init__(self, content: List[Union["TextContent", "ImageContent"]]):
            self.content = content
    
    class TextContent:
        def __init__(self, type: str, text: str):
            self.type = type
            self.text = text


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


@dataclass
class CommandSyntax:
    """Command syntax for different operations"""
    operation: str
    shell_command: str
    explanation: str
    example: str
    environment: str


class EnvironmentDetector:
    """Core environment detection logic"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def detect_environment(self) -> EnvironmentInfo:
        """Detect current environment with caching"""
        cache_key = "environment"
        now = self._get_timestamp()
        
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if now - cached_time < self.cache_ttl:
                return EnvironmentInfo(**cached_data)
        
        # Perform fresh detection
        env_info = self._detect_environment_fresh()
        self.cache[cache_key] = (now, asdict(env_info))
        return env_info
    
    def _detect_environment_fresh(self) -> EnvironmentInfo:
        """Fresh environment detection"""
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
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                return "raspberry pi" in f.read().lower()
        except (FileNotFoundError, PermissionError):
            return False
    
    def _detect_container(self) -> bool:
        """Detect if running in a container"""
        # Check for Docker
        if os.path.exists("/.dockerenv"):
            return True
        
        # Check for other container indicators
        try:
            with open("/proc/1/cgroup", "r") as f:
                content = f.read()
                return "docker" in content or "containerd" in content
        except (FileNotFoundError, PermissionError):
            return False
    
    def _detect_windows_project_root(self) -> Optional[str]:
        """Detect project root on Windows"""
        cwd = Path.cwd()
        
        # Common Windows dev paths
        common_roots = [
            Path("c:/dev"),
            Path("c:/projects"),
            Path("c:/code"),
            Path.home() / "Documents" / "dev",
            Path.home() / "dev",
        ]
        
        for root in common_roots:
            if cwd.is_relative_to(root):
                return str(cwd)
        
        return str(cwd)
    
    def _detect_unix_project_root(self) -> Optional[str]:
        """Detect project root on Unix systems"""
        cwd = Path.cwd()
        
        # Common Unix dev paths
        common_roots = [
            Path.home() / "dev",
            Path.home() / "projects",
            Path.home() / "code",
            Path("/home") / self._get_user() / "dev",
            Path("/opt/dev"),
        ]
        
        for root in common_roots:
            try:
                if cwd.is_relative_to(root):
                    return str(cwd)
            except ValueError:
                continue
        
        return str(cwd)
    
    def _get_user(self) -> str:
        """Get current username"""
        return os.getenv("USER", os.getenv("USERNAME", "user"))
    
    def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()


class CommandSyntaxProvider:
    """Provides correct command syntax for different environments"""
    
    def __init__(self, detector: EnvironmentDetector):
        self.detector = detector
    
    def get_command_syntax(self, operation: str, target: str = "local", 
                          format_type: str = "shell") -> CommandSyntax:
        """Get command syntax for a specific operation"""
        env = self.detector.detect_environment()
        
        # Command templates by operation and environment
        commands = self._get_command_templates()
        
        if operation not in commands:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Select command based on environment
        cmd_info = self._select_command(commands[operation], env, target)
        
        return CommandSyntax(
            operation=operation,
            shell_command=cmd_info["command"],
            explanation=cmd_info["explanation"],
            example=cmd_info.get("example", cmd_info["command"]),
            environment=f"{env.os_type}/{env.shell}"
        )
    
    def format_command(self, command_template: str, variables: Dict[str, Any]) -> str:
        """Format a command template with variables"""
        env = self.detector.detect_environment()
        
        # Add environment variables to the context
        all_vars = {
            "python_cmd": env.python_cmd,
            "shell_sep": ";" if env.shell_syntax == "powershell" else "&&",
            "project_root": env.project_root or env.working_directory,
            "home": env.home_directory,
            "user": env.user,
            **variables
        }
        
        try:
            return command_template.format(**all_vars)
        except KeyError as e:
            raise ValueError(f"Missing variable in template: {e}")
    
    def _get_command_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Get command templates for different operations"""
        return {
            "test": {
                "windows": {
                    "command": "python -m pytest test/",
                    "explanation": "Run Python tests using pytest on Windows",
                    "example": "cd c:\\dev\\project; python -m pytest test/ -v"
                },
                "linux": {
                    "command": "python3 -m pytest test/",
                    "explanation": "Run Python tests using pytest on Linux",
                    "example": "cd /home/user/project && python3 -m pytest test/ -v"
                },
                "pi": {
                    "command": "sudo python3 -m pytest test/",
                    "explanation": "Run Python tests with sudo on Raspberry Pi",
                    "example": "cd /home/marty/project && sudo python3 -m pytest test/"
                }
            },
            "build": {
                "windows": {
                    "command": "python -m build",
                    "explanation": "Build Python package on Windows",
                    "example": "cd c:\\dev\\project; python -m build --wheel"
                },
                "linux": {
                    "command": "python3 -m build",
                    "explanation": "Build Python package on Linux",
                    "example": "cd /home/user/project && python3 -m build --wheel"
                }
            },
            "install": {
                "windows": {
                    "command": "pip install -e .",
                    "explanation": "Install package in development mode on Windows",
                    "example": "cd c:\\dev\\project; pip install -e .[dev]"
                },
                "linux": {
                    "command": "pip3 install -e .",
                    "explanation": "Install package in development mode on Linux",
                    "example": "cd /home/user/project && pip3 install -e .[dev]"
                }
            },
            "deploy": {
                "windows": {
                    "command": ".\\deploy.ps1",
                    "explanation": "Run PowerShell deployment script",
                    "example": ".\\deploy.ps1 -Target production"
                },
                "linux": {
                    "command": "./deploy.sh",
                    "explanation": "Run Bash deployment script",
                    "example": "./deploy.sh --target production"
                }
            },
            "env_var": {
                "windows": {
                    "command": "$env:{name} = '{value}'",
                    "explanation": "Set environment variable in PowerShell",
                    "example": "$env:PYTHONPATH = 'c:\\dev\\project'"
                },
                "linux": {
                    "command": "export {name}='{value}'",
                    "explanation": "Set environment variable in Bash",
                    "example": "export PYTHONPATH=/home/user/project"
                }
            }
        }
    
    def _select_command(self, cmd_templates: Dict[str, Dict[str, str]], 
                       env: EnvironmentInfo, target: str) -> Dict[str, str]:
        """Select appropriate command template based on environment"""
        # Priority order for command selection
        if target == "pi" or env.is_raspberry_pi:
            if "pi" in cmd_templates:
                return cmd_templates["pi"]
        
        if env.os_type == "windows":
            return cmd_templates.get("windows", cmd_templates.get("linux", {}))
        elif env.os_type in ["linux", "darwin"]:
            return cmd_templates.get("linux", cmd_templates.get("windows", {}))
        
        # Fallback to first available
        return next(iter(cmd_templates.values()), {})


class EnvironmentMCPServer:
    """Main MCP server implementation"""
    
    def __init__(self, name: str = "dev-environment-mcp"):
        self.server = Server(name)
        self.detector = EnvironmentDetector()
        self.command_provider = CommandSyntaxProvider(self.detector)
        self.logger = self._setup_logging()
        
        # Register tools
        self._register_tools()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("dev-environment-mcp")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.server.tool("detect_environment", "Detect current development environment")
        async def detect_environment(format_type: str = "json") -> ToolResult:
            """Detect and return current environment information"""
            try:
                env = self.detector.detect_environment()
                
                if format_type == "summary":
                    summary = self._format_environment_summary(env)
                    return ToolResult([TextContent(type="text", text=summary)])
                elif format_type == "copilot":
                    copilot_context = self._format_copilot_context(env)
                    return ToolResult([TextContent(type="text", text=json.dumps(copilot_context, indent=2))])
                else:  # json
                    return ToolResult([TextContent(type="text", text=json.dumps(asdict(env), indent=2))])
            except Exception as e:
                self.logger.error(f"Environment detection failed: {e}")
                return ToolResult([TextContent(type="text", text=f"Error: {e}")])
        
        @self.server.tool("get_command_syntax", "Get correct command syntax for current environment")
        async def get_command_syntax(operation: str, target: str = "local", 
                                   format_type: str = "shell") -> ToolResult:
            """Get command syntax for a specific operation"""
            try:
                cmd_syntax = self.command_provider.get_command_syntax(operation, target, format_type)
                
                if format_type == "explanation":
                    text = f"Operation: {cmd_syntax.operation}\nCommand: {cmd_syntax.shell_command}\nExplanation: {cmd_syntax.explanation}\nExample: {cmd_syntax.example}\nEnvironment: {cmd_syntax.environment}"
                elif format_type == "examples":
                    text = json.dumps({
                        "operation": cmd_syntax.operation,
                        "command": cmd_syntax.shell_command,
                        "example": cmd_syntax.example,
                        "environment": cmd_syntax.environment
                    }, indent=2)
                else:  # shell
                    text = cmd_syntax.shell_command
                
                return ToolResult([TextContent(type="text", text=text)])
            except Exception as e:
                self.logger.error(f"Command syntax generation failed: {e}")
                return ToolResult([TextContent(type="text", text=f"Error: {e}")])
        
        @self.server.tool("format_command", "Format a command template for current environment")
        async def format_command(command_template: str, variables: Dict[str, Any] = None) -> ToolResult:
            """Format a command template with variables"""
            try:
                if variables is None:
                    variables = {}
                
                formatted_cmd = self.command_provider.format_command(command_template, variables)
                return ToolResult([TextContent(type="text", text=formatted_cmd)])
            except Exception as e:
                self.logger.error(f"Command formatting failed: {e}")
                return ToolResult([TextContent(type="text", text=f"Error: {e}")])
        
        @self.server.tool("get_project_context", "Analyze current project structure")
        async def get_project_context(include_files: bool = False, 
                                    analyze_dependencies: bool = True) -> ToolResult:
            """Get context about the current project"""
            try:
                context = self._analyze_project_context(include_files, analyze_dependencies)
                return ToolResult([TextContent(type="text", text=json.dumps(context, indent=2))])
            except Exception as e:
                self.logger.error(f"Project analysis failed: {e}")
                return ToolResult([TextContent(type="text", text=f"Error: {e}")])
    
    def _format_environment_summary(self, env: EnvironmentInfo) -> str:
        """Format environment info as a human-readable summary"""
        summary = f"""Environment Summary:
- OS: {env.os_type.title()} ({env.architecture})
- Shell: {env.shell} ({env.shell_syntax} syntax)
- Python: {env.python_cmd} (v{env.python_version})
- User: {env.user}
- Directory: {env.working_directory}
- Project Root: {env.project_root or 'Not detected'}"""
        
        if env.is_raspberry_pi:
            summary += "\n- Hardware: Raspberry Pi detected"
        if env.is_container:
            summary += "\n- Container: Running in container"
        
        return summary
    
    def _format_copilot_context(self, env: EnvironmentInfo) -> Dict[str, Any]:
        """Format environment info for Copilot consumption"""
        return {
            "environment": {
                "type": "development",
                "os": env.os_type,
                "shell": env.shell,
                "syntax": env.shell_syntax,
                "is_pi": env.is_raspberry_pi,
                "is_container": env.is_container
            },
            "commands": {
                "python": env.python_cmd,
                "separator": ";" if env.shell_syntax == "powershell" else "&&",
                "env_var_syntax": "$env:VAR = 'value'" if env.shell_syntax == "powershell" else "export VAR='value'"
            },
            "paths": {
                "project_root": env.project_root,
                "working_dir": env.working_directory,
                "home": env.home_directory
            },
            "examples": {
                "test": f"cd {env.project_root or env.working_directory}{';' if env.shell_syntax == 'powershell' else ' &&'} {env.python_cmd} -m pytest",
                "install": f"{env.python_cmd.replace('python', 'pip')} install -e .",
                "build": f"{env.python_cmd} -m build",
            }
        }
    
    def _analyze_project_context(self, include_files: bool, analyze_dependencies: bool) -> Dict[str, Any]:
        """Analyze current project structure and dependencies"""
        context = {
            "project_type": "unknown",
            "languages": [],
            "frameworks": [],
            "tools": []
        }
        
        cwd = Path.cwd()
        
        # Detect project type from common files
        project_files = {
            "package.json": "node.js",
            "pyproject.toml": "python",
            "setup.py": "python",
            "requirements.txt": "python",
            "Cargo.toml": "rust",
            "go.mod": "go",
            "pom.xml": "java",
            "build.gradle": "java",
            "Dockerfile": "docker"
        }
        
        found_files = []
        for file, lang in project_files.items():
            if (cwd / file).exists():
                found_files.append(file)
                if lang not in context["languages"]:
                    context["languages"].append(lang)
        
        if found_files:
            context["project_type"] = "multi-language" if len(set(project_files[f] for f in found_files)) > 1 else project_files[found_files[0]]
        
        # Analyze dependencies if requested
        if analyze_dependencies:
            context["dependencies"] = self._analyze_dependencies(cwd)
        
        # Include file listing if requested
        if include_files:
            context["files"] = self._get_file_listing(cwd)
        
        return context
    
    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {}
        
        # Python dependencies
        if (project_path / "requirements.txt").exists():
            try:
                with open(project_path / "requirements.txt") as f:
                    deps["python_requirements"] = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            except Exception:
                pass
        
        if (project_path / "pyproject.toml").exists():
            try:
                import toml
                with open(project_path / "pyproject.toml") as f:
                    data = toml.load(f)
                    if "project" in data and "dependencies" in data["project"]:
                        deps["python_dependencies"] = data["project"]["dependencies"]
            except Exception:
                pass
        
        # Node.js dependencies
        if (project_path / "package.json").exists():
            try:
                with open(project_path / "package.json") as f:
                    data = json.load(f)
                    deps["node_dependencies"] = data.get("dependencies", {})
                    deps["node_dev_dependencies"] = data.get("devDependencies", {})
            except Exception:
                pass
        
        return deps
    
    def _get_file_listing(self, project_path: Path, max_files: int = 50) -> List[str]:
        """Get a listing of project files"""
        files = []
        try:
            for item in project_path.rglob("*"):
                if len(files) >= max_files:
                    break
                if item.is_file() and not any(part.startswith(".") for part in item.parts):
                    files.append(str(item.relative_to(project_path)))
        except Exception:
            pass
        
        return sorted(files)
    
    async def run_stdio(self):
        """Run server using stdio transport"""
        if not MCP_AVAILABLE:
            self.logger.error("MCP SDK not available. Install with: pip install mcp")
            return
        
        # This would integrate with the actual MCP transport layer
        self.logger.info("Starting MCP server with stdio transport")
        # await self.server.run_stdio()
    
    async def run_http(self, host: str = "localhost", port: int = 8080):
        """Run server using HTTP transport"""
        if not MCP_AVAILABLE:
            self.logger.error("MCP SDK not available. Install with: pip install mcp")
            return
        
        self.logger.info(f"Starting MCP server with HTTP transport on {host}:{port}")
        # await self.server.run_http(host, port)


def standalone_detect_environment(format_type: str = "json") -> str:
    """Standalone environment detection function"""
    detector = EnvironmentDetector()
    env = detector.detect_environment()
    
    if format_type == "summary":
        return f"""Environment Summary:
- OS: {env.os_type.title()} ({env.architecture})
- Shell: {env.shell} ({env.shell_syntax} syntax)
- Python: {env.python_cmd} (v{env.python_version})
- User: {env.user}
- Directory: {env.working_directory}
- Project Root: {env.project_root or 'Not detected'}
{"- Hardware: Raspberry Pi detected" if env.is_raspberry_pi else ""}
{"- Container: Running in container" if env.is_container else ""}"""
    elif format_type == "copilot":
        copilot_context = {
            "environment": {
                "type": "development",
                "os": env.os_type,
                "shell": env.shell,
                "syntax": env.shell_syntax,
                "is_pi": env.is_raspberry_pi,
                "is_container": env.is_container
            },
            "commands": {
                "python": env.python_cmd,
                "separator": ";" if env.shell_syntax == "powershell" else "&&",
                "env_var_syntax": "$env:VAR = 'value'" if env.shell_syntax == "powershell" else "export VAR='value'"
            },
            "paths": {
                "project_root": env.project_root,
                "working_dir": env.working_directory,
                "home": env.home_directory
            },
            "examples": {
                "test": f"cd {env.project_root or env.working_directory}{';' if env.shell_syntax == 'powershell' else ' &&'} {env.python_cmd} -m pytest",
                "install": f"{env.python_cmd.replace('python', 'pip')} install -e .",
                "build": f"{env.python_cmd} -m build",
            }
        }
        return json.dumps(copilot_context, indent=2)
    else:  # json
        return json.dumps(asdict(env), indent=2)


def standalone_get_command_syntax(operation: str, target: str = "local", format_type: str = "shell") -> str:
    """Standalone command syntax generation"""
    detector = EnvironmentDetector()
    provider = CommandSyntaxProvider(detector)
    
    try:
        cmd_syntax = provider.get_command_syntax(operation, target, format_type)
        
        if format_type == "explanation":
            return f"Operation: {cmd_syntax.operation}\nCommand: {cmd_syntax.shell_command}\nExplanation: {cmd_syntax.explanation}\nExample: {cmd_syntax.example}\nEnvironment: {cmd_syntax.environment}"
        elif format_type == "examples":
            return json.dumps({
                "operation": cmd_syntax.operation,
                "command": cmd_syntax.shell_command,
                "example": cmd_syntax.example,
                "environment": cmd_syntax.environment
            }, indent=2)
        else:  # shell
            return cmd_syntax.shell_command
    except ValueError as e:
        return f"Error: {e}"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Development Environment MCP Server")
    parser.add_argument("--version", action="version", version="1.0.0")
    parser.add_argument("--mcp-mode", action="store_true", help="Run as MCP server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio", help="Transport method for MCP mode")
    parser.add_argument("--host", default="localhost", help="Host for HTTP transport")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP transport")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR"], default="INFO", help="Logging level")
    
    # Standalone commands
    subparsers = parser.add_subparsers(dest="command", help="Standalone commands")
    
    # Detect environment command
    detect_parser = subparsers.add_parser("detect-environment", help="Detect current environment")
    detect_parser.add_argument("--format", choices=["json", "summary", "copilot"], default="json", help="Output format")
    
    # Get command syntax
    syntax_parser = subparsers.add_parser("get-command-syntax", help="Get command syntax")
    syntax_parser.add_argument("--operation", required=True, help="Operation type (test, build, deploy, install)")
    syntax_parser.add_argument("--target", default="local", help="Target environment")
    syntax_parser.add_argument("--format", choices=["shell", "explanation", "examples"], default="shell", help="Output format")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    if args.mcp_mode:
        # Run as MCP server
        server = EnvironmentMCPServer()
        if args.transport == "stdio":
            asyncio.run(server.run_stdio())
        else:
            asyncio.run(server.run_http(args.host, args.port))
    elif args.command == "detect-environment":
        # Standalone environment detection
        result = standalone_detect_environment(args.format)
        print(result)
    elif args.command == "get-command-syntax":
        # Standalone command syntax
        result = standalone_get_command_syntax(args.operation, args.target, args.format)
        print(result)
    else:
        # No command specified, run environment detection by default
        result = standalone_detect_environment("summary")
        print(result)


if __name__ == "__main__":
    main()
