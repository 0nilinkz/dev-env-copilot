#!/usr/bin/env python3
"""
Quick test script to show environment detection functionality
"""

import sys
import os
import json

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dev_environment_mcp.mcp_server_clean import EnvironmentDetector, CommandGenerator

def main():
    """Test the environment detection functionality"""
    print("=== Development Environment Detection ===\n")
    
    # Create detector instance
    detector = EnvironmentDetector()
    
    # Detect environment
    print("Detecting environment...")
    env_info = detector.detect_environment()
    
    # Display results
    print("\n=== Environment Information ===")
    print(f"OS Type: {env_info.os_type}")
    print(f"Architecture: {env_info.architecture}")
    print(f"Shell: {env_info.shell}")
    print(f"Shell Syntax: {env_info.shell_syntax}")
    print(f"Python Command: {env_info.python_cmd}")
    print(f"Python Version: {env_info.python_version}")
    print(f"User: {env_info.user}")
    print(f"Home Directory: {env_info.home_directory}")
    print(f"Working Directory: {env_info.working_directory}")
    print(f"Project Root: {env_info.project_root}")
    print(f"Is Container: {env_info.is_container}")
    
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
    
    print("\n=== JSON Output ===")
    # Also show as JSON for easy parsing
    env_dict = {
        "os_type": env_info.os_type,
        "architecture": env_info.architecture,
        "shell": env_info.shell,
        "shell_syntax": env_info.shell_syntax,
        "python_cmd": env_info.python_cmd,
        "python_version": env_info.python_version,
        "user": env_info.user,
        "home_directory": env_info.home_directory,
        "working_directory": env_info.working_directory,
        "project_root": env_info.project_root,
        "is_container": env_info.is_container
    }
    
    print(json.dumps(env_dict, indent=2))

if __name__ == "__main__":
    main()
