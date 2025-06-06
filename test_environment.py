#!/usr/bin/env python3
"""
Quick test script to show environment detection functionality
"""

import sys
import os
import json

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dev_environment_mcp.mcp_server import EnvironmentDetector, CommandGenerator

def main():
    """Test the environment detection functionality"""
    print("=== Development Environment Detection ===\n")
    
    # Create detector instance
    detector = EnvironmentDetector()
    
    # Detect environment
    print("Detecting environment...")
    env_info = detector.detect_environment()
      # Display results
    print("\n=== Basic Environment Information ===")
    print(f"OS Type: {env_info.os_type}")
    print(f"Architecture: {env_info.architecture}")
    print(f"Shell: {env_info.shell} ({env_info.shell_syntax} syntax)")
    print(f"Terminal Type: {env_info.terminal_type}")
    print(f"Python Command: {env_info.python_cmd}")
    print(f"Python Version: {env_info.python_version}")
    print(f"User: {env_info.user}")
    print(f"Admin/Elevated: {env_info.is_admin_elevated}")
    print(f"Container: {env_info.is_container}")
    
    print("\n=== Directory Context ===")
    print(f"Home Directory: {env_info.home_directory}")
    print(f"Working Directory: {env_info.working_directory}")
    print(f"Project Root: {env_info.project_root}")
    print(f"Project Type: {env_info.project_type}")
    
    print("\n=== Git Information ===")
    print(f"Git Repository: {env_info.git_repository}")
    print(f"Git Branch: {env_info.git_branch}")
    
    print("\n=== Development Tools ===")
    print(f"IDE Detected: {env_info.ide_detected}")
    print(f"Package Managers: {', '.join(env_info.package_managers) if env_info.package_managers else 'None'}")
    
    print("\n=== Installed Tools ===")
    for tool, version in env_info.installed_tools.items():
        status = version if version else "Not installed"
        print(f"  {tool}: {status}")
    
    print("\n=== Available Runtimes ===")
    for runtime, version in env_info.available_runtimes.items():
        print(f"  {runtime}: {version}")
    
    print("\n=== Relevant Environment Variables ===")
    for var, value in env_info.environment_variables.items():
        # Truncate long paths for readability
        display_value = value[:60] + "..." if len(value) > 60 else value
        print(f"  {var}: {display_value}")
    
    print("\n=== Command Examples ===")
    
    # Test different operations
    operations = ["test", "run", "install", "build"]
    
    for operation in operations:
        try:
            command_info = CommandGenerator.get_command_syntax(env_info, operation)
            print(f"\n{operation.upper()} Command:")
            print(f"  Command: {command_info['command']}")
            print(f"  Shell: {command_info['shell']}")
            print(f"  Example: {command_info['example']}")
        except Exception as e:
            print(f"  Error generating {operation} command: {e}")
    
    print("\n=== JSON Output for AI Agents ===")
    # Also show as JSON for easy parsing by AI agents
    env_dict = {
        "basic_info": {
            "os_type": env_info.os_type,
            "architecture": env_info.architecture,
            "shell": env_info.shell,
            "shell_syntax": env_info.shell_syntax,
            "terminal_type": env_info.terminal_type,
            "python_cmd": env_info.python_cmd,
            "python_version": env_info.python_version,
            "user": env_info.user,
            "is_admin_elevated": env_info.is_admin_elevated,
            "is_container": env_info.is_container
        },
        "directories": {
            "home_directory": env_info.home_directory,
            "working_directory": env_info.working_directory,
            "project_root": env_info.project_root
        },
        "project_context": {
            "project_type": env_info.project_type,
            "git_repository": env_info.git_repository,
            "git_branch": env_info.git_branch
        },
        "development_tools": {
            "ide_detected": env_info.ide_detected,
            "package_managers": env_info.package_managers,
            "installed_tools": env_info.installed_tools,
            "available_runtimes": env_info.available_runtimes
        },
        "environment_variables": env_info.environment_variables
    }
    
    print(json.dumps(env_dict, indent=2))

if __name__ == "__main__":
    main()
